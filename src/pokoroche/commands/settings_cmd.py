from typing import Dict, Any


class SettingsCommand:
    """Обработчик команды /settings"""

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def check_time_hhmm(self, value: str) -> bool:
        """Проверка формата HH:MM"""
        if not isinstance(value, str):
            return False
        value = value.strip()
        if len(value) != 5 or value[2] != ":":
            return False
        hh = value[:2]
        mm = value[3:]
        if not (hh.isdigit() and mm.isdigit()):
            return False
        h = int(hh)
        m = int(mm)
        return 0 <= h <= 23 and 0 <= m <= 59

    async def handle(self, user_id: int, message: Dict[str, Any]) -> str:
        """Обработчик /settings."""

        text = message.get("text") or ""
        if not isinstance(text, str):
            return "Команда /settings"

        parts = text.split()
        if not parts:
            return "Команда /settings"

        user = await self.user_repository.find_by_telegram_id(user_id)
        if user is None:
            return "Нажми /start, чтобы я тебя зарегистрировал."

        settings = user.settings if isinstance(user.settings, dict) else {}
        digest_time = settings.get("digest_time", "20:00")
        detail_level = settings.get("detail_level", "brief")
        timezone = settings.get("timezone", "Europe/Moscow")

        # /settings
        if len(parts) == 1:
            return (
                "Твои настройки:\n"
                f"• Время дайджеста: {digest_time}\n"
                f"• Детализация: {detail_level}\n\n"
                f"• Часовой пояс: {timezone}\n\n"
                "Команды:\n"
                "/settings time HH:MM\n"
                "/settings detail brief/full\n"
            )

        # /settings time HH:MM
        if len(parts) == 3 and parts[1].lower() == "time":
            new_time = parts[2].strip()
            if not self.check_time_hhmm(new_time):
                return "Неверный формат. Пример: /settings time 20:00"

            user.update_settings(digest_time=new_time)
            await self.user_repository.update(user)
            return f"Новое время дайджеста: {new_time}"

        # /settings detail brief/full
        if len(parts) == 3 and parts[1].lower() == "detail":
            new_level = parts[2].strip().lower()
            if new_level not in ("brief", "full"):
                return "Неверный формат. Варианты: brief или full"
            user.update_settings(detail_level=new_level)
            await self.user_repository.update(user)
            return f"Новая детализация: {new_level}"

        return (
            "Неверный формат команды.\n\n"
            "Доступные команды:\n"
            "/settings - показать настройки\n"
            "/settings time HH:MM\n"
            "/settings detail brief|full\n"
        )
