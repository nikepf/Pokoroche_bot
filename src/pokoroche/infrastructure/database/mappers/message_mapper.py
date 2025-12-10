from src.pokoroche.domain.models.message import MessageEntity
from src.pokoroche.infrastructure.database.models.message_model import MessageModel


def message_entity_to_model(entity: MessageEntity) -> MessageModel:
    """Преобразовать MessageEntity в MessageModel для сохранения в БД"""
    return MessageModel(
        id=getattr(entity, "id", None),
        telegram_message_id=entity.telegram_message_id,
        chat_id=entity.chat_id,
        user_id=entity.user_id,
        text=entity.text,
        importance_score=entity.importance_score,
        topics=entity.topics or [],
        metadata=entity.metadata or {},
        created_at=entity.created_at,
    )


def message_model_to_entity(model: MessageModel) -> MessageEntity:
    """Преобразовать MessageModel из БД в MessageEntity"""
    return MessageEntity(
        telegram_message_id=model.telegram_message_id,
        chat_id=model.chat_id,
        user_id=model.user_id,
        text=model.text,
        importance_score=model.importance_score or 0.0,
        topics=model.topics or [],
        metadata=model.metadata or {},
        created_at=model.created_at,
        id=model.id,
    )
