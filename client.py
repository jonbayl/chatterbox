"""Acts as a client for the Chatterbox Chat Server.

This module handles communication with a Chatterbox server,
allowing users to send and receive messages in real-time. It 
supports both secure (SSL/TLS) and insecure connections, 
depending on the user's preference.
"""

import argparse
import ssl
import asyncio

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import FormattedText

def chatterbox_client_cliparser():
    """Handle command line parsing for the client.

    Configure arguments for the host address, port,
    and SSL configuration required to connect to the
    chat server.

    Returns:
        argparse.Namespace: Parsed command line arguments.
        May contain host, port, and ssl certificate path.
    """

    parser = argparse.ArgumentParser(
        description='Chatterbox Client is a simple network chat client)'
        )
    parser.add_argument('host', type=str, nargs="?", default="localhost",
        help='Host address to connect to (default: localhost)'
    )
    parser.add_argument('--port', type=int, default=2428,
        help='Port number to connect to (default: 2428)'
    )
    parser.add_argument('--ssl', type=str,
        help='Enable SSL/TLS for secure communication (provide'
        ' "trusted CA cert" to enable SSL)'
    )
    args = parser.parse_args()

    return args

async def chatterbox_client_insecure(host, port):
    """Establish an insecure connection to the server.

    Sets up a raw TCP connection to the specified host and
    port, without encryption. 

    Args:
        host (str): The server's hostname or IP address.
        port (int): The server's port number.

    Returns:
        tuple: A tuple containing the reader and writer streams 
        for the connection:
            - reader: asyncio.StreamReader.
            - writer: asyncio.StreamWriter.
    """

    reader, writer = await asyncio.open_connection(host, port)
    return reader, writer

async def chatterbox_client_secure(host, port, cert):
    """Establish an secure connection to the server.

    Sets up a TCP connection to the specified host and
    port, with SSL/TLS encryption.

    Args:
        host (str): The server's hostname or IP address.
        port (int): The server's port number.
        cert (str): Path to the SSL certificate file for
        certificate verification.

    Returns:
        tuple: A tuple containing the reader and writer streams 
        for the connection:
            - reader: asyncio.StreamReader.
            - writer: asyncio.StreamWriter.
    """

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cert)

    reader, writer = await asyncio.open_connection(host, port,
    ssl=context)

    return reader, writer

async def chatterbox_receive(reader, writer):
    """ Receive messages from the server.

    Continuously listens for incoming messages from the server
    and displays them within the terminal. 

    Args:
        reader (asyncio.StreamReader): The reader for the connection.
        writer (asyncio.StreamWriter): The writer for the connection.
    """

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                print_formatted_text("Server closed the connection.")
                break
            print_formatted_text(FormattedText([
                ('ansicyan', f"{data.decode('utf-8')}")
            ]))
    except KeyboardInterrupt:
        print_formatted_text("Server closed the connection.")
    finally:
        writer.close()
        await writer.wait_closed()

async def chatterbox_send(writer):
    """ Send messages to the server.

    Allows the user to input messages which are then sent to the server.

    Args:
        writer (asyncio.StreamWriter): The writer for the connection.
    """

    session = PromptSession()
    try:
        while True:
            message = await session.prompt_async("Your message > ")
            session.app.output.write_raw("\033[1A\033[2K")
            session.app.output.flush()
            if message.lower() == 'exit':
                print_formatted_text("Exiting chat...")
                break
            writer.write(message.encode('utf-8'))
            await writer.drain()
    except KeyboardInterrupt:
        print_formatted_text("Exiting chat...")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    """Execute the primary lifecycle of the Chatterbox client."""

    args = chatterbox_client_cliparser()

    if args.ssl:
        reader, writer = await chatterbox_client_secure(args.host,
            args.port, args.ssl
        )
    else:
        reader, writer = await chatterbox_client_insecure(args.host,
            args.port
        )

    with patch_stdout():
        await asyncio.gather(
            chatterbox_receive(reader, writer),
            chatterbox_send(writer)
        )

if __name__ == "__main__":
    asyncio.run(main())
