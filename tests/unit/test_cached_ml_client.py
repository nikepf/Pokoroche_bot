import pytest
from src.pokoroche.adapters.ml_client import CachedMLClient

class FakeMLClient(CachedMLClient):
    def __init__(self, redis_client):
        super().__init__("http://fake-ml", redis_client)
        self.calls = 0

    async def analyze_importance(self, text, context=None):
        self.calls += 1
        return 0.5


@pytest.mark.asyncio
async def test_ml_client_cache(fake_redis):
    ml_client = FakeMLClient(fake_redis)

    result1 = await ml_client.analyze_importance("hello")
    result2 = await ml_client.analyze_importance("hello")

    assert result1 == result2
    assert ml_client.calls == 1
