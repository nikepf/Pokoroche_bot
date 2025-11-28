from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IMLClient(ABC):
    """Интерфейс для взаимодействия с ML сервисом"""
    
    @abstractmethod
    async def analyze_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        """Получить оценку важности текста (0.0 - 1.0)"""
        pass
    
    @abstractmethod
    async def extract_topics(self, text: str) -> List[str]:
        """Извлечь список тем из текста"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Проверить доступность ML сервиса"""
        pass

class MLClient(IMLClient):
    """Реализация ML клиента"""
    
    def __init__(self, ml_service_url: str, timeout: int = 30, max_retries: int = 3):
        self.ml_service_url = ml_service_url
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def analyze_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        # TODO: Реализовать HTTP запрос к ML сервису для анализа важности
        return 0.0
    
    async def extract_topics(self, text: str) -> List[str]:
        # TODO: Реализовать HTTP запрос к ML сервису для извлечения тем
        return []
    
    async def health_check(self) -> bool:
        # TODO: Реализовать проверку здоровья ML сервиса
        return True