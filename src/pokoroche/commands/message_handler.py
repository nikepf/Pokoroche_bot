import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)

class MessageHandler:
    """Обработчик обычных текстовых сообщений (не команд)"""
    
    def __init__(self, 
                 message_repository,
                 importance_service,
                 topic_service):
        self.message_repository = message_repository
        self.importance_service = importance_service
        self.topic_service = topic_service
    
    async def handle(self, 
                    user_id: int, 
                    chat_id: int, 
                    text: str, 
                    message_data: Dict[str, Any]) -> None:
        """
        Обработать текстовое сообщение:
        1. Сохранить в БД через message_repository
        2. Проанализировать важность через importance_service  
        3. Извлечь темы через topic_service
        4. Сохранить метаданные
        
        Args:
            user_id: ID пользователя в Telegram
            chat_id: ID чата
            text: Текст сообщения
            message_data: Полные данные сообщения от Telegram API
        """
        logger.info("Processing message", 
                   user_id=user_id, 
                   chat_id=chat_id,
                   text_preview=text[:50] if text else "")
        
        # TODO: Реализовать логику обработки сообщения
        # 1. Создать MessageEntity
        # 2. Проанализировать важность
        # 3. Извлечь темы
        # 4. Сохранить в БД
        
        raise NotImplementedError("Реализуйте обработку сообщений")