import pytest
from src.pokoroche.adapters.message_queue import MessageQueue

@pytest.mark.asyncio
async def test_message_queue_push_pop(fake_redis):
    queue = MessageQueue(fake_redis)

    message = {"id": 1, "text": "hello"}

    await queue.push("test_queue", message)
    result = await queue.pop("test_queue")

    assert result == message
