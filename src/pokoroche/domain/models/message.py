from datetime import datetime, timezone
from typing import List
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, JSON, Text
from src.pokoroche.infrastructure.database.database import Base


class MessageEntity(Base):
    """Сущность сообщения из чата."""

    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    telegram_message_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    importance_score = Column(Float, default=0.0)
    topics = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<MessageEntity(id={self.id}, chat_id={self.chat_id}, "
            f"importance={self.importance_score})>"
        )

    def update_importance_score(self, score: float) -> None:
        """Обновление оценки важности сообщения."""
        try:
            self.importance_score = float(score)
        except (TypeError, ValueError):
            return

    def add_topic(self, topic: str) -> None:
        """Добавление темы к сообщению без дублей."""
        topic = topic.strip()
        if not topic:
            return

        current: List[str] = list(self.topics or [])
        if topic not in current:
            current.append(topic)
            self.topics = current

    def is_important(self, threshold: float = 0.5) -> bool:
        """Проверка: является ли сообщение важным.

        :param threshold: порог важности, по умолчанию 0.5.
        """
        score = self.importance_score or 0.0
        return score >= threshold
