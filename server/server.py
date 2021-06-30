import asyncio
from asyncio.exceptions import TimeoutError
import logging
import argparse

logging.basicConfig(
    filename="server_log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


writers_list = []


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", default="localhost")
    return parser.parse_args()


async def handle_connection(reader, writer):
    add_writer(writer)
    addr_client = writer.get_extra_info("peername")
    join_message = f"[SERVER] {addr_client} is connected"
    lost_connection_message = f"Connection lost with {addr_client}"
    await broadcast(join_message)
    while True:
        try:
            await handle_message(reader, addr_client)
            connection = await check_connection(reader)
            if connection is False:
                del_writer(writer)
                await broadcast(lost_connection_message)
                break
        except ConnectionResetError:
            del_writer(writer)
            await broadcast(lost_connection_message)
            break
    writer.close()


async def handle_message(reader, addr_client):
    message = await read_message(reader)
    message = write_message(addr_client, message)
    await broadcast(message)


async def read_message(reader):
    data = await reader.read(100)
    message = data.decode()
    return message


async def check_connection(reader):
    try:
        try:
            await asyncio.wait_for(reader.readline(), timeout=0.1)
            return False
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            return False
    except TimeoutError:
        return True


def write_message(addr, message):
    message = f"[{addr}] {message}"
    return message


async def broadcast(message):
    # SENDING MESSAGE TO ALL CLIENTS
    logging.info(message)
    print(message)
    for client in writers_list:
        client.write(message.encode())
        await client.drain()


def add_writer(writer):
    writers_list.append(writer)


def del_writer(writer):
    writers_list.remove(writer)


async def main():
    # OPEN SERVER
    try:
        args = parse_args()
        server = await asyncio.start_server(handle_connection, args.address, 5051)
        addr_servidor = server.sockets[0].getsockname()
        logging.info(f"[STARTIG] Server is running in {addr_servidor}")
    except Exception as error:
        print(error)
        logging.info("[SERVER] failed to creating server")
    else:
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
