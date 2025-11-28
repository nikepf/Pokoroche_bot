from sqlalchemy import Column, BigInteger, Text, DateTime, JSON, ForeignKey, Float
from datetime import datetime, timezone
from src.pokoroche.infrastructure.database.database import Base

class DigestEntity(Base):
    """Сущность дайджеста"""
    
    __tablename__ = "digests"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    important_messages = Column(JSON, default=list)
    summary = Column(Text)
    sent_at = Column(DateTime, default=datetime.now(timezone.utc))
    feedback_score = Column(Float)

    def __repr__(self):
        return f"<DigestEntity(id={self.id}, user_id={self.user_id}, sent_at={self.sent_at})>"

# TODO: Реализовать методы бизнес-логики:
# - add_message для добавления сообщения в дайджест
# - generate_summary для генерации сводки
# - update_feedback для обновления оценки пользователя