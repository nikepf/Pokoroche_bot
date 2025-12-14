class StatsCommand:
    def __init__(self, user_repository, digest_repository):
        self.user_repository = user_repository
        self.digest_repository = digest_repository

    # нормализация тем
    def normalize_topic(self, topic: str) -> str:
        return " ".join((topic or "").strip().lower().split())

    async def handle(self, user_id: int, message: dict) -> str:
        """ Статистика пользователя """
        user = await self.user_repository.find_by_telegram_id(user_id)
        if user is None:
            return "Нажми /start, чтобы я тебя зарегистрировал."

        # Сколько дайджестов отправлено
        try:
            digests = await self.digest_repository.get_user_digests(user_id=user_id, limit=1000)
        except Exception:
            return "Не получилось получить статистику. Попробуй позже."

        if not isinstance(digests, list):
            digests = []

        total = len(digests)

        # - Средняя оценка фидбека
        feedback_sum = 0.0
        feedback_count = 0

        for digest in digests:
            feedback_score = getattr(digest, "feedback_score", None)
            # на случай, если пользовательне не нажал 👎 или 👍
            if isinstance(feedback_score, (int, float)):
                feedback_sum += float(feedback_score)
                feedback_count += 1

        average_feedback = (feedback_sum / feedback_count) if feedback_count > 0 else None

        # - Активность по темам
        topic_counts = {}
        for digest in digests:
            important = getattr(digest, "important_messages", None)
            if not isinstance(important, list):
                continue

            for msg in important:
                if not isinstance(msg, dict):
                    continue

                tops = msg.get("topics")
                # если тема одна строкой, то переделываем в список
                if isinstance(tops, str):
                    tops = [tops]

                if isinstance(tops, list):
                    for t in tops:
                        if isinstance(t, str):
                            # нормализуем темы
                            nt = self.normalize_topic(t)
                            if nt:
                                topic_counts[nt] = topic_counts.get(nt, 0) + 1

        # формирование результата
        lines = []
        lines.append("Статистика")
        lines.append(f"Дайджестов отправлено: {total}")

        if average_feedback is None:
            lines.append("Средняя оценка: нет оценок")
        else:
            lines.append(f"Средняя оценка: {average_feedback:.2f}")

        if not topic_counts:
            lines.append("Темы: нет данных")
        else:
            # выводим первые 10 тем, чтобы сообщение не было громоздким
            all_topics = sorted(topic_counts.items(), key=lambda x: (-x[1], x[0]))
            lines.append("Темы (топ 10):")
            for name, cnt in all_topics[:10]:
                lines.append(f"• {name}: {cnt}")

        return "\n".join(lines)
