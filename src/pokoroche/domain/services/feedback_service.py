class FeedbackService:
    def __init__(self, digest_repository, ml_training_service):
        self.digest_repository = digest_repository
        self.ml_training_service = ml_training_service
    
    async def process_feedback(self, digest_id: int, user_id: int, score: float) -> bool:
        # TODO: Обработать фидбек пользователя
        pass