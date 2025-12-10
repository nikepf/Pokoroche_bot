from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.pokoroche.domain.models.message import MessageEntity
from src.pokoroche.infrastructure.database.models.message_model import MessageModel
from src.pokoroche.infrastructure.database.mappers.message_mapper import (
    message_entity_to_model, message_model_to_entity
)


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message: MessageEntity) -> MessageEntity:
        """Сохранить сообщение (создать или обновить)"""
        if getattr(message, "id", None) is None:
            model = message_entity_to_model(message)
            self.session.add(model)
            await self.session.flush()
            return message_model_to_entity(model)

        model: Optional[MessageModel] = await self.session.get(MessageModel, message.id)
        if model is None:
            model = message_entity_to_model(message)
            self.session.add(model)
            await self.session.flush()
            return message_model_to_entity(model)

        model.telegram_message_id = message.telegram_message_id
        model.chat_id = message.chat_id
        model.user_id = message.user_id
        model.text = message.text
        model.importance_score = message.importance_score
        model.topics = list(message.topics or [])
        model.metadata = dict(message.metadata or {})
        await self.session.flush()

        return message_model_to_entity(model)

    async def find_by_id(self, message_id: int) -> Optional[MessageEntity]:
        """Найти сообщение по ID"""
        model: Optional[MessageModel] = await self.session.get(MessageModel, message_id)
        if model is None:
            return None
        return message_model_to_entity(model)

    async def get_recent_messages(
        self,
        user_id: int,
        limit: int = 50,
    ) -> List[MessageEntity]:
        """Получить последние сообщения пользователя"""
        stmt = (
            select(MessageModel)
            .where(MessageModel.user_id == user_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [message_model_to_entity(m) for m in models]

    async def get_important_messages(
        self,
        user_id: int,
        threshold: float = 0.5,
        from_date: Optional[datetime] = None,
    ) -> List[MessageEntity]:
        """Получить важные сообщения пользователя"""
        conditions = [
            MessageModel.user_id == user_id,
            MessageModel.importance_score >= threshold,
        ]
        if from_date is not None:
            conditions.append(MessageModel.created_at >= from_date)

        stmt = (
            select(MessageModel)
            .where(and_(*conditions))
            .order_by(
                MessageModel.importance_score.desc(),
                MessageModel.created_at.desc(),
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [message_model_to_entity(m) for m in models]

    async def get_messages_by_topics(
        self,
        user_id: int,
        topics: List[str],
        from_date: Optional[datetime] = None,
    ) -> List[MessageEntity]:
        """Получить сообщения по темам"""
        conditions = [MessageModel.user_id == user_id]
        if from_date is not None:
            conditions.append(MessageModel.created_at >= from_date)
        if topics:
            conditions.append(MessageModel.topics.contains(topics))

        stmt = (
            select(MessageModel)
            .where(and_(*conditions))
            .order_by(MessageModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [message_model_to_entity(m) for m in models]
