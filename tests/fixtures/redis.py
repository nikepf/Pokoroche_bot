import pytest
from src.pokoroche.adapters.redis_client import RedisClient

@pytest.fixture
async def real_redis():
    client = RedisClient("redis://localhost:6379")

    await client.connect()
    yield client
    await client.disconnect()
