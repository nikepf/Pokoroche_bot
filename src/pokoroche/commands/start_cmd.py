from typing import Dict, Any
from src.pokoroche.application.use_cases.user_registration import UserRegistrationUseCase


class StartCommand:
    """Обработчик команды /start"""

    def __init__(self, telegram_bot, user_repository):
        self.telegram_bot = telegram_bot
        self.user_repository = user_repository
        # регестрирует пользователя: проверяет пользователя в БД, создаёт/обновляет и ставит дефолтные настройки
        self.user_registration_uc = UserRegistrationUseCase(
            user_repository=user_repository,
            telegram_bot=telegram_bot,
        )

    async def handle(self, user_id: int,
                     message: Dict[str, Any]) -> str:
        """
        Обработать команду /start
        """
        from_user = message.get("from") or {}
        user_data = {
            "username": from_user.get("username"),
            "first_name": from_user.get("first_name"),
            "last_name": from_user.get("last_name"),
        }

        await self.user_registration_uc.execute(user_id, user_data)
        # TODO: приветсвенное сообщение можно бубет поменять
        return (
            "Привет! Я бот Pokoroche.\n\n"
            "Меня добавляют в групповые чаты - я анализирую упоминания и теги, "
            "отфильтровываю шум и раз в день присылаю тебе краткую сводку самого важного.\n\n"
            "Доступные команды:\n"
            "/start - первоначальная настройка\n"
            "/subscribe - выбрать интересующие темы и ключевые слова\n"
            "/settings - время дайджеста и уровень детализации\n"
        )
