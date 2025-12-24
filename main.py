import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

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
        k = self._key(user)
        if k is not None:
            self._users[k] = user


class Application:
    def __init__(self):
        self.config = None
        self.db = None
        self.redis = None
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

        stub_digest = StubDigestDelivery()
        stub_topic_service = StubTopicService()

        start_handler = StartCommand(self.bot, user_repo)
        settings_handler = SettingsCommand(user_repo)
        digest_handler = DigestCommand(stub_digest)
        subscribe_handler = SubscribeCommand(self.bot, user_repo, stub_topic_service)

        self.bot.register_handler("/start", start_handler.handle)
        self.bot.register_handler("/settings", settings_handler.handle)
        self.bot.register_handler("/digest", digest_handler.handle)
        self.bot.register_handler("/subscribe", subscribe_handler.handle)

        logger.info("Бот инициализирован")

    async def run(self):
        try:
            self.config = load_config()
            logger.info("Конфигурация загружена")

            if not self.config.bot.token:
                logger.error("BOT_TOKEN не задан!")
                return

            logger.info(f"Токен бота: {self.config.bot.token[:10]}...")

            await self.setup_database()
            await self.setup_redis()
            await self.setup_bot()

            logger.info("Все компоненты инициализированы")
            logger.info("Запуск бота...")

            await self.bot.start()

        except Exception as e:
            logger.error(f"Ошибка при запуске: {e}")
            import traceback

            traceback.print_exc()

    async def shutdown(self):
        logger.info("Завершение работы...")
        if self.bot:
            await self.bot.stop()
        logger.info("Работа завершена")


def main():
    logger.info("Запуск Pokoroche бота...")

    app = Application()

    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.info("Остановлено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
