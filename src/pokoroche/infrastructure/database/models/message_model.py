from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Float, JSON, Text, ForeignKey

from src.pokoroche.infrastructure.database.database import Base


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)

    telegram_message_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    text = Column(Text, nullable=False)
    importance_score = Column(Float, default=0.0)

    topics = Column(JSON, nullable=False, default=list)

    meta = Column("metadata", JSON, nullable=False, default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<MessageModel(id={self.id}, user_id={self.user_id}, importance_score={self.importance_score})>"
