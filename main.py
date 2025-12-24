import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pokoroche.infrastructure.config.config import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class InMemoryUserRepo:
    def __init__(self):
        self._users = {}

    def _key(self, user):
        if isinstance(user, dict):
            for k in ("telegram_id", "user_id", "id"):
                v = user.get(k)
                if v is not None:
                    return int(v)
            return None
        for attr in ("telegram_id", "user_id", "id"):
            v = getattr(user, attr, None)
            if v is not None:
                return int(v)
        return None

    async def find_by_telegram_id(self, telegram_id):
        return self._users.get(int(telegram_id))

    async def insert(self, user):
        k = self._key(user)
        if k is not None:
            self._users[k] = user

    async def update(self, user):
        await self.insert(user)

    async def create(self, user):
        await self.insert(user)

    async def save(self, user):
        await self.insert(user)

    async def add(self, user):
        await self.insert(user)

    async def upsert(self, user):
        await self.insert(user)


class Application:
    def __init__(self):
        self.config = None
        self.bot = None

    async def setup_database(self):
        logger.info("Инициализация базы данных...")
        logger.info(f"Подключение к БД: {self.config.database.url}")

    async def setup_redis(self):
        logger.info("Инициализация Redis...")
        logger.info(f"Подключение к Redis: {self.config.redis.url}")

    async def setup_bot(self):
        logger.info("Инициализация Telegram бота...")

        from src.pokoroche.adapters.telegram_bot import TelegramBot
        from src.pokoroche.commands.start_cmd import StartCommand
        from src.pokoroche.commands.settings_cmd import SettingsCommand
        from src.pokoroche.commands.digest_cmd import DigestCommand
        from src.pokoroche.commands.subscribe_cmd import SubscribeCommand

        self.bot = TelegramBot(self.config.bot.token)

        user_repo = InMemoryUserRepo()

        class StubDigestDelivery:
            async def execute(self, user_id):
                return True

        class StubTopicService:
            async def list_available_topics(self):
                return []

        start_cmd = StartCommand(self.bot, user_repo)
        settings_cmd = SettingsCommand(user_repo)
        digest_cmd = DigestCommand(StubDigestDelivery())
        subscribe_cmd = SubscribeCommand(user_repository=user_repo, topic_service=StubTopicService())

        async def start_handler(user_id, msg):
            reply = await start_cmd.handle(user_id, msg)
            existing = await user_repo.find_by_telegram_id(user_id)
            if existing is None:
                await user_repo.insert({"telegram_id": user_id, "settings": {"topics": []}})
            return reply

        self.bot.register_handler("/start", start_handler)
        self.bot.register_handler("/settings", settings_cmd.handle)
        self.bot.register_handler("/digest", digest_cmd.handle)
        self.bot.register_handler("/subscribe", subscribe_cmd.handle)

        logger.info("Бот инициализирован")

    async def run(self):
        self.config = load_config()
        logger.info("Конфигурация загружена")
        logger.info(f"Токен бота: {self.config.bot.token[:10]}...")

        await self.setup_database()
        await self.setup_redis()
        await self.setup_bot()

        logger.info("Все компоненты инициализированы")
        logger.info("Запуск бота...")
        await self.bot.start()


def main():
    logger.info("Запуск Pokoroche бота...")
    asyncio.run(Application().run())


if name == "__main__":
    main()