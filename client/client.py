import asyncio
from asyncio.tasks import gather
import socket
import aioconsole
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--test', action='store_true')
parser.add_argument(
    '-r', '--read', action='store_true', help='Client only listen')
args = parser.parse_args()


async def read_message(reader, writer):
    while True:
        try:
            readed_message = await reader.read(100)
            print(f'{readed_message.decode()}')
            check_connection_message = ' '
            writer.write(check_connection_message.encode())
            await writer.drain()
        except Exception as error:
            print(error)
            break


async def write_message(writer):
    writed_message = ""
    try:
        while writed_message.upper() != 'EXIT':
            writed_message = await aioconsole.ainput('')
            writer.write(writed_message.encode())
            await writer.drain()
        writer.close()
    except Exception as error:
        print(error)
        writer.close()


def ip_selector():
    # TEST MODE OR NOT
    if args.test:
        IP = socket.gethostbyname(socket.gethostname())
        PORT = 5051
    else:
        IP = input(
            'Choose the IP server (type "my" if the client use your own IP): ')
        if IP.upper() == 'MY':
            IP = socket.gethostbyname(socket.gethostname())
        PORT = 5051
    return IP, PORT


async def main():
    IP, PORT = ip_selector()
    try:
        reader, writer = await asyncio.open_connection(
            IP, PORT)
        addr_client = writer.get_extra_info('peername')
        print(f'Joined to the server {addr_client}')
        print('To disconnect type "EXIT"')
    except Exception:
        print('Server not found')
    else:
        if args.read:
            await read_message(reader, writer)
        else:
            await gather(read_message(reader, writer), write_message(
                writer))


if __name__ == '__main__':
    asyncio.run(main())
