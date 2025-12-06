from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


@dataclass
class UserEntity:
    """Сущность пользователя Telegram."""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=lambda: {
        "digest_time": "20:00",
        "detail_level": "brief",
        "timezone": "Europe/Moscow",
    })
    id: Optional[int] = None  # ID из БД
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


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
