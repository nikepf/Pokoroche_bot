import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pokoroche.infrastructure.config.config import load_config
from src.pokoroche.infrastructure.database.database import Database
from src.pokoroche.adapters.telegram_bot import TelegramBot
from src.pokoroche.adapters.fake_ml_client import FakeMLClient
from src.pokoroche.adapters.redis_client import RedisClient
from src.pokoroche.domain.services.importance_service import ImportanceService
from src.pokoroche.domain.services.topic_service import TopicService
from src.pokoroche.commands.start_cmd import StartCommand
from src.pokoroche.commands.subscribe_cmd import SubscribeCommand
from src.pokoroche.commands.stats_cmd import StatsCommand
from src.pokoroche.commands.settings_cmd import SettingsCommand
from src.pokoroche.commands.digest_cmd import DigestCommand
from src.pokoroche.commands.message_handler import MessageHandler
from src.pokoroche.commands.feedback_handler import FeedbackHandler
from src.pokoroche.application.use_cases.user_registration import UserRegistrationUseCase
from src.pokoroche.application.use_cases.user_registration import DigestDeliveryUseCase
from src.pokoroche.infrastructure.scheduler import Scheduler

class FakeMLClient:
    async def analyze_importance(self, text: str, context=None):
        return 0.8

    async def extract_topics(self, text: str):
        topics = ["тест"]
        if not text:
            return topics

        text_lower = text.lower()
        if any(word in text_lower for word in ["математик", "алгебр", "геометр"]):
            topics.append("математика")
        if any(word in text_lower for word in ["программир", "код", "python"]):
            topics.append("программирование")
        if any(word in text_lower for word in ["учеб", "лекци", "занят"]):
            topics.append("учеба")
        return topics

    async def health_check(self):
        return True


class Scheduler:
    def __init__(self, user_repository, digest_repository, telegram_bot, digest_delivery_uc):
        self.user_repo = user_repository
        self.digest_repo = digest_repository
        self.bot = telegram_bot
        self.digest_delivery_uc = digest_delivery_uc
        self.is_running = False
        self.check_interval = 60

    async def check_and_send_digests(self):
        try:
            users = await self.user_repo.get_all()

            for user in users:
                try:
                    settings = user.settings or {}
                    if not user.can_receive_digest():
                        continue
                    await self.digest_delivery_uc.execute(user.telegram_id)
                except Exception as e:
                    logging.error(f"Ошибка при обработке пользователя {user.telegram_id}: {e}")

        except Exception as e:
            logging.error(f"Ошибка в планировщике: {e}")

    async def run(self):
        self.is_running = True
        logging.info("Планировщик запущен")

        while self.is_running:
            try:
                await self.check_and_send_digests()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Ошибка в планировщике: {e}")
                await asyncio.sleep(self.check_interval)

    async def stop(self):
        self.is_running = False
        logging.info("Планировщик остановлен")


class Application:
    def __init__(self):
        self.config = load_config()
        self.db = None
        self.redis = None
        self.bot = None
        self.scheduler = None

    async def setup_database(self):
        logging.info("Инициализация базы данных...")
        
        db_url = self.config.database.database_url
        if not db_url:
            logging.error("DATABASE_URL не задан в конфигурации")
            sys.exit(1)
            
        logging.info(f"Подключение к БД: {db_url.split('@')[1] if '@' in db_url else db_url}")
        self.db = Database(db_url)
        await self.db.connect()
        await self.db.create_tables()
        logging.info("База данных подключена")

    async def setup_redis(self):
        logging.info("Инициализация Redis...")
        self.redis = RedisClient(self.config.redis.redis_url)
        await self.redis.connect()
        logging.info("Redis подключен")

    async def setup_ml_client(self):
        logging.info("Инициализация ML клиента...")
        self.ml_client = FakeMLClient()
        logging.info("ML клиент инициализирован")

    async def setup_services(self):
        logging.info("Инициализация сервисов...")
        self.importance_service = ImportanceService(self.ml_client)
        self.topic_service = TopicService(self.ml_client)
        logging.info("Сервисы инициализированы")

    async def setup_bot(self):
        logging.info("Инициализация Telegram бота...")
        self.bot = TelegramBot(self.config.bot.bot_token)

        async with self.db.get_repositories() as (user_repo, message_repo, digest_repo):
            user_registration_uc = UserRegistrationUseCase(user_repo, self.bot)
            digest_delivery_uc = DigestDeliveryUseCase(user_repo, digest_repo, self.bot)

            start_cmd = StartCommand(self.bot, user_repo)
            subscribe_cmd = SubscribeCommand(user_repo, self.topic_service)
            stats_cmd = StatsCommand(user_repo, digest_repo)
            settings_cmd = SettingsCommand(user_repo)
            digest_cmd = DigestCommand(digest_delivery_uc)

            self.bot.register_handler("/start", start_cmd.handle)
            self.bot.register_handler("/subscribe", subscribe_cmd.handle)
            self.bot.register_handler("/stats", stats_cmd.handle)
            self.bot.register_handler("/settings", settings_cmd.handle)
            self.bot.register_handler("/digest", digest_cmd.handle)

            message_handler = MessageHandler(
                message_repository=message_repo,
                importance_service=self.importance_service,
                topic_service=self.topic_service
            )

            feedback_handler = FeedbackHandler(
                telegram_bot=self.bot,
                digest_repository=digest_repo,
                feedback_service=None
            )

            self.bot.register_message_handler(message_handler.handle)
            self.bot.register_feedback_handler(feedback_handler.handle)

            self.scheduler = Scheduler(user_repo, digest_repo, self.bot, digest_delivery_uc)

        logging.info("Бот инициализирован")

    async def run(self):
        logging.info("Запуск Pokoroche бота...")

        try:
            await self.setup_database()
            await self.setup_redis()
            await self.setup_ml_client()
            await self.setup_services()
            await self.setup_bot()

            logging.info("Все компоненты инициализированы")
            logging.info("Запуск бота и планировщика...")

            scheduler_task = asyncio.create_task(self.scheduler.run())
            await self.bot.start()

        except KeyboardInterrupt:
            logging.info("Получен сигнал прерывания...")
        except Exception as e:
            logging.error(f"Ошибка при запуске: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.shutdown()

    async def shutdown(self):
        logging.info("Завершение работы...")

        if self.bot:
            await self.bot.stop()

        if self.scheduler:
            await self.scheduler.stop()

        if self.redis:
            await self.redis.disconnect()

        if self.db:
            await self.db.disconnect()

        logging.info("Работа завершена")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    app = Application()

    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\nОстановлено пользователем")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
