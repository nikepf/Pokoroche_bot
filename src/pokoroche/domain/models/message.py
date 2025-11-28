from sqlalchemy import Column, BigInteger, Text, DateTime, JSON, Float, ForeignKey
from datetime import datetime, timezone
from src.pokoroche.infrastructure.database.database import Base

class MessageEntity(Base):
    """Сущность сообщения из чата"""
    
    __tablename__ = "messages"
    
    id = Column(BigInteger, primary_key=True)
    telegram_message_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    importance_score = Column(Float, default=0.0)
    topics = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<MessageEntity(id={self.id}, chat_id={self.chat_id}, importance={self.importance_score})>"

# TODO: Реализовать методы бизнес-логики:
# - update_importance_score для обновления оценки важности
# - add_topic для добавления темы
# - is_important проверка является ли сообщение важным