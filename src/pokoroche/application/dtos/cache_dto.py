class CacheItem:
    """Элемент кеша"""
    
    def __init__(self, key: str, value: any, ttl: int):
        self.key = key
        self.value = value
        self.ttl = ttl  # время жизни в секундах
    
    def is_valid(self) -> bool:
        """Проверить, не истек ли срок действия"""
        # TODO: Реализовать проверку срока действия
        raise NotImplementedError("Реализуйте is_valid")