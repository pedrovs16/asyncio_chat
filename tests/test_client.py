from client import client
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


@pytest.mark.asyncio
async def test_send_message(writer):
    message = "test_message"
    await client.send_message(message, writer)
    writer.write.assert_called_with(message.encode())


@pytest.mark.asyncio
async def test_read_message(reader):
    expect_message = b"test_message"
    message = await client.read_message(reader)
    assert message == expect_message


@pytest.mark.asyncio
async def test_when_message_is_exit(writer, mocker):
    with pytest.raises(SystemExit):
        mocker.patch("client.client.write_input", return_value="EXIT")
        await client.write_task(writer)


@pytest.mark.asyncio
async def test_when_messege_is_none(reader):
    with pytest.raises(SystemExit):
        reader.read.return_value = b""
        await client.read_task(reader)
