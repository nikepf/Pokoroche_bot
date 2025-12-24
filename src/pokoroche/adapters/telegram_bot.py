from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import aiohttp
import asyncio


class ITelegramBot(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def send_message(self, chat_id: int, text: str, **kwargs) -> bool:
        pass

    @abstractmethod
    async def send_digest(self, user_id: int, digest_content: str) -> bool:
        pass

    @abstractmethod
    async def setup_commands(self) -> None:
        pass

    @abstractmethod
    async def answer_callback_query(self, callback_query_id: str, **kwargs) -> bool:
        pass


class TelegramBot(ITelegramBot):
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.is_running = False
        self.session: Optional[aiohttp.ClientSession] = None
        self.handlers: Dict[str, Any] = {}
        self.update_offset: int = 0
        self.message_handler = None
        self.feedback_handler = None

    def register_handler(self, command: str, handler) -> None:
        self.handlers[command] = handler

    def register_message_handler(self, handler) -> None:
        self.message_handler = handler

    def register_feedback_handler(self, handler) -> None:
        self.feedback_handler = handler

    def api_url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.bot_token}/{method}"

    async def ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def post(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        session = await self.ensure_session()
        async with session.post(self.api_url(method), json=payload) as response:
            return await response.json(content_type=None)

    async def answer_callback_query(self, callback_query_id: str, **kwargs) -> bool:
        payload = {"callback_query_id": callback_query_id, **kwargs}
        data = await self.post("answerCallbackQuery", payload)
        return data.get("ok") is True

    async def start(self) -> None:
        await self.ensure_session()
        await self.post("deleteWebhook", {"drop_pending_updates": True})
        await self.setup_commands()
        self.is_running = True

        while self.is_running:
            try:
                data = await self.post(
                    "getUpdates",
                    {
                        "offset": self.update_offset,
                        "timeout": 25,
                        "allowed_updates": ["message", "callback_query"],
                    },
                )
                if data.get("ok") is not True:
                    print("getUpdates error:", data)
                    await asyncio.sleep(1)
                    continue

                updates = data.get("result", [])
                for upd in updates:
                    upd_id = upd.get("update_id")
                    if isinstance(upd_id, int):
                        self.update_offset = upd_id + 1

                    cb = upd.get("callback_query")
                    if isinstance(cb, dict):
                        if self.feedback_handler is not None:
                            await self.feedback_handler(cb)
                        cb_id = cb.get("id")
                        if isinstance(cb_id, str):
                            await self.answer_callback_query(cb_id)
                        continue

                    msg = upd.get("message")
                    if not isinstance(msg, dict):
                        continue

                    text = msg.get("text") or ""
                    chat = msg.get("chat") if isinstance(msg.get("chat"), dict) else {}
                    from_user = msg.get("from") if isinstance(msg.get("from"), dict) else {}

                    chat_id = chat.get("id")
                    user_id = from_user.get("id")

                    if not isinstance(chat_id, int) or not isinstance(user_id, int):
                        continue

                    if isinstance(text, str) and text.startswith("/"):
                        command = text.split()[0].split("@")[0]
                        handler = self.handlers.get(command)
                        if handler is None:
                            continue
                        reply = await handler(user_id, msg)
                        if isinstance(reply, str) and reply:
                            await self.send_message(chat_id, reply)
                    else:
                        if self.message_handler is not None and isinstance(text, str) and text.strip():
                            await self.message_handler(user_id, chat_id, text, msg)

            except asyncio.CancelledError:
                break
            except Exception:
                import traceback

                traceback.print_exc()
                await asyncio.sleep(1)

    async def stop(self) -> None:
        self.is_running = False
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = None

    async def send_message(self, chat_id: int, text: str, **kwargs) -> bool:
        payload = {"chat_id": chat_id, "text": text, **kwargs}
        data = await self.post("sendMessage", payload)
        if data.get("ok") is not True:
            print("sendMessage error:", data)
        return data.get("ok") is True

    async def send_digest(self, user_id: int, digest_content: str) -> bool:
        header = "📃 Дайджест за 24 часа\n\n"
        full_text = header + (digest_content or "")
        max_len = 4096

        parts = []
        while full_text:
            parts.append(full_text[:max_len])
            full_text = full_text[max_len:]

        last_message_id: Optional[int] = None

        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                data = await self.post("sendMessage", {"chat_id": user_id, "text": part})
                if data.get("ok") is not True:
                    print("sendMessage error:", data)
                    return False
                result = data.get("result") or {}
                mid = result.get("message_id")
                if isinstance(mid, int):
                    last_message_id = mid
            else:
                ok = await self.send_message(user_id, part)
                if not ok:
                    return False

        if last_message_id is not None:
            reply_markup = {
                "inline_keyboard": [
                    [
                        {"text": "👍", "callback_data": f"feedback:{last_message_id}:1"},
                        {"text": "👎", "callback_data": f"feedback:{last_message_id}:0"},
                    ]
                ]
            }
            await self.post(
                "editMessageReplyMarkup",
                {"chat_id": user_id, "message_id": last_message_id, "reply_markup": reply_markup},
            )

        return True

    async def setup_commands(self) -> None:
        commands = [
            {"command": "start", "description": "Первоначальная настройка"},
            {"command": "subscribe", "description": "Выбрать темы и ключевые слова"},
            {"command": "stats", "description": "Статистика"},
            {"command": "settings", "description": "Настройка дайджестов"},
            {"command": "digest", "description": "Получить дайджест сейчас"},
        ]
        data = await self.post("setMyCommands", {"commands": commands})
        if data.get("ok") is not True:
            print("setMyCommands error:", data)
