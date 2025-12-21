import pytest
from unittest.mock import AsyncMock
from src.pokoroche.commands.stats_cmd import StatsCommand


class FakeUser:
    def __init__(self, settings=None):
        self.settings = settings or {}


class FakeDigest:
    def __init__(self, feedback_score=None, important_messages=None):
        self.feedback_score = feedback_score
        self.important_messages = important_messages


@pytest.mark.asyncio
async def test_stats_user_not_found():
    user_repo = AsyncMock()
    user_repo.find_by_telegram_id = AsyncMock(return_value=None)
    digest_repo = AsyncMock()
    cmd = StatsCommand(user_repo, digest_repo)
    reply = await cmd.handle(user_id=123, message={"text": "/stats"})
    assert reply == "Нажми /start, чтобы я тебя зарегистрировал."
    user_repo.find_by_telegram_id.assert_awaited_once_with(123)


# случай, когда репозорий дайджестов упал
@pytest.mark.asyncio
async def test_stats_digest_repo_error():
    user_repo = AsyncMock()
    user_repo.find_by_telegram_id = AsyncMock(return_value=FakeUser())
    digest_repo = AsyncMock()
    digest_repo.get_user_digests = AsyncMock(side_effect=Exception("meow"))
    cmd = StatsCommand(user_repo, digest_repo)
    reply = await cmd.handle(user_id=123, message={"text": "/stats"})
    assert reply == "Не получилось получить статистику. Попробуй позже."
    user_repo.find_by_telegram_id.assert_awaited_once_with(123)
    digest_repo.get_user_digests.assert_awaited_once_with(user_id=123, limit=1000)


@pytest.mark.asyncio
async def test_stats_success():
    user_repo = AsyncMock()
    user_repo.find_by_telegram_id = AsyncMock(return_value=FakeUser())

    digests = [
        FakeDigest(
            feedback_score=1,
            important_messages=[
                {"topics": ["матан", "питон"]},
                "bad_msg",
            ],
        ),
        FakeDigest(
            feedback_score=0,
            important_messages=[
                {"topics": ["матан ", " питон ", " тервер "]},
                {"topics": "   "},
            ],
        ),
        FakeDigest(
            feedback_score=None,
            important_messages="wow",
        ),
    ]

    digest_repo = AsyncMock()
    digest_repo.get_user_digests = AsyncMock(return_value=digests)

    cmd = StatsCommand(user_repo, digest_repo)
    reply = await cmd.handle(user_id=123, message={"text": "/stats"})

    assert reply == "\n".join([
        "Статистика",
        "Дайджестов отправлено: 3",
        "Средняя оценка: 0.50",
        "Темы (топ 10):",
        "• матан: 2",
        "• питон: 2",
        "• тервер: 1",
    ])

    user_repo.find_by_telegram_id.assert_awaited_once_with(123)
    digest_repo.get_user_digests.assert_awaited_once_with(user_id=123, limit=1000)
