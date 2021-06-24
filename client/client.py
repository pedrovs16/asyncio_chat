import asyncio
from asyncio.tasks import gather
import aioconsole
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument("-r", "--read", action="store_true", help="Client only listen")
    return parser.parse_args()


async def read_task(reader, writer):
    while True:
        try:
            await read_message(reader)
            check_connection_message = " "
            writer.write(check_connection_message.encode())
            await writer.drain()
        except Exception as error:
            print(error)
            break


async def read_message(reader):
    read_message = await reader.read(100)
    print(f"{read_message.decode()}")


async def write_task(writer):
    message = ""
    try:
        while message.upper() != "EXIT":
            message = await handle_message(writer)
        writer.close()
    except Exception as error:
        print(error)
        writer.close()


async def handle_message(writer):
    message = await write_input()
    await write_message(message, writer)
    return message


async def write_message(message, writer):
    writer.write(message.encode())
    await writer.drain()


async def write_input():
    return await aioconsole.ainput("")


async def main():
    try:
        reader, writer = await asyncio.open_connection("localhost", 5051)
        print(f"Joined to the server")
        print('To disconnect type "EXIT"')
    except Exception:
        print("Server not found")
    else:
        if args.read:
            await read_task(reader, writer)
        else:
            await gather(read_task(reader, writer), write_task(writer))
        # if not args.read:
        #    asyncio.create_task(write_message(writer))
        # asyncio.create_task(read_message(reader, writer))


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main())
