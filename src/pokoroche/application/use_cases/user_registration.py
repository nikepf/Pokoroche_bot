from typing import Dict, Any

from src.pokoroche.domain.models.user import UserEntity
from datetime import datetime, timezone, timedelta

DEFAULT_SETTINGS = {
    "digest_time": "20:00",
    "detail_level": "brief",
    "timezone": "Europe/Moscow",
}


class UserRegistrationUseCase:
    """Регистрация и управление пользователями"""

    def __init__(self, user_repository, telegram_bot):
        self.user_repository = user_repository
        self.telegram_bot = telegram_bot

    async def execute(self, telegram_id: int, user_data: Dict[str, Any]) -> bool:
        """
        Зарегистрировать нового пользователя или обновить существующего
        """
        user = await self.user_repository.find_by_telegram_id(telegram_id)
        # TODO: Реализовать find_by_telegram_id: поиск пользователя по telegram_id
        if user is None:
            new_user = UserEntity(
                telegram_id=telegram_id,
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
            )

            # TODO: Реализовать insert: добавление  пользователя в БД
            await self.user_repository.insert(new_user)
            return True
        else:
            if user_data.get("username") is not None:
                user.username = user_data["username"]
            if user_data.get("first_name") is not None:
                user.first_name = user_data["first_name"]
            if user_data.get("last_name") is not None:
                user.last_name = user_data["last_name"]
            current_settings = user.settings if isinstance(user.settings, dict) else {}
            missing = {key: value for key, value in DEFAULT_SETTINGS.items() if key not in current_settings}
            if missing:
                user.update_settings(**missing)
            await self.user_repository.update(user)
            # TODO: Реализовать update: сохранение в БД изменений существующего пользователя
            return True


# TODO: кол-во пункт дайджеста - можно будет поменять
BRIEF_LIMIT = 5
FULL_LIMIT = 15


class DigestDeliveryUseCase:
    """Формирование и доставка дайджестов"""

    def __init__(self, user_repository, digest_repository, telegram_bot):
        self.user_repository = user_repository
        self.digest_repository = digest_repository
        self.telegram_bot = telegram_bot

    async def execute(self, user_id: int) -> bool:
        """
        Сформировать и отправить дайджест пользователю
        """
        user = await self.user_repository.find_by_telegram_id(user_id)
        if user is None:
            return False
        if not user.can_receive_digest():
            return False
        detail_level = (user.settings or {}).get("detail_level", "brief")
        topics = (user.settings or {}).get("topics", [])

        from_time = datetime.now(timezone.utc) - timedelta(hours=24)
        items = await self.digest_repository.get_important_items(
            telegram_id=user.telegram_id,
            from_time=from_time,
            topics=topics,
        )
        # TODO: Реализовать get_important_items: должен вернуть важные сообщение за период from_time
        if not items:
            return True

        if detail_level == "brief":
            limit = BRIEF_LIMIT
        else:
            limit = FULL_LIMIT

        lines = []
        count = 0
        for item in items:
            if count >= limit:
                break
            lines.append("• " + str(item))  # TODO: форматирование можно будет поменять
            count += 1
        text = "\n".join(lines)

        await self.telegram_bot.send_digest(user.telegram_id, text)

        # TODO: реализовать save_delivery - Сохранить запись об отправленном дайджесте
        await self.digest_repository.save_delivery(
            telegram_id=user.telegram_id,
            from_time=from_time,
            sent_at=datetime.now(timezone.utc),
            items_count=count,
            digest=text,
        )
        return True
