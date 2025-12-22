import pytest
from unittest.mock import AsyncMock
from src.pokoroche.commands.subscribe_cmd import SubscribeCommand


class FakeUser:
    def __init__(self, settings=None):
        self.settings = settings or {}

    def update_settings(self, **kwargs):
        self.settings.update(kwargs)


@pytest.mark.asyncio
async def test_subscribe_user_not_found():
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=None)
    topic_service = AsyncMock()
    cmd = SubscribeCommand(user_repository=repo, topic_service=topic_service)
    reply = await cmd.handle(user_id=123, message={"text": "/subscribe"})

    assert reply == "Нажми /start, чтобы я тебя зарегистрировал."
    repo.find_by_telegram_id.assert_awaited_once_with(123)


# список тем пустой
@pytest.mark.asyncio
async def test_subscribe_show_empty_list():
    user = FakeUser(settings={"topics": []})
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=user)
    topic_service = AsyncMock()
    cmd = SubscribeCommand(user_repository=repo, topic_service=topic_service)
    reply = await cmd.handle(user_id=123, message={"text": "/subscribe"})

    assert "У тебя пока нет подписок." in reply
    assert "/subscribe add <тема>" in reply
    assert "/subscribe remove <тема>" in reply


# проверка обновления списка тем
@pytest.mark.asyncio
async def test_subscribe_add_topic_updates_user():
    user = FakeUser(settings={"topics": ["акосик"]})
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=user)
    repo.update = AsyncMock(return_value=True)
    topic_service = AsyncMock()
    cmd = SubscribeCommand(user_repository=repo, topic_service=topic_service)
    reply = await cmd.handle(user_id=123, message={"text": "/subscribe add питончик"})
    assert reply == "Готово! Ты подписался на тему: питончик"
    assert user.settings["topics"] == ["акосик", "питончик"]
    repo.update.assert_awaited_once_with(user)