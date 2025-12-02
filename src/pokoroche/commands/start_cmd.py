from typing import Dict, Any
from src.pokoroche.domain.models.user import UserEntity


class StartCommand:
    """Обработчик команды /start"""

    def __init__(self, telegram_bot, user_repository):
        self.telegram_bot = telegram_bot
        self.user_repository = user_repository

    async def handle(self, user_id: int,
                     message: Dict[str, Any]) -> str:
        """
        Обработать команду /start
        """
        # TODO: Реализовать find_by_telegram_id: поиск пользователя по telegram_id
        user = await self.user_repository.find_by_telegram_id(user_id)
        if user is None:
            from_user = message.get("from") or {}
            username = from_user.get("username")
            first_name = from_user.get("first_name")
            last_name = from_user.get("last_name")
            new_user = UserEntity(
                telegram_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            await self.user_repository.insert(new_user)
            # settings по умолчанию задаются default в UserEntity.settings

        # TODO: приветсвенное сообщение можно бубет поменять
        return (
            "Привет! Я бот Pokoroche.\n\n"
            "Меня добавляют в групповые чаты - я анализирую упоминания и теги, "
            "отфильтровываю шум и раз в день присылаю тебе краткую сводку самого важного.\n\n"
            "Доступные команды:\n"
            "/start — первоначальная настройка\n"
            "/subscribe — выбрать интересующие темы и ключевые слова\n"
            "/settings — время дайджеста и уровень детализации\n"
        )
