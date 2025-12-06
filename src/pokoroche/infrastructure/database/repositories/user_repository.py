from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from src.pokoroche.domain.models.user import UserEntity
from src.pokoroche.infrastructure.database.models.user_model import UserModel
from src.pokoroche.infrastructure.database.mappers.user_mapper import (
    user_entity_to_model, user_model_to_entity
)

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_telegram_id(self, telegram_id: int) -> Optional[UserEntity]:
        """Найти пользователя по telegram_id"""
        # TODO: Реализовать запрос к БД через SQLAlchemy
        raise NotImplementedError("Реализуйте find_by_telegram_id")

    async def insert(self, user: UserEntity) -> UserEntity:
        """Сохранить нового пользователя"""
        # TODO: Реализовать вставку в БД
        raise NotImplementedError("Реализуйте insert")

    async def update(self, user: UserEntity) -> None:
        """Обновить существующего пользователя"""
        # TODO: Реализовать обновление в БД
        raise NotImplementedError("Реализуйте update")

    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя по ID"""
        # TODO: Реализовать удаление
        raise NotImplementedError("Реализуйте delete")

    async def get_all(self, limit: int = 100) -> List[UserEntity]:
        """Получить всех пользователей с лимитом"""
        # TODO: Реализовать получение всех пользователей
        raise NotImplementedError("Реализуйте get_all")