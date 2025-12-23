import asyncio
import logging
from datetime import datetime, time
import pytz
from typing import Optional

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(
        self,
        user_repository,
        digest_repository,
        telegram_bot,
        digest_delivery_uc,
        check_interval: int = 60
    ):
        self.user_repo = user_repository
        self.digest_repo = digest_repository
        self.bot = telegram_bot
        self.digest_delivery_uc = digest_delivery_uc
        self.check_interval = check_interval
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
    def _parse_digest_time(self, time_str: str) -> Optional[time]:
        try:
            hour, minute = map(int, time_str.split(":"))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return time(hour, minute)
        except (ValueError, AttributeError):
            pass
        return None
    
    def _get_user_timezone(self, timezone_str: str) -> pytz.timezone:
        try:
            return pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            return pytz.timezone("Europe/Moscow")
    
    def _is_digest_time(self, user_time: time, now: datetime) -> bool:
        return (
            now.hour == user_time.hour and 
            now.minute == user_time.minute and
            now.second < 30
        )
    
    async def check_and_send_digests(self):
        logger.debug("Проверка времени для отправки дайджестов...")
        
        try:
            users = await self.user_repo.get_all()
            logger.debug(f"Найдено {len(users)} пользователей для проверки")
            
            for user in users:
                try:
                    settings = user.settings or {}
                    
                    if not user.can_receive_digest():
                        logger.debug(f"Пользователь {user.telegram_id} отключил дайджесты")
                        continue
                    
                    digest_time_str = settings.get("digest_time", "20:00")
                    digest_time = self._parse_digest_time(digest_time_str)
                    
                    if not digest_time:
                        logger.warning(f"Неверный формат времени у пользователя {user.telegram_id}: {digest_time_str}")
                        continue
                    
                    timezone_str = settings.get("timezone", "Europe/Moscow")
                    user_tz = self._get_user_timezone(timezone_str)
                    
                    now = datetime.now(user_tz)
                    
                    if self._is_digest_time(digest_time, now):
                        logger.info(f"Отправка дайджеста пользователю {user.telegram_id} в {digest_time_str} ({timezone_str})")
                        
                        success = await self.digest_delivery_uc.execute(user.telegram_id)
                        
                        if success:
                            logger.info(f"Дайджест успешно отправлен пользователю {user.telegram_id}")
                        else:
                            logger.warning(f"Не удалось отправить дайджест пользователю {user.telegram_id}")
                            
                except Exception as e:
                    logger.error(f"Ошибка при обработке пользователя {user.telegram_id}: {e}", exc_info=True)
                    
        except Exception as e:
            logger.error(f"Критическая ошибка в планировщике: {e}", exc_info=True)
    
    async def run_once(self):
        await self.check_and_send_digests()
    
    async def _run_loop(self):
        self.is_running = True
        logger.info(f"Планировщик запущен. Интервал проверки: {self.check_interval} секунд")
        
        while self.is_running:
            try:
                await self.check_and_send_digests()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                logger.info("Планировщик остановлен (CancelledError)")
                break
            except Exception as e:
                logger.error(f"Ошибка в основном цикле планировщика: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)
    
    async def start(self):
        if self.is_running:
            logger.warning("Планировщик уже запущен")
            return
        
        self.task = asyncio.create_task(self._run_loop())
        return self.task
    
    async def stop(self):
        if not self.is_running:
            logger.warning("Планировщик уже остановлен")
            return
        
        self.is_running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        
        logger.info("Планировщик остановлен")
    
    def get_status(self) -> dict:
        return {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "task_active": self.task is not None and not self.task.done()
        }