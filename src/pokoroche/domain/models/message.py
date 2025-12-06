from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


@dataclass
class MessageEntity:
    """Сущность сообщения из чата."""

    __tablename__ = "messages"

    telegram_message_id: int
    chat_id: int
    user_id: int
    text: str
    importance_score: float = 0.0
    topics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None  # ID из БД
    created_at: datetime = field(default_factory=datetime.utcnow)

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
