import pytest
from unittest.mock import AsyncMock
from src.pokoroche.commands.start_cmd import StartCommand


class FakeUser:
    def __init__(self, username="old", first_name="Old", last_name="Old", settings=None):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.settings = settings or {}

    def update_settings(self, **kwargs):
        self.settings.update(kwargs)


def msg() -> dict:
    return {
        "text": "/start",
        "from": {"username": "maria_ivanova", "first_name": "Maria", "last_name": "Ivanova"},
    }


@pytest.mark.asyncio
async def test_start_new_user_inserted():
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=None)
    repo.insert = AsyncMock(return_value=True)
    cmd = StartCommand(AsyncMock(), repo)
    reply = await cmd.handle(123, msg())
    assert "Привет! Я бот Pokoroche" in reply
    repo.insert.assert_awaited_once()


@pytest.mark.asyncio
async def test_start_existing_user_no_insert():
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=FakeUser())
    repo.insert = AsyncMock(return_value=True)
    cmd = StartCommand(AsyncMock(), repo)
    reply = await cmd.handle(123, msg())
    assert "Привет! Я бот Pokoroche" in reply
    repo.insert.assert_not_awaited()
