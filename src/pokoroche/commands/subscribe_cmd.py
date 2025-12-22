class SubscribeCommand:
    def __init__(self, user_repository, topic_service):
        self.user_repository = user_repository
        self.topic_service = topic_service

    # нормализация тем
    def normalize_topic(self, topic: str) -> str:
        return " ".join((topic or "").strip().lower().split())

    async def handle(self, user_id: int, message: dict) -> str:
        """Реализация подписок на темы"""

        text = message.get("text") or ""
        if not isinstance(text, str):
            return "Команда /subscribe"
        parts = text.split()
        if not parts:
            return "Команда /subscribe"

        # /subscribe
        # len = 1 чтобы не спутать с другой командой
        if len(parts) == 1:
            # достаём пользователя из БД
            user = await self.user_repository.find_by_telegram_id(user_id)
            if user is None:
                return "Нажми /start, чтобы я тебя зарегистрировал."

            # достаем список тем
            settings = user.settings if isinstance(user.settings, dict) else {}
            topics = settings.get("topics", [])
            if not isinstance(topics, list):
                topics = []

            # если тем нет
            if not topics:
                return (
                    "У тебя пока нет подписок.\n\n"
                    "Как пользоваться:\n"
                    "/subscribe - показать подписки\n"
                    "/subscribe add <тема> - подписаться\n"
                    "/subscribe remove <тема> - отписаться"
                )

            # темы есть
            topics = [t for t in topics if isinstance(t, str) and t.strip()]
            topics_str = ", ".join(topics)
            return (
                "Твои подписки:\n"
                f"{topics_str}\n\n"
                "Команды:\n"
                "/subscribe add <тема>\n"
                "/subscribe remove <тема>"
            )

        # /subscribe add <topic> и /subscribe remove <topic>
        action = parts[1].lower()
        if action not in ("add", "remove"):
            return (
                "Неверный формат команды.\n\n"
                "Как пользоваться:\n"
                "/subscribe - показать подписки\n"
                "/subscribe add <тема> - подписаться\n"
                "/subscribe remove <тема> - отписаться"
            )

        # достаем тему
        _topic = " ".join(parts[2:]).strip()
        topic = self.normalize_topic(_topic)
        if not topic:
            return (
                "Укажи тему.\n\n"
                "Пример:\n"
                "/subscribe add учеба\n"
                "/subscribe remove учеба"
            )

        # достаём пользователя из БД
        user = await self.user_repository.find_by_telegram_id(user_id)
        if user is None:
            return "Нажми /start, чтобы я тебя зарегистрировал."

        # достаем список тем
        settings = user.settings if isinstance(user.settings, dict) else {}
        topics = settings.get("topics", [])
        if not isinstance(topics, list):
            topics = []

        # чистим и готовим для сравнения
        topics = [t for t in topics if isinstance(t, str) and t.strip()]
        topics_norm = [self.normalize_topic(t) for t in topics]

        # add
        if action == "add":
            if topic in topics_norm:
                return f"Ты уже подписан(а) на тему: {topic}"

            topics.append(topic)

            # обновляем настройки пользователя
            user.update_settings(topics=topics)
            await self.user_repository.update(user)
            return f"Готово! Ты подписался на тему: {topic}"
        # remove
        elif action == "remove":
            if topic not in topics_norm:
                return f"Тема не найдена в подписках: {topic}"

            new_topics = []
            for t in topics:
                if self.normalize_topic(t) != topic:
                    new_topics.append(t)

            user.update_settings(topics=new_topics)
            await self.user_repository.update(user)
            return f"Готово! Подписка на тему: {topic} убрана"
