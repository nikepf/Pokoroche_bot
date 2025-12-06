from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from redis.asyncio import Redis


class IRedisClient(ABC):
    """Интерфейс для работы с Redis"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Установить подключение к Redis"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Закрыть подключение к Redis"""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Получить значение по ключу"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, expire: int = None) -> bool:
        """Установить значение с опциональным временем жизни"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Удалить ключ"""
        pass

class RedisClient(IRedisClient):
    """Реализация Redis клиента"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None
    
    async def connect(self) -> None:
        """Установление асинхронного подключения к Redis"""
        self.redis = Redis.from_url(
            self.redis_url,
            decode_responses=True,
        )
        await self.redis.ping()

    async def disconnect(self) -> None:
        """Закрытие подключения к Redis"""
        if self.redis:
            await self.redis.close()
            self.redis = None
            
    async def get(self, key: str) -> Optional[str]:
        """Получение значения по ключу"""
        if not self.redis:
            raise RuntimeError("Redis isn't connected!")
        
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = None) -> bool:
        """Установка значения по ключу."""
        if not self.redis:
            raise RuntimeError("Redis isn't connected!")
        
        result = await self.redis.set(key, value, ex=expire)
        return bool(result)

    async def delete(self, key: str) -> bool:
        """Удаление элемента по ключу."""
        if not self.redis:
            raise RuntimeError("Redis isnt connected!")
        
        removed = self.redis.delete(key)
        return removed > 0