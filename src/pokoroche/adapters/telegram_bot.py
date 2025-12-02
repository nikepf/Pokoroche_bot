from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import aiohttp
import asyncio


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

        self.session: Optional[aiohttp.ClientSession] = None
        self.handlers: Dict[str, Any] = {}  # словарь команд бота
        self.update_offset: int = 0  # указатель "с какого сообщения читать дальше"

    def register_handler(self, command: str, handler) -> None:
        """Подключение команды"""
        self.handlers[command] = handler

    def api_url(self, method: str) -> str:
        """Собирает URL Telegram Bot API для указанного метода"""
        return f"https://api.telegram.org/bot{self.bot_token}/{method}"

    async def ensure_session(self):
        """Создаёт и возвращает aiohttp-сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def post(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Отправляет POST-запрос в Telegram API"""
        session = await self.ensure_session()
        async with session.post(self.api_url(method), json=payload) as response:
            return await response.json(content_type=None)

    async def start(self) -> None:
        await self.ensure_session()
        await self.setup_commands()
        self.is_running = True

        while self.is_running:
            try:
                data = await self.post(
                    "getUpdates",
                    {
                        "offset": self.update_offset,
                        "timeout": 25,
                        "allowed_updates": ["message"],
                    },
                )
                if data.get("ok") is not True:
                    continue

                updates = data.get("result", [])  # новые сообщения
                for upd in updates:
                    upd_id = upd.get("update_id")
                    if isinstance(upd_id, int):
                        self.update_offset = upd_id + 1

                    msg = upd.get("message")
                    if not isinstance(msg, dict):
                        continue

                    text = msg.get("text") or ""
                    if not isinstance(text, str) or not text.startswith("/"):  # если начинается не c / => пропускаем
                        continue

                    chat = msg.get("chat") if isinstance(msg.get("chat"), dict) else {}
                    from_user = msg.get("from") if isinstance(msg.get("from"), dict) else {}

                    chat_id = chat.get("id")
                    user_id = from_user.get("id")

                    if not isinstance(chat_id, int) or not isinstance(user_id, int):
                        continue

                    command = text.split()[0].split("@")[0]  # /start@botname => /start; /start => /start
                    handler = self.handlers.get(command)
                    if handler is None:
                        continue

                    reply = await handler(user_id, msg)

                    if isinstance(reply, str) and reply:
                        await self.send_message(chat_id, reply)

            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)

    async def stop(self) -> None:
        self.is_running = False
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = None

    async def send_message(self, chat_id: int, text: str, **kwargs) -> bool:
        payload = {"chat_id": chat_id, "text": text, **kwargs}
        data = await self.post("sendMessage", payload)
        if data.get("ok") is True:
            return True
        return False

    async def send_digest(self, user_id: int, digest_content: str) -> bool:
        header = "📃 Дайджест за 24 часа\n\n"
        full_text = header + (digest_content or "")
        max_len = 4096

        parts = []
        while full_text:
            parts.append(full_text[:max_len])
            full_text = full_text[max_len:]

        for part in parts:
            ok = await self.send_message(user_id, part)
            if not ok:
                return False
        return True

    async def setup_commands(self) -> None:
        commands = [
            {"command": "start", "description": "Первоначальная настройка"},
            {"command": "subscribe", "description": "Выбрать темы и ключевые слова"},
            {"command": "settings", "description": "Настройка дайджестов"},
        ]
        await self.post("setMyCommands", {"commands": commands})
