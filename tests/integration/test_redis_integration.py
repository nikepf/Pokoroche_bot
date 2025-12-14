import pytest
from src.pokoroche.adapters.message_queue import MessageQueue

@pytest.mark.asyncio
async def test_message_queue_with_real_redis(real_redis):
    queue = MessageQueue(real_redis)

    message = {"event": "user_registered"}

    await queue.push("integration_queue", message)
    result = await queue.pop("integration_queue")

    assert result == message
