from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class ITelegramBot(ABC):
    """Интерфейс Telegram бота"""
    
    @abstractmethod
    async def start(self) -> None:
        """Запустить бота и начать прослушивание сообщений"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Остановить бота и освободить ресурсы"""
        pass
    
    @abstractmethod
    async def send_message(self, chat_id: int, text: str, **kwargs) -> bool:
        """Отправить текстовое сообщение пользователю/чату"""
        pass
    
    @abstractmethod
    async def send_digest(self, user_id: int, digest_content: str) -> bool:
        """Отправить дайджест пользователю"""
        pass
    
    @abstractmethod
    async def setup_commands(self) -> None:
        """Настроить меню команд бота"""
        pass

class TelegramBot(ITelegramBot):
    """Реализация Telegram бота"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.is_running = False
    
    async def start(self) -> None:
        # TODO: Инициализировать бота, зарегистрировать обработчики, запустить поллинг
        self.is_running = True
    
    async def stop(self) -> None:
        # TODO: Остановить бота, закрыть сессии
        self.is_running = False
    
    async def send_message(self, chat_id: int, text: str, **kwargs) -> bool:
        # TODO: Реализовать отправку сообщения
        return True
    
    async def send_digest(self, user_id: int, digest_content: str) -> bool:
        # TODO: Реализовать форматирование и отправку дайджеста
        return await self.send_message(user_id, digest_content)
    
    async def setup_commands(self) -> None:
        # TODO: Зарегистрировать команды /start, /subscribe, /settings
        pass