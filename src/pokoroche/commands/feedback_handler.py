import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)


class FeedbackHandler:
    """Обработчик фидбека по дайджестам"""

    def __init__(self,
                 telegram_bot,
                 digest_repository,
                 feedback_service):
        self.telegram_bot = telegram_bot
        self.digest_repository = digest_repository
        self.feedback_service = feedback_service

    async def handle(self, callback_data: Dict[str, Any]) -> None:
        """
        Обработать callback с оценкой дайджеста

        Формат callback_data:
        {
            "id": "123456789",
            "from": {"id": 987654321, "first_name": "Иван"},
            "message": {...},
            "data": "feedback:123:1"  # digest_id:score (1-лайк, 0-дизлайк)
        }
        """
        callback_id = callback_data.get("id")
        data = callback_data.get("data", "")
        user_id = callback_data.get("from", {}).get("id")

        logger.info("Feedback received",
                    callback_id=callback_id,
                    user_id=user_id,
                    data=data)

        if not data.startswith("feedback:"):
            logger.warning("Invalid feedback format", data=data)
            # отвечаем тг, чтобы кнопка не зависала
            if isinstance(callback_id, str):
                await self.telegram_bot.answer_callback_query(callback_id)
            return

        try:
            _, digest_id_str, score_str = data.split(":")
            digest_id = int(digest_id_str)
            score = float(score_str)

            logger.info("Processing feedback",
                        digest_id=digest_id,
                        score=score,
                        user_id=user_id)

            # 1 ) Сохранение фидбека в БД через digest_repository.update_feedback()
            if self.digest_repository is not None:
                await self.digest_repository.update_feedback(digest_id=digest_id, feedback_score=score)

            # 2) Отправка в ML для обучения через feedback_service.process_feedback()
            if self.feedback_service is not None:
                await self.feedback_service.process_feedback(
                    user_id=user_id,
                    digest_id=digest_id,
                    score=score,
                    raw_callback=callback_data,
                )

            # 3) Уведомление пользователя
            logger.info("Feedback processed successfully", digest_id=digest_id, score=score, user_id=user_id)

        except (ValueError, IndexError) as e:
            logger.error("Failed to parse feedback data",
                         data=data,
                         error=str(e))

        if isinstance(callback_id, str):
            await self.telegram_bot.answer_callback_query(callback_id)
