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

    @abstractmethod
    async def rpush(self, key: str, value: str) -> int:
        """Добавить элемент в конец очереди"""
        pass
    
    @abstractmethod
    async def lpop(self, key: str) -> Optional[str]:
        """Взять элемент из начала очереди"""
        pass
    
    @abstractmethod
    async def llen(self, key: str) -> int:
        """Получить размер очереди (количество элементов)"""
        pass

class RedisClient(IRedisClient):
    """Реализация Redis клиента"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None
    
    def _check_connection(self) -> None:
        if not self.redis:
            raise RuntimeError("Redis isn't connected!")

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
        self._check_connection()
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = None) -> bool:
        """Установка значения по ключу."""
        self._check_connection()
        
        result = await self.redis.set(key, value, ex=expire)
        return bool(result)

    async def delete(self, key: str) -> bool:
        """Удаление элемента по ключу."""
        self._check_connection()
        
        removed = await self.redis.delete(key)
        return removed > 0
    
    async def rpush(self, key: str, value: str) -> int:
        """Добавить элемент в конец очереди"""
        self._check_connection()
        return await self.redis.rpush(key, value)
    
    async def lpop(self, key: str) -> Optional[str]:
        """Взять элемент из начала очереди"""
        self._check_connection()
        return await self.redis.lpop(key)
    
    async def llen(self, key: str) -> int:
        """Получить размер очереди (количество элементов)"""
        self._check_connection()
        return await self.redis.llen(key)