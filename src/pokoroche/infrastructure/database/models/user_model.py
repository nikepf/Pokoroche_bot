from sqlalchemy import BigInteger, Column, DateTime, JSON, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from src.pokoroche.infrastructure.database.database import Base

class UserModel(Base):
    """SQLAlchemy модель для таблицы users"""
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
        return f"<UserModel(id={self.id}, telegram_id={self.telegram_id})>"