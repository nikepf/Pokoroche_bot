import pytest
from unittest.mock import AsyncMock
from src.pokoroche.commands.settings_cmd import SettingsCommand


class FakeUser:
    def __init__(self, settings=None):
        self.settings = settings or {}
        self.last_update_kwargs = None

    def update_settings(self, **kwargs):
        # имитация обновления настроек
        self.settings.update(kwargs)
        self.last_update_kwargs = kwargs


@pytest.mark.asyncio
async def test_settings_user_not_found():
    repo = AsyncMock()  # фейковый репозиторий
    repo.find_by_telegram_id = AsyncMock(return_value=None)

    cmd = SettingsCommand(user_repository=repo)
    reply = await cmd.handle(user_id=123, message={"text": "/settings"})

    assert reply == "Нажми /start, чтобы я тебя зарегистрировал."
    repo.find_by_telegram_id.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_settings_show_current():
    user = FakeUser(settings={"digest_time": "21:30", "detail_level": "full", "timezone": "Europe/Moscow"})
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=user)

    cmd = SettingsCommand(user_repository=repo)
    reply = await cmd.handle(user_id=123, message={"text": "/settings"})

    assert "Время дайджеста: 21:30" in reply
    assert "Детализация: full" in reply
    assert "Часовой пояс: Europe/Moscow" in reply


# проверка на изменения
@pytest.mark.asyncio
async def test_settings_time_ok_updates_user():
    user = FakeUser(settings={"digest_time": "20:00", "detail_level": "brief"})
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=user)
    repo.update = AsyncMock(return_value=True)

    cmd = SettingsCommand(user_repository=repo)
    reply = await cmd.handle(user_id=123, message={"text": "/settings time 11:10"})

    assert reply == "Новое время дайджеста: 11:10"
    assert user.settings["digest_time"] == "11:10"
    assert user.last_update_kwargs == {"digest_time": "11:10"}
    repo.update.assert_awaited_once_with(user)


# неверный формат времени
@pytest.mark.asyncio
async def test_settings_time_invalid_does_not_update():
    user = FakeUser(settings={"digest_time": "20:00", "detail_level": "brief"})
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=user)
    repo.update = AsyncMock(return_value=True)

    cmd = SettingsCommand(user_repository=repo)
    reply = await cmd.handle(user_id=123, message={"text": "/settings time 99:99"})

    assert reply == "Неверный формат. Пример: /settings time 20:00"
    assert user.settings["digest_time"] == "20:00"
    repo.update.assert_not_awaited()


# проверка на изменения
@pytest.mark.asyncio
async def test_settings_detail_ok_updates_user():
    user = FakeUser(settings={"detail_level": "brief"})
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=user)
    repo.update = AsyncMock(return_value=True)

    cmd = SettingsCommand(user_repository=repo)
    reply = await cmd.handle(user_id=123, message={"text": "/settings detail full"})

    assert reply == "Новая детализация: full"
    assert user.settings["detail_level"] == "full"
    repo.update.assert_awaited_once_with(user)


# неверный формат
@pytest.mark.asyncio
async def test_settings_detail_invalid_does_not_update():
    user = FakeUser(settings={"detail_level": "brief"})
    repo = AsyncMock()
    repo.find_by_telegram_id = AsyncMock(return_value=user)
    repo.update = AsyncMock(return_value=True)

    cmd = SettingsCommand(user_repository=repo)
    reply = await cmd.handle(user_id=123, message={"text": "/settings detail meow"})

    assert reply == "Неверный формат. Варианты: brief или full"
    assert user.settings["detail_level"] == "brief"
    repo.update.assert_not_awaited()
