from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import BigInteger, Column, DateTime, JSON, String
from sqlalchemy.orm import relationship
from src.pokoroche.infrastructure.database.database import Base


class UserEntity(Base):
    """Сущность пользователя Telegram."""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    settings = Column(
        JSON,
        default=lambda: {
            "digest_time": "20:00",
            "detail_level": "brief",
            "timezone": "Europe/Moscow",
        },
    )
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<UserEntity(id={self.id}, telegram_id={self.telegram_id}, "
            f"username='{self.username}')>"
        )

    def update_settings(self, **settings: Any) -> None:
        """Обновление словаря настроек пользователя.

        Пример:
            user.update_settings(digest_time="21:00", detail_level="full")
        """
        current: Dict[str, Any] = dict(self.settings or {})
        current.update(settings)
        self.settings = current
        self.updated_at = datetime.now(timezone.utc)

    def subscribe_to_topic(self, topic: str) -> None:
        """Подписка пользователя на тему.

        Темы хранятся внутри ``settings`` в ключе ``"topics"``.
        """
        topic = topic.strip()
        if not topic:
            return

        current: Dict[str, Any] = dict(self.settings or {})
        topics: List[str] = list(current.get("topics", []))
        if topic not in topics:
            topics.append(topic)
            current["topics"] = topics
            self.settings = current
            self.updated_at = datetime.now(timezone.utc)

    def can_receive_digest(self) -> bool:
        """Проверка: может ли пользователь получать дайджесты.

        По умолчанию пользователь считается активным, если явно не указано
        обратное (``digest_enabled=False``) в настройках.
        """
        current: Dict[str, Any] = dict(self.settings or {})
        return bool(current.get("digest_enabled", True))
