from src.pokoroche.domain.models.digest import DigestEntity
from src.pokoroche.infrastructure.database.models.digest_model import DigestModel


def digest_entity_to_model(entity: DigestEntity) -> DigestModel:
    """Преобразовать DigestEntity в DigestModel для сохранения в БД"""
    return DigestModel(
        id=getattr(entity, "id", None),
        user_id=entity.user_id,
        content=entity.content,
        important_messages=entity.important_messages or [],
        summary=entity.summary,
        feedback_score=entity.feedback_score,
        sent_at=entity.sent_at,
    )


def digest_model_to_entity(model: DigestModel) -> DigestEntity:
    """Преобразовать DigestModel из БД в DigestEntity"""
    return DigestEntity(
        user_id=model.user_id,
        content=model.content,
        important_messages=model.important_messages or [],
        summary=model.summary,
        feedback_score=model.feedback_score,
        sent_at=model.sent_at,
        id=model.id,
    )
