from abc import ABC, abstractmethod
from typing import List, Dict, Any
import aiohttp

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
        self.ml_service_url = ml_service_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def analyze_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        """Реализация HTTP запроса к ML сервису для анализа важности"""
        url = f"{self.ml_service_url}/importance"
        payload = {"text": text, "context": context or {}}

        for _ in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=self.timeuot) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        return float(data["importance"])
            except Exception:
                continue

        return 0.0
    
    async def extract_topics(self, text: str) -> List[str]:
        """Извлечение списка тем из текста."""
        url = f"{self.ml_service_url}/topics"
        payload = {"text":text}

        for _ in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=self.timeout) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        return list(data["topics"])
            except Exception:
                continue
        
        return []

    async def health_check(self) -> bool:
        """Проверка, доступен ли ML сервер"""
        url = f"{self.ml_service_url}/health"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, timeout=self.timeout) as resp:
                    return resp.status == 200
        except Exception:
            return False