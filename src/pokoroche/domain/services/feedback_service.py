from abc import ABC, abstractmethod
from typing import Dict


class IFeedbackService(ABC):
    @abstractmethod
    # User_id - кто поставил оценку, чтобы не считать фидбек дважды
    # Chat_id - в каком чате был дайджест (иногда один пользователь в нескольких чатах)
    # Digest_id - какой именно дайджест
    # Score - палец вверх (1), палец вниз (0)
    # Нужен, чтобы сохранить палец вверх/вниз в базу
    async def save_feedback(self, user_id: int, chat_id: int, digest_id: str, score: int) -> None:
        pass

    # Digest_id - id дайджеста
    # Нужен, чтобы получить все оценки по дайджесту
    @abstractmethod
    async def get_feedback_for_digest(self, digest_id: str) -> Dict[str, int]:
        pass


class FeedbackService(IFeedbackService):
    def __init__(self, db_client, ml_client=None):
        self.db = db_client
        self.ml = ml_client

    async def save_feedback(self, user_id: int, chat_id: int, digest_id: str, score: int) -> None:
        # Проверка на корректность всех параметров
        if user_id <= 0:
            raise ValueError("user_id must be positive")
        if chat_id <= 0:
            raise ValueError("chat_id must be positive")
        if not isinstance(digest_id, str) or not digest_id.strip():
            raise ValueError("digest_id must be a non-empty string")
        if score < 0 or score > 1:
            raise ValueError("score must be between 0 and 1")
        # Есть ли запись, где user_id = X и digest_id = Y? (чтобы на одного и того же пользователя не создавалась новая запись)
        existing = await self.db.get_feedback(user_id, digest_id)
        if existing:
            # Если существует, то мы просто обновляем score, если пользователь например передумал
            existing.score = score
            await self.db.update_feedback(user_id, digest_id, score)
        else:
            # Если не существует, то просто добавляю новую запись
            record = {
                "user_id": user_id,
                "chat_id": chat_id,
                "digest_id": digest_id,
                "score": score
            }
            await self.db.insert_feedback(record)

    async def get_feedback_for_digest(self, digest_id: str) -> Dict[str, int]:
        # Проверка на корректность digest_id
        if not isinstance(digest_id, str) or not digest_id.strip():
            raise ValueError("digest_id must be a non-empty string")
        # Забрала все оценки из базы
        feedback_list = await self.db.get_feedback_for_digest(digest_id)
        # Если пустой, то возвращаю нули
        if feedback_list is None:
            return {"positive": 0, "negative": 0}
        # Иначе прохожусь по элементу из списка и подсчитываю голоса
        positive, negative = 0, 0
        for item in feedback_list:
            if item.score == 1:
                positive += 1
            if item.score == 0:
                negative += 1
        return {"positive": positive, "negative": negative}
