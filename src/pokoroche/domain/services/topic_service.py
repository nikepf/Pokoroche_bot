from abc import ABC, abstractmethod
from typing import List, Dict

class ITopicService(ABC):
    """Интерфейс сервиса определения и классификации тем"""
    
    @abstractmethod
    async def extract_topics(self, text: str) -> List[str]:
        """Извлечь релевантные темы из текста"""
        pass
    
    @abstractmethod
    async def categorize_message(self, text: str) -> Dict[str, float]:
        """Классифицировать сообщение по темам с оценками уверенности"""
        pass

class TopicService(ITopicService):
    """Сервис определения тем"""
    
    def __init__(self, ml_client):
        self.ml_client = ml_client
    
    async def extract_topics(self, text: str) -> List[str]:
        # TODO: Реализовать извлечение тем
        return await self.ml_client.extract_topics(text)
    
    async def categorize_message(self, text: str) -> Dict[str, float]:
        # TODO: Реализовать многоклассовую классификацию
        topics = await self.extract_topics(text)
        return {topic: 1.0 for topic in topics}