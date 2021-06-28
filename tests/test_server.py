from server import create_server
import asynctest
import asyncio
import pytest


@pytest.fixture
def StreamReader():
    reader = asynctest.mock.Mock(asyncio.StreamReader)
    reader.read.return_value = b"Test_message"
    return reader


@pytest.fixture
def StreamWriter():
    writer = asynctest.mock.Mock(asyncio.StreamWriter)
    return writer


def test_write_message():
    addr = "cliente"
    message = "Test_message"
    full_message = create_server.write_message(addr, message)
    assert full_message == (f"[{addr}] {message}")
    pass


def test_add_writer(StreamWriter):
    create_server.add_writer(StreamWriter)
    assert StreamWriter in create_server.writers_list


def test_del_writer(StreamWriter):
    create_server.add_writer(StreamWriter)
    create_server.del_writer(StreamWriter)
    assert StreamWriter not in create_server.writers_list


@pytest.mark.asyncio
async def test_broadcast(StreamWriter):
    create_server.add_writer(StreamWriter)
    message = "Test_message"
    await create_server.broadcast(message)


@pytest.mark.asyncio
async def test_read_message(StreamReader):
    message = await create_server.read_message(StreamReader)
    assert message == "Test_message"


@pytest.mark.asyncio
async def test_handle_message(StreamWriter, StreamReader, mocker):
    mocker.patch("server.create_server.check_connection", return_value=True)
    create_server.add_writer(StreamWriter)
    await create_server.handle_message(StreamWriter, StreamReader, "Cliente")
