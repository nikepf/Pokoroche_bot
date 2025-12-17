from abc import ABC, abstractmethod
from typing import List, Dict, Any
import hashlib
import aiohttp
import json
from .dtos.cache_dto import CacheItem

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
                    async with session.post(url, json=payload, timeout=self.timeout) as resp:
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
        

class CachedMLClient(MLClient):
    """ML клиент с кешированием результатов в Redis"""

    CACHE_TTL = 3600 #Значение будет находиться в кеше CACHE_TTL секунд
    
    def __init__(self, ml_service_url: str, redis_client, timeout: int = 30, max_retries: int = 3):
           super().__init__(ml_service_url, timeout, max_retries)
           self.redis = redis_client

    def _generate_cache_key(self, text: str, prefix: str) -> str:
        """Генерируем уникальный ключ для Redis по тексту"""
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"{prefix}:{text_hash}"
    
    async def analyze_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        """Анализ важности с кешированием"""
        key = self._generate_cache_key(text, "importance")

        cached = await self.redis.get(key)
        if cached:
            return float(cached)
        
        result = await super().analyze_importance(text, context)
        await self.redis.set(key, str(result), expire=self.CACHE_TTL)
        return result

    async def extract_topics(self, text: str) -> List[str]:
        """Извлечение тем с кешированием"""
        key = self._generate_cache_key(text, "topics")

        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        result = await super().extract_topics(text)
        await self.redis.set(key, json.dumps(result), expire=self.CACHE_TTL)
        return result