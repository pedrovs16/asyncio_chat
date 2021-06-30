import asyncio
from asyncio.tasks import gather
import sys
import aioconsole
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--read", action="store_true", help="Client only listen")
    return parser.parse_args()


async def read_task(reader):
    while True:
        try:
            message = await read_message(reader)
            print(f"{message.decode()}")
            if len(message) == 0:
                sys.exit()
        except Exception:
            break


async def read_message(reader):
    message = await reader.read(100)
    return message


async def write_task(writer):
    while True:
        try:
            message = await write_input()
            await send_message(message, writer)
            if message.upper() == "EXIT":
                writer.close()
                break
        except Exception:
            writer.close()
            break
    sys.exit()


async def send_message(message, writer):
    writer.write(message.encode())
    await writer.drain()


async def write_input():
    return await aioconsole.ainput("")


async def main():
    try:
        reader, writer = await asyncio.open_connection("localhost", 5051)
        print(f"Joined to the server")
        print('To disconnect type "EXIT"')
    except OSError:
        print("Server not found")
    else:
        if not args.read:
            asyncio.create_task(write_task(writer))
        asyncio.create_task(read_task(reader))


if __name__ == "__main__":
    args = parse_args()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
