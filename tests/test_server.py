from server import server
from unittest.mock import AsyncMock
import asyncio
import pytest


@pytest.fixture
def reader():
    reader = AsyncMock(asyncio.StreamReader)
    reader.read.return_value = b"test_message"
    return reader


@pytest.fixture
def writer():
    writer = AsyncMock(asyncio.StreamWriter)
    return writer


def test_write_message():
    addr = "localhost"
    message = "test_message"
    full_message = server.write_message(addr, message)
    assert full_message == (f"[{addr}] {message}")


def test_add_writer(writer):
    server.add_writer(writer)
    assert writer in server.writers_list
    server.del_writer(writer)


def test_del_writer(writer):
    server.add_writer(writer)
    server.del_writer(writer)
    assert writer not in server.writers_list


@pytest.mark.asyncio
async def test_broadcast(writer):
    server.add_writer(writer)
    message = "test_message"
    await server.broadcast(message)
    writer.write.assert_called_with(message.encode())
    server.del_writer(writer)


@pytest.mark.asyncio
async def test_read_message(reader):
    message = await server.read_message(reader)
    assert message == "test_message"


@pytest.mark.asyncio
async def test_handle_message(writer, reader):
    addr = "localhost"
    message = "test_message"
    message = f"[{addr}] {message}"
    server.add_writer(writer)
    await server.handle_message(reader, "localhost")
    writer.write.assert_called_with(message.encode())
    server.del_writer(writer)


@pytest.mark.asyncio
async def test_when_connection_is_false(reader, writer, mocker):
    mocker.patch("server.server.check_connection", return_value=False)
    await server.handle_connection(reader, writer)
    writer.close.assert_called_once()
