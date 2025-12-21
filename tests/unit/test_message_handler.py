import pytest
from unittest.mock import AsyncMock
from src.pokoroche.commands.message_handler import MessageHandler
from src.pokoroche.domain.models.message import MessageEntity


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, message_data, should_analyze",
    [
        ("привет", {"message_id": 1, "date": 1700000000, "text": "привет"}, True),
        ("   ", {"message_id": 2, "date": 1700000000, "photo": [{"file_id": "p1"}]}, False),
        ("", {"message_id": 3, "date": 1700000000, "voice": {"file_id": "v1"}}, False),
        ("", {"message_id": 4, "date": 1700000000, "document": {"file_id": "d1"}}, False),
        ("", {"message_id": 5, "date": 1700000000, "sticker": {"file_id": "s1"}}, False),
    ],
)
async def test_message_handler_saves_messages_of_different_types(text, message_data, should_analyze):
    message_repo = AsyncMock()
    importance_service = AsyncMock()
    importance_service.calculate_importance = AsyncMock(return_value=0.7)
    topic_service = AsyncMock()
    topic_service.extract_topics = AsyncMock(return_value=["тема"])
    handler = MessageHandler(message_repo, importance_service, topic_service)

    await handler.handle(user_id=123, chat_id=777, text=text, message_data=message_data)

    message_repo.save.assert_awaited_once()
    saved_entity = message_repo.save.await_args.args[0]
    assert isinstance(saved_entity, MessageEntity)
    assert saved_entity.user_id == 123
    assert saved_entity.chat_id == 777
    assert saved_entity.telegram_message_id == message_data["message_id"]
    assert saved_entity.metadata == message_data

    if should_analyze:  # нормальный текст - все вызвано
        importance_service.calculate_importance.assert_awaited_once()
        topic_service.extract_topics.assert_awaited_once()
    else:
        importance_service.calculate_importance.assert_not_awaited()
        topic_service.extract_topics.assert_not_awaited()


@pytest.mark.asyncio
async def test_message_handler_skips_when_no_message_id():
    message_repo = AsyncMock()
    importance_service = AsyncMock()
    topic_service = AsyncMock()
    handler = MessageHandler(message_repo, importance_service, topic_service)
    await handler.handle(user_id=123, chat_id=777, text="hi", message_data={"date": 1700000000})

    message_repo.save.assert_not_awaited()
