from client import create_client
import asynctest
import asyncio
import pytest


@pytest.fixture
def StreamReader():
    reader = asynctest.mock.Mock(asyncio.StreamReader)
    # reader.read.return_value = b"Test_message"
    return reader


@pytest.fixture
def StreamWriter():
    writer = asynctest.mock.Mock(asyncio.StreamWriter)
    return writer


@pytest.mark.asyncio
async def test_send_message(StreamWriter, StreamReader):
    send_message = "Test_message"
    create_client.send_message(send_message, StreamWriter)
    message = await StreamReader.read(100)
    assert send_message == message
