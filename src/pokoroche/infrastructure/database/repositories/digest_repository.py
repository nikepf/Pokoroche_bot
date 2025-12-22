from datetime import datetime
from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.pokoroche.domain.models.digest import DigestEntity
from src.pokoroche.infrastructure.database.models.digest_model import DigestModel
from src.pokoroche.infrastructure.database.models.message_model import MessageModel
from src.pokoroche.infrastructure.database.models.user_model import UserModel
from src.pokoroche.infrastructure.database.mappers.digest_mapper import (
    digest_entity_to_model, digest_model_to_entity
)


class DigestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_delivery(
        self,
        telegram_id: int,
        from_time: datetime,
        sent_at: datetime,
        items_count: int,
        digest: str,
    ) -> DigestEntity:
        """Сохранить отправленный дайджест"""
        stmt_user = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result_user = await self.session.execute(stmt_user)
        user_model = result_user.scalar_one_or_none()
        if user_model is None:
            raise ValueError(f"User with telegram_id={telegram_id} not found")

        entity = DigestEntity(
            user_id=user_model.id,
            content=digest,
            important_messages=[],
            summary=None,
            feedback_score=None,
            sent_at=sent_at,
        )
        model = digest_entity_to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return digest_model_to_entity(model)

    async def get_important_items(
        self,
        telegram_id: int,
        from_time: datetime,
        topics: List[str],
    ) -> List[dict]:
        """Получить важные сообщения для дайджеста"""
        stmt_user = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result_user = await self.session.execute(stmt_user)
        user_model = result_user.scalar_one_or_none()
        if user_model is None:
            return []

        conditions = [
            MessageModel.user_id == user_model.id,
            MessageModel.created_at >= from_time,
            MessageModel.importance_score >= 0.5,
        ]
        if topics:
            conditions.append(MessageModel.topics.contains(topics))

        stmt = (
            select(MessageModel)
            .where(and_(*conditions))
            .order_by(
                MessageModel.importance_score.desc(),
                MessageModel.created_at.desc(),
            )
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()

        items: List[dict] = []
        for m in messages:
            items.append(
                {
                    "id": m.id,
                    "telegram_message_id": m.telegram_message_id,
                    "chat_id": m.chat_id,
                    "text": m.text,
                    "importance_score": m.importance_score,
                    "topics": m.topics or [],
                    "created_at": m.created_at,
                }
            )

        return items

    async def get_user_digests(
        self,
        user_id: int,
        limit: int = 10,
    ) -> List[DigestEntity]:
        """Получить историю дайджестов пользователя"""
        stmt = (
            select(DigestModel)
            .where(DigestModel.user_id == user_id)
            .order_by(DigestModel.sent_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [digest_model_to_entity(m) for m in models]

    async def update_feedback(
        self,
        digest_id: int,
        feedback_score: float,
    ) -> None:
        """Обновить фидбек по дайджесту"""
        model = await self.session.get(DigestModel, digest_id)
        if model is None:
            return

        model.feedback_score = float(feedback_score)
        await self.session.flush()
