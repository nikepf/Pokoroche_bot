from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IImportanceService(ABC):
    """Интерфейс сервиса анализа важности сообщений"""
    
    @abstractmethod
    async def calculate_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        """Рассчитать оценку важности сообщения"""
        pass
    
    @abstractmethod
    async def batch_calculate_importance(self, texts: List[str]) -> List[float]:
        """Пакетный расчет важности для нескольких сообщений"""
        pass

class ImportanceService(IImportanceService):
    """Сервис анализа важности"""
    
    def __init__(self, ml_client):
        self.ml_client = ml_client
    
    async def calculate_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        # TODO: Реализовать логику анализа важности:
        # Использовать модели для классификации, учитывать контекст, комбинировать несколько факторов в итоговую оценку
        return await self.ml_client.analyze_importance(text, context)
    
    async def batch_calculate_importance(self, texts: List[str]) -> List[float]:
        # TODO: Оптимизировать для пакетной обработки
        return [await self.calculate_importance(text) for text in texts]