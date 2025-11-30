from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, JSON, Text
from src.pokoroche.infrastructure.database.database import Base


class DigestEntity(Base):
    """Сущность дайджеста.

    Хранение сгенерированного дайджеста для пользователя, а также
    вспомогательной информации по сообщениям и пользовательского фидбека.
    """

    __tablename__ = "digests"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    important_messages = Column(JSON, default=list)
    summary = Column(Text)
    sent_at = Column(DateTime, default=datetime.now(timezone.utc))
    feedback_score = Column(Float)

    def __repr__(self) -> str:
        return (
            f"<DigestEntity(id={self.id}, user_id={self.user_id}, "
            f"sent_at={self.sent_at})>"
        )

    def add_message(self, message: Dict[str, Any]) -> None:
        """Добавление информации о важном сообщении в дайджест.

        Ожидается, что в ``message`` попадёт всё, что нужно для отображения в
        дайджесте (id сообщения, чат, текст, оценка важности и т.п.).
        """
        messages: List[Dict[str, Any]] = list(self.important_messages or [])
        messages.append(message)
        self.important_messages = messages

    def generate_summary(self, max_length: int = 500) -> str:
        """Генерация простой текстовой сводки по дайджесту.

        Сейчас реализована максимально изи логика:
        * использование уже существующей ``summary``, если она заполнена;
        * обрезка текста до первых ``max_length`` символов из ``content`` с
          записью в ``summary``.

        В дальнейшем эту функцию можно заменить на вызов МЛьки.
        """
        if self.summary:
            return self.summary

        base_text = (self.content or "").strip()
        if not base_text:
            self.summary = ""
            return self.summary

        if len(base_text) <= max_length:
            self.summary = base_text
        else:
            self.summary = base_text[: max_length - 1].rstrip() + "…"

        return self.summary

    def update_feedback(self, score: Optional[float]) -> None:
        """Обновление пользовательского фидбека по дайджесту.

        Сейчас просто сохраняется последнее значение оценки.
        """
        if score is None:
            self.feedback_score = None
            return

        try:
            value = float(score)
        except (TypeError, ValueError):
            return

        self.feedback_score = value
