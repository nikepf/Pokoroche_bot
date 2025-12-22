import structlog
from typing import Dict, Any
from datetime import datetime, timezone

from src.pokoroche.domain.models.message import MessageEntity

logger = structlog.get_logger(__name__)


class MessageHandler:
    """Обработчик обычных текстовых сообщений (не команд)"""

    def __init__(self,
                 message_repository,
                 importance_service,
                 topic_service):
        self.message_repository = message_repository
        self.importance_service = importance_service
        self.topic_service = topic_service

    async def handle(self,
                     user_id: int,
                     chat_id: int,
                     text: str,
                     message_data: Dict[str, Any]) -> None:
        """
        Обработать текстовое сообщение:
        1. Сохранить в БД через message_repository
        2. Проанализировать важность через importance_service
        3. Извлечь темы через topic_service
        4. Сохранить метаданные

        Args:
            user_id: ID пользователя в Telegram
            chat_id: ID чата
            text: Текст сообщения
            message_data: Полные данные сообщения от Telegram API
        """
        text = text if isinstance(text, str) else ""
        logger.info(
            "Processing message",
            user_id=user_id,
            chat_id=chat_id,
            text_preview=text[:50] if text else "",
        )
        has_text = bool(text.strip())

        # 1)создание MessageEntity
        telegram_message_id = message_data.get("message_id")
        if not isinstance(telegram_message_id, int):
            return

        created_at = datetime.now(timezone.utc)
        ts = message_data.get("date")  # время сообщения в формате числа(timestamp)
        if isinstance(ts, int):
            created_at = datetime.fromtimestamp(ts, tz=timezone.utc)
        message_entity = MessageEntity(
            telegram_message_id=telegram_message_id,
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            metadata=message_data,
            created_at=created_at,
        )

        #  2) анализ важности
        importance_score: float = 0.0
        if has_text and self.importance_service is not None:
            val = await self.importance_service.calculate_importance(text, context=message_data)
            if isinstance(val, (int, float)):
                importance_score = float(val)

        message_entity.update_importance_score(importance_score)  # обновление важности; метод из MessageEntity

        # 3) Извлечение тем
        topics = []
        if has_text and self.topic_service is not None:
            topics = await self.topic_service.extract_topics(text)

        for t in topics:
            message_entity.add_topic(t)

        # 4) Сохранение в БД
        await self.message_repository.save(message_entity)

        # запись в лог
        logger.info(
            "Message saved",
            telegram_message_id=telegram_message_id,
            chat_id=chat_id,
            user_id=user_id,
            importance_score=message_entity.importance_score,
            topics=message_entity.topics,
        )
