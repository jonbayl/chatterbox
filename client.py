import argparse
import socket
import ssl
import asyncio

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import FormattedText

def chatterbox_client_cliparser():
    parser = argparse.ArgumentParser(description='Chatterbox Client is a simple network chat client)')
    parser.add_argument('host', type=str, nargs="?", default="localhost", help='Host address to connect to (default: localhost)')
    parser.add_argument('--port', type=int, default=2428, help='Port number to connect to (default: 2428)')
    parser.add_argument('--ssl', type=str, help='Enable SSL/TLS for secure communication (provide "trusted CA cert" to enable SSL)')
    args = parser.parse_args()

    return args

async def chatterbox_client_insecure(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    return reader, writer

async def chatterbox_client_secure(host, port, cert):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cert)

    reader, writer = await asyncio.open_connection(host, port, ssl=context)
    
    return reader, writer

async def chatterbox_receive(reader, writer):
    loop = asyncio.get_event_loop()
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                print_formatted_text("Server closed the connection.")
                break
            print_formatted_text(FormattedText([
                ('ansicyan', f"Received: {data.decode('utf-8')}")
            ]))
    except KeyboardInterrupt:
        print_formatted_text("Server closed the connection.")
    finally:
        writer.close()
        await writer.wait_closed()

async def chatterbox_send(reader, writer):
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
    if args.ssl:
        reader, writer = await chatterbox_client_secure(args.host, args.port, args.ssl)
    else:
        reader, writer = await chatterbox_client_insecure(args.host, args.port)

    with patch_stdout():
        await asyncio.gather(
            chatterbox_receive(reader, writer),
            chatterbox_send(reader, writer)
        )

if __name__ == "__main__":
    args = chatterbox_client_cliparser()
    asyncio.run(main())
    