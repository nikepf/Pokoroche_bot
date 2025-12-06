class SubscribeCommand:
    def __init__(self, user_repository, topic_service):
        self.user_repository = user_repository
        self.topic_service = topic_service
    
    async def handle(self, user_id: int, message: dict) -> str:
        # TODO: Реализовать подписку на темы
        # Форматы:
        # /subscribe - показать мои подписки
        # /subscribe add <тема> - подписаться
        # /subscribe remove <тема> - отписаться
        return "Команда /subscribe"