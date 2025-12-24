import asyncio

from src.pokoroche.commands.start_cmd import StartCommand
from src.pokoroche.commands.settings_cmd import SettingsCommand
from src.pokoroche.commands.digest_cmd import DigestCommand
from src.pokoroche.commands.subscribe_cmd import SubscribeCommand


class FakeBot:
    async def send_message(self, chat_id: int, text: str, **kwargs):
        print(f"[send_message chat_id={chat_id}] {text}")


class InMemoryUserRepo:
    def __init__(self):
        self._users = {}

    async def find_by_telegram_id(self, telegram_id):
        return self._users.get(int(telegram_id))

    async def insert(self, user):
        tid = getattr(user, "telegram_id", None)
        if tid is None and isinstance(user, dict):
            tid = user.get("telegram_id")
        if tid is not None:
            self._users[int(tid)] = user

    async def update(self, user):
        await self.insert(user)


class StubDigestDelivery:
    async def execute(self, user_id):
        return "Тестовый дайджест"


class StubTopicService:
    async def list_available_topics(self):
        return []


async def main():
    bot = FakeBot()
    repo = InMemoryUserRepo()

    start = StartCommand(bot, repo)
    settings = SettingsCommand(repo)
    digest = DigestCommand(StubDigestDelivery())
    subscribe = SubscribeCommand(bot, repo, StubTopicService())

    user_id = 1
    chat_id = 1

    async def call(cmd, text):
        msg = {"text": text, "chat": {"id": chat_id}, "from": {"id": user_id}}
        out = await cmd.handle(user_id, msg)
        print(text, "->", out)

    await call(start, "/start")
    await call(subscribe, "/subscribe")
    await call(subscribe, "/subscribe add test")
    await call(subscribe, "/subscribe")
    await call(subscribe, "/subscribe remove test")
    await call(subscribe, "/subscribe")
    await call(settings, "/settings")
    await call(digest, "/digest")


asyncio.run(main())
