class SubscribeCommand:
    def __init__(self, bot, user_repository, topic_service):
        self.bot = bot
        self.user_repository = user_repository
        self.topic_service = topic_service

    def _normalize(self, s: str) -> str:
        return " ".join((s or "").strip().lower().split())

    def _get_settings(self, user):
        if isinstance(user, dict):
            s = user.get("settings")
            return s if isinstance(s, dict) else {}
        s = getattr(user, "settings", None)
        return s if isinstance(s, dict) else {}

    def _set_topics(self, user, topics):
        if isinstance(user, dict):
            user.setdefault("settings", {})
            if not isinstance(user["settings"], dict):
                user["settings"] = {}
            user["settings"]["topics"] = topics
            return
        if hasattr(user, "update_settings") and callable(getattr(user, "update_settings")):
            user.update_settings(topics=topics)
            return
        s = getattr(user, "settings", None)
        if isinstance(s, dict):
            s["topics"] = topics
            return
        setattr(user, "settings", {"topics": topics})

    async def handle(self, user_id: int, message) -> str:
        if not isinstance(message, dict):
            return "Некорректное сообщение"

        text = str(message.get("text") or "")
        parts = text.split()
        if not parts:
            return "Команда /subscribe"

        user = await self.user_repository.find_by_telegram_id(user_id)
        if user is None:
            return "Нажми /start, чтобы я тебя зарегистрировал."

        settings = self._get_settings(user)
        topics = settings.get("topics", [])
        if not isinstance(topics, list):
            topics = []

        if len(parts) == 1:
            if not topics:
                return (
                    "У тебя пока нет подписок.\n\n"
                    "Использование:\n"
                    "/subscribe add <тема>\n"
                    "/subscribe remove <тема>"
                )
            return "Твои подписки:\n" + ", ".join(topics)

        if len(parts) < 3:
            return "Использование: /subscribe add <тема> или /subscribe remove <тема>"

        action = parts[1].lower()
        topic = " ".join(parts[2:]).strip()
        if not topic:
            return "Тема не может быть пустой"

        norm = self._normalize(topic)

        if action == "add":
            if any(self._normalize(t) == norm for t in topics):
                return f"Ты уже подписан на тему: {topic}"
            topics = topics + [topic]
            self._set_topics(user, topics)
            await self.user_repository.update(user)
            return f"Готово! Ты подписался на тему: {topic}"

        if action == "remove":
            new_topics = [t for t in topics if self._normalize(t) != norm]
            if len(new_topics) == len(topics):
                return f"Тема '{topic}' не найдена в твоих подписках."
            self._set_topics(user, new_topics)
            await self.user_repository.update(user)
            return f"Готово! Подписка на тему '{topic}' удалена."

        return "Неизвестное действие. Используй add или remove."