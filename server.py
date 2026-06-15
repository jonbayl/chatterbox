""" Chatterbox Chat Server

This module implements a simple chat server that allows
multiple clients to connect and send messages which are 
then broadcast to all other users.
"""

import argparse
import socket
import ssl

def chatterbox_cliparser():
    """Handle command line parsing for the server.

    Configure arguments for the host address and port 
    on which the server will listen, and optional SSL 
    configuration (cert and key) which can be used to 
    provide secure communication.

    Returns:
        argparse.Namespace: Parsed command line arguments.
        May contain host, port, and ssl certificate path.
    """

    parser = argparse.ArgumentParser(description='Chatterbox Server is a'
        ' simple network chat server)'
    )
    parser.add_argument('host', type=str, nargs="?",
        default="localhost", help='Host address to listen on'
        ' (default: localhost)'
    )
    parser.add_argument('--port', type=int, default=2428,
        help='Port number to listen on (default: 12345)'
    )

    enable_ssl = parser.add_argument_group("ssl",
        "Enable SSL/TLS for secure communication"
    )
    enable_ssl.add_argument('--cert', type=str,
        help="Path to the SSL certificate file (optional)"
    )
    enable_ssl.add_argument('--key', type=str,
        help="Path to the SSL key file (optional)"
    )

    args = parser.parse_args()

    if any(vars(args)[k] for k in ["cert", "key"]) and \
    not all(vars(args)[k] for k in ["cert", "key"]):
        parser.error("--cert and --key must be provided together")

    return args

def chatterbox_setup(host, port):
    """ Setup an insecure TCP socket

    Configures the server to set up a raw, unencrypted TCP socket
    on the specified host and port.

    Args:
        host (str): The hostname or IP address to bind the server to.
        port (int): The port number to listen on.

    Returns:
        socket.socket: A configured TCP socket ready to accept connections.
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    print(f"Chatterbox Server is listening on {host}:{port}")

    return sock

def chatterbox_setup_ssl(host, port, cert, key):
    """ Setup an secure TCP socket

    Configures the server to set up an encrypted TCP socket
    on the specified host and port.

    Args:
        host (str): The hostname or IP address to bind the server to.
        port (int): The port number to listen on.
        cert (str): Path to the SSL certificate file.
        key (str): Path to the SSL key file.

    Returns:
        socket.socket: A configured TCP socket ready to accept connections.
    """

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert, keyfile=key)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    print(f"Chatterbox Server is listening on {host}:{port} (ssl enabled)")

    sock = context.wrap_socket(sock, server_side=True)

    return sock

def chatterbox_serve(sock):
    """ Start the server to accept incoming connections.

    Continuously listens for incoming client connections and
    handles them in a loop. For each connection, it sends a welcome
    message and echoes back any received messages.

    Args:
        sock (socket.socket): The server socket to accept connections on.
    """

    while True:
        client_socket, client_address = sock.accept()
        print(f"Connection established with {client_address}")

        client_socket.sendall(b"Welcome to Chatterbox Server!\n")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Message from {client_address[0]}: "
                f"{data.decode('utf-8')}"
            )
            client_socket.sendall(data)

        client_socket.close()

def main():
    args = chatterbox_cliparser()

    if args.cert:
        sock = chatterbox_setup_ssl(args.host, args.port,
            args.cert, args.key
        )
    else:
        sock = chatterbox_setup(args.host, args.port)

    try:
        chatterbox_serve(sock)
    except KeyboardInterrupt:
        print("\nChatterbox server is exiting...")
        sock.close()

    sock.close()

if __name__ == '__main__':
    main()
