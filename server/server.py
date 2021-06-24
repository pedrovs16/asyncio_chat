import asyncio
import socket
from asyncio.exceptions import TimeoutError
import logging
import argparse

logging.basicConfig(
    filename="server_log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", action="store_true")
args = parser.parse_args()

writers_list = []


async def broadcast(addr_client, message, writer):
    # SENDING MESSAGE TO ALL CLIENTS
    logging.info(f"[{addr_client}] {message}")
    print(f"[{addr_client}] {message}")
    for w in writers_list:
        w.write(f"[{addr_client}] {message}".encode())
        await writer.drain()


async def new_client(writer):
    # FIRST STEPS WHEN A CLIENT JOIN THE SERVER
    writers_list.append(writer)
    addr_client = writer.get_extra_info("peername")
    join_message = f"{addr_client} is connected"
    await broadcast("SERVER", join_message, writer)
    return addr_client


async def read_message(reader):
    # READ MESSAGE FROM CLIENT
    data = await reader.read(100)
    client_message = data.decode()
    check_spacebar = len(client_message.split())
    return client_message, check_spacebar


async def check_connection(reader):
    # CHECK IF THE CLIENT STILL ARE IN THE SERVER
    try:
        try:
            await asyncio.wait_for(reader.readline(), timeout=0.1)
            return False
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            return False
    except TimeoutError:
        return True


async def handle(reader, writer):
    addr_client = await new_client(writer)
    lost_connection_message = f" Connection lost with {addr_client}"
    only_space = 0
    while True:
        try:
            client_message, check_spacebar = await read_message(reader)
            connection = await check_connection(reader)
            if connection is False:
                writers_list.remove(writer)
                await broadcast("SERVER", lost_connection_message, writer)
                break
            if check_spacebar != only_space:
                await broadcast(addr_client, client_message, writer)
        except ConnectionResetError:
            writers_list.remove(writer)
            await broadcast("SERVER", lost_connection_message, writer)
            break
    writer.close()


def ip_selector():
    # TEST MODE OR NOT
    if args.test:
        IP = socket.gethostbyname(socket.gethostname())
        PORT = 5051
    else:
        IP = input('Choose your IP (type "my" if the server use your own IP): ')
        if IP.upper() == "MY":
            IP = socket.gethostbyname(socket.gethostname())
        PORT = 5051
    return IP, PORT


async def main():
    IP, PORT = ip_selector()
    # OPEN SERVER
    try:
        server = await asyncio.start_server(handle, IP, PORT)
        addr_servidor = server.sockets[0].getsockname()
        logging.info(f"[STARTIG] Server is running in {addr_servidor}")
        print(f"[STARTIG] Server is running in {addr_servidor}")
    except Exception:
        logging.info("[SERVER] failed to creating server")
        print("[SERVER] failed to creating server")
    else:
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
