from typing import Optional
import json

class MessageQueue:
    """Очередь сообщений для асинхронной обработки"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def push(self, queue_name: str, message_data: dict) -> bool:
        """Добавить сообщение в очередь"""
        message_json = json.dumps(message_data)
        await self.redis.rpush(queue_name, message_json)
        return True
    
    async def pop(self, queue_name: str) -> Optional[dict]:
        """Взять сообщение из очереди"""
        message = await self.redis.lpop(queue_name)
        if message is None:
            return None
        return json.loads(message)
