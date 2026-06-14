import argparse
import socket
import asyncio

def chatterbox_client_cliparser():
    parser = argparse.ArgumentParser(description='Chatterbox Client is a simple network chat client)')
    parser.add_argument('host', type=str, nargs="?", default="localhost", help='Host address to connect to (default: localhost)')
    parser.add_argument('--port', type=int, default=2428, help='Port number to connect to (default: 2428)')
    parser.add_argument('--ssl', type=str, help='Enable SSL/TLS for secure communication (provide "trusted CA cert" to enable SSL)')
    args = parser.parse_args()

    return args

def chatterbox_client_insecure(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.setblocking(False)
    return sock

def chatterbox_client_secure(host, port, cert):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cert)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = context.wrap_socket(sock, server_hostname=host)
    sock.connect((host, port))
    sock.setblocking(False)
    
    return sock

async def chatterbox_receive(sock):
    loop = asyncio.get_event_loop()
    try:
        while True:
            data = await loop.sock_recv(sock, 1024)
            if not data:
                print("Server closed the connection.")
                break
            print(f"\rReceived: {data.decode('utf-8')}")
    except KeyboardInterrupt:
        print("\nExiting chat...")
    finally:
        sock.close()

async def chatterbox_send(sock):
    loop = asyncio.get_event_loop()
    try:
        while True:
            message = await loop.run_in_executor(None, input, "Your message > ")
            if message.lower() == 'exit':
                print("Exiting chat...")
                break
            await loop.sock_sendall(sock, message.encode('utf-8'))
    except KeyboardInterrupt:
        print("\nExiting chat...")
    finally:
        sock.close()

async def main():
    await asyncio.gather(
        chatterbox_receive(sock),
        chatterbox_send(sock)
    )

if __name__ == "__main__":
    args = chatterbox_client_cliparser()

    if args.ssl:
        sock = chatterbox_client_secure(args.host, args.port, args.ssl)
    else:
        sock = chatterbox_client_insecure(args.host, args.port)
    
    asyncio.run(main())
    