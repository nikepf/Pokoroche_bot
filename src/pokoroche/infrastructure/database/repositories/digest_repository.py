from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, and_, or_, cast, Text
from sqlalchemy.ext.asyncio import AsyncSession

from src.pokoroche.domain.models.digest import DigestEntity
from src.pokoroche.infrastructure.database.models.digest_model import DigestModel
from src.pokoroche.infrastructure.database.models.user_model import UserModel
from src.pokoroche.infrastructure.database.models.message_model import MessageModel
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
        digest: str
    ) -> DigestEntity:
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise ValueError(f"User with telegram_id={telegram_id} not found")

        entity = DigestEntity(
            user_id=int(user.id),
            content=digest,
            important_messages=[],
            summary=None,
            feedback_score=None,
            sent_at=sent_at,
        )

        model = digest_entity_to_model(entity)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return digest_model_to_entity(model)

    async def get_important_items(
        self,
        telegram_id: int,
        from_time: datetime,
        topics: List[str]
    ) -> List[dict]:
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return []

        conditions = [
            MessageModel.user_id == int(user.id),
            MessageModel.created_at >= from_time,
            MessageModel.importance_score >= 0.5,
        ]

        if topics:
            topic_filters = [cast(MessageModel.topics, Text).like(f'%"{t}"%') for t in topics]
            conditions.append(or_(*topic_filters))

        stmt = (
            select(MessageModel)
            .where(and_(*conditions))
            .order_by(MessageModel.importance_score.desc(), MessageModel.created_at.desc())
        )

        result = await self.session.execute(stmt)
        messages = result.scalars().all()

        items = []
        for m in messages:
            items.append(
                {
                    "id": int(m.id),
                    "text": m.text,
                    "importance_score": float(m.importance_score or 0.0),
                    "topics": m.topics or [],
                    "created_at": m.created_at,
                }
            )
        return items

    async def get_user_digests(self, user_id: int, limit: int = 10) -> List[DigestEntity]:
        stmt = (
            select(DigestModel)
            .where(DigestModel.user_id == user_id)
            .order_by(DigestModel.sent_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [digest_model_to_entity(m) for m in models]

    async def update_feedback(self, digest_id: int, feedback_score: float) -> None:
        stmt = select(DigestModel).where(DigestModel.id == digest_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return
        model.feedback_score = feedback_score
        await self.session.flush()
