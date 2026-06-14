import argparse
import socket
import ssl

def chatterbox_cliparser():
    parser = argparse.ArgumentParser(description='Chatterbox Server is a simple network chat server)')
    parser.add_argument('host', type=str, nargs="?", default="localhost", help='Host address to listen on (default: localhost)')
    parser.add_argument('--port', type=int, default=2428, help='Port number to listen on (default: 12345)')

    enable_ssl = parser.add_argument_group("ssl", "Enable SSL/TLS for secure communication")
    enable_ssl.add_argument('--cert', type=str, help="Path to the SSL certificate file (optional)")
    enable_ssl.add_argument('--key', type=str, help="Path to the SSL key file (optional)")

    args = parser.parse_args()

    if any(vars(args)[k] for k in ["cert", "key"]) and \
    not all(vars(args)[k] for k in ["cert", "key"]):
        parser.error("--cert and --key must be provided together")

    return args

def chatterbox_setup(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    print(f"Chatterbox Server is listening on {host}:{port}")

    return sock 

def chatterbox_setup_ssl(host, port, cert, key):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert, keyfile=key)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    print(f"Chatterbox Server is listening on {host}:{port} (ssl enabled)")

    sock = context.wrap_socket(sock, server_side=True)

    return sock

def chatterbox_serve(sock):
    while True:
        client_socket, client_address = sock.accept()
        print(f"Connection established with {client_address}")

        client_socket.sendall(b"Welcome to Chatterbox Server!\n")
        while True: 
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Message from {client_address[0]}: {data.decode('utf-8')}")
            client_socket.sendall(data) 
        
        client_socket.close()

if __name__ == '__main__':
    args = chatterbox_cliparser()

    if args.cert:
        sock = chatterbox_setup_ssl(args.host, args.port, args.cert, args.key)
    else:
        sock = chatterbox_setup(args.host, args.port)

    try:
        chatterbox_serve(sock)
    except KeyboardInterrupt:
        print("\nChatterbox server is exiting...")
        sock.close()

    sock.close()