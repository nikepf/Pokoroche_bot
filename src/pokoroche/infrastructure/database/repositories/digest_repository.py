from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from src.pokoroche.domain.models.digest import DigestEntity
from src.pokoroche.infrastructure.database.models.digest_model import DigestModel
from src.pokoroche.infrastructure.database.mappers.digest_mapper import (
    digest_entity_to_model, digest_model_to_entity
)

class DigestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_delivery(self,
                           telegram_id: int,
                           from_time: datetime,
                           sent_at: datetime,
                           items_count: int,
                           digest: str) -> DigestEntity:
        """Сохранить отправленный дайджест"""
        # TODO: Реализовать сохранение дайджеста
        raise NotImplementedError("Реализуйте save_delivery")

    async def get_important_items(self,
                                 telegram_id: int,
                                 from_time: datetime,
                                 topics: List[str]) -> List[dict]:
        """Получить важные сообщения для дайджеста"""
        # TODO: Реализовать сложный запрос:
        raise NotImplementedError("Реализуйте get_important_items")

    async def get_user_digests(self,
                              user_id: int,
                              limit: int = 10) -> List[DigestEntity]:
        """Получить историю дайджестов пользователя"""
        # TODO: Реализовать запрос дайджестов пользователя с сортировкой по дате
        raise NotImplementedError("Реализуйте get_user_digests")

    async def update_feedback(self,
                             digest_id: int,
                             feedback_score: float) -> None:
        """Обновить фидбек по дайджесту"""
        # TODO: Реализовать обновление поля feedback_score
        raise NotImplementedError("Реализуйте update_feedback")