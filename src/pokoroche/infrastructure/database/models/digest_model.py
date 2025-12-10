from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Float, JSON, Text, ForeignKey

from src.pokoroche.infrastructure.database.database import Base


class DigestModel(Base):
    """SQLAlchemy модель для таблицы digests"""
    __tablename__ = "digests"

    id = Column(BigInteger, primary_key=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content = Column(Text, nullable=False)

    important_messages = Column(
        JSON,
        nullable=False,
        default=list,
    )

    summary = Column(Text, nullable=True)
    feedback_score = Column(Float, nullable=True)

    sent_at = Column(DateTime, default=datetime.now(timezone.utc), index=True)

    def __repr__(self) -> str:
        return f"<DigestModel(id={self.id}, user_id={self.user_id}, sent_at={self.sent_at})>"
