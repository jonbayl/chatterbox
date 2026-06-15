""" Chatterbox Chat Server

This module implements a simple chat server that allows
multiple clients to connect and send messages which are 
then broadcast to all other users.
"""

import argparse
import ssl
import asyncio

CONNECTED_CLIENTS = set()

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

async def chatterbox_broadcast(message, sender):
    """Broadcast a received message to all other users

    Takes a raw byte stream read from the reader and broadcasts
    it to all connected clients which are not the original
    sender.

    Args:
        message (bytes): raw message data in binary
        sender (asyncio.StreamWriter): The writer for the connection.
    """
    message = message.decode("utf-8")
    message = sender+": "+message
    message = message.encode("utf-8")

    for client in list(CONNECTED_CLIENTS):
        try:
            client.write(message)
            await client.drain()
        except ConnectionResetError:
            CONNECTED_CLIENTS.discard(client)

async def chatterbox_handle(reader, writer):
    """Handles a connection received by the chat server.

    For each connection received, unpacks key metadata, 
    broadcasts a welcome message and then handles reading 
    data received and calling the broadcast function as 
    needed.

    Args:
        reader (asyncio.StreamReader): The reader for the connection.
        writer (asyncio.StreamWriter): The writer for the connection.
    """

    client_ip = writer.get_extra_info('peername')
    print(f"Accepted connection from: {client_ip[0]}")

    CONNECTED_CLIENTS.add(writer)
    writer.write(b"Welcome to Chatterbox Server!\n")
    await writer.drain()

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                 break
            print(f"Message from {client_ip[0]}: "
                f"{data.decode('utf-8').strip()}"
            )
            await chatterbox_broadcast(data, sender=client_ip[0])
    except asyncio.IncompleteReadError:
        pass
    finally:
        CONNECTED_CLIENTS.discard(writer)
        writer.close()
        await writer.wait_closed()
        print(f"{client_ip[0]}: disconnected.")

async def chatterbox_listen(host, port, cert=None, key=None):
    """ Setup a TCP socket to listen for incoming connections.

    Configures the server to set up an encrypted TCP socket
    on the specified host and port, if a cert and key are
    provided. Otherwise, it sets up a raw, unencrypted TCP socket.

    Args:
        host (str): The hostname or IP address to bind the server to.
        port (int): The port number to listen on.
        cert (str): Path to the SSL certificate file.
        key (str): Path to the SSL key file.

    Raises:
        ValueError: If only one of cert or key is provided.
    """

    if cert and key:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert, keyfile=key)

        print(f"Chatterbox Server is listening on {host}:{port} "
            "(ssl enabled)"
        )

        server = await asyncio.start_server(chatterbox_handle, host, port,
            ssl=context
        )
        async with server:
            await server.serve_forever()
    elif cert or key:
        raise ValueError("SSL certificate provided without a key.")
    else:
       server = await asyncio.start_server(chatterbox_handle, host, port)
       async with server:
        await server.serve_forever()

def main():
    """Main entry point for the Chatterbox server."""

    args = chatterbox_cliparser()

    try:
        asyncio.run(chatterbox_listen(args.host, args.port,
            args.cert, args.key
        ))
    except KeyboardInterrupt:
        print("\nChatterbox server is exiting...")

if __name__ == '__main__':
    main()
