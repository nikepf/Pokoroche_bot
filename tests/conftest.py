import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

import pytest

class FakeRedis:
    def __init__(self):
        self.storage = {}
        self.queue = []

    async def get(self, key):
        return self.storage.get(key)

    async def set(self, key, value, expire=None):
        self.storage[key] = value
        return True

    async def rpush(self, key, value):
        self.queue.append(value)
        return len(self.queue)

    async def lpop(self, key):
        if not self.queue:
            return None
        return self.queue.pop(0)

    async def llen(self, key):
        return len(self.queue)


@pytest.fixture
def fake_redis():
    return FakeRedis()
