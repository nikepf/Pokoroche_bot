from src.pokoroche.domain.models.message import MessageEntity
from src.pokoroche.infrastructure.database.models.message_model import MessageModel


def message_entity_to_model(entity: MessageEntity) -> MessageModel:
    model = MessageModel(
        telegram_message_id=entity.telegram_message_id,
        chat_id=entity.chat_id,
        user_id=entity.user_id,
        text=entity.text,
        importance_score=entity.importance_score,
        topics=entity.topics or [],
        meta=entity.metadata or {},
        created_at=entity.created_at,
    )
    if getattr(entity, "id", None) is not None:
        model.id = entity.id
    return model


def message_model_to_entity(model: MessageModel) -> MessageEntity:
    return MessageEntity(
        id=int(model.id) if model.id is not None else None,
        telegram_message_id=int(model.telegram_message_id),
        chat_id=int(model.chat_id),
        user_id=int(model.user_id),
        text=model.text,
        importance_score=float(model.importance_score or 0.0),
        topics=model.topics or [],
        metadata=model.meta or {},
        created_at=model.created_at,
    )
