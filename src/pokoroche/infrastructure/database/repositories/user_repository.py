from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        model: Optional[UserModel] = result.scalar_one_or_none()
        if model is None:
            return None
        return user_model_to_entity(model)

    async def insert(self, user: UserEntity) -> UserEntity:
        """Сохранить нового пользователя"""
        model = user_entity_to_model(user)
        self.session.add(model)
        await self.session.flush()
        return user_model_to_entity(model)

    async def update(self, user: UserEntity) -> None:
        """Обновить существующего пользователя"""
        if user.id is None:
            raise ValueError("Нельзя обновить пользователя без id")

        model: Optional[UserModel] = await self.session.get(UserModel, user.id)
        if model is None:
            return

        model.telegram_id = user.telegram_id
        model.username = user.username
        model.first_name = user.first_name
        model.last_name = user.last_name
        model.settings = dict(user.settings or {})
        await self.session.flush()

    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя по ID"""
        model: Optional[UserModel] = await self.session.get(UserModel, user_id)
        if model is None:
            return False

        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_all(self, limit: int = 100) -> List[UserEntity]:
        """Получить всех пользователей с лимитом"""
        stmt = select(UserModel).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [user_model_to_entity(m) for m in models]
