from src.pokoroche.domain.models.user import UserEntity
from src.pokoroche.infrastructure.database.models.user_model import UserModel

def user_entity_to_model(entity: UserEntity) -> UserModel:
    """Преобразовать UserEntity в UserModel для сохранения в БД"""
    return UserModel(
        id=entity.id,
        telegram_id=entity.telegram_id,
        username=entity.username,
        first_name=entity.first_name,
        last_name=entity.last_name,
        settings=entity.settings,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )

def user_model_to_entity(model: UserModel) -> UserEntity:
    """Преобразовать UserModel из БД в UserEntity"""
    return UserEntity(
        id=model.id,
        telegram_id=model.telegram_id,
        username=model.username,
        first_name=model.first_name,
        last_name=model.last_name,
        settings=model.settings,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )