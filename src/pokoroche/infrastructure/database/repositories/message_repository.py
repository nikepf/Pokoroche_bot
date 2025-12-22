from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from src.pokoroche.domain.models.message import MessageEntity
from src.pokoroche.infrastructure.database.models.message_model import MessageModel
from src.pokoroche.infrastructure.database.mappers.message_mapper import (
    message_entity_to_model, message_model_to_entity
)


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message: MessageEntity) -> MessageEntity:
        if message.id is not None:
            stmt = select(MessageModel).where(MessageModel.id == message.id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                model = message_entity_to_model(message)
                self.session.add(model)
            else:
                model.telegram_message_id = message.telegram_message_id
                model.chat_id = message.chat_id
                model.user_id = message.user_id
                model.text = message.text
                model.importance_score = message.importance_score
                model.topics = message.topics
                model.meta = message.metadata
                model.created_at = message.created_at
        else:
            model = message_entity_to_model(message)
            self.session.add(model)

        await self.session.flush()
        await self.session.refresh(model)
        return message_model_to_entity(model)

    async def find_by_id(self, message_id: int) -> Optional[MessageEntity]:
        stmt = select(MessageModel).where(MessageModel.id == message_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return message_model_to_entity(model)

    async def get_recent_messages(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[MessageEntity]:
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
        from_date: Optional[datetime] = None
    ) -> List[MessageEntity]:
        conditions = [
            MessageModel.user_id == user_id,
            MessageModel.importance_score >= threshold,
        ]
        if from_date is not None:
            conditions.append(MessageModel.created_at >= from_date)

        stmt = (
            select(MessageModel)
            .where(and_(*conditions))
            .order_by(MessageModel.importance_score.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [message_model_to_entity(m) for m in models]

    async def get_messages_by_topics(
        self,
        user_id: int,
        topics: List[str],
        from_date: Optional[datetime] = None
    ) -> List[MessageEntity]:
        conditions = [MessageModel.user_id == user_id]
        if from_date is not None:
            conditions.append(MessageModel.created_at >= from_date)

        stmt = select(MessageModel).where(and_(*conditions))
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        filtered = []
        topics_set = set(topics)
        for m in models:
            msg_topics = set(m.topics or [])
            if msg_topics & topics_set:
                filtered.append(m)

        filtered.sort(key=lambda x: (x.created_at or datetime.min), reverse=True)
        return [message_model_to_entity(m) for m in filtered]
