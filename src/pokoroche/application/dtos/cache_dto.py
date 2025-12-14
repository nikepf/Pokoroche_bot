import time

class CacheItem:
    """Элемент кеша"""
    
    def __init__(self, key: str, value: any, ttl: int):
        self.key = key
        self.value = value
        self.ttl = ttl  # время жизни в секундах
        self.created_at = time.time() #время создания кеша
    
    def is_valid(self) -> bool:
        """Проверить, не истек ли срок действия"""
        if self.ttl is None:
            return True
        return (time.time() - self.created_at) < self.ttl
    