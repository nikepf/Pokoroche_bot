class StatsCommand:
    def __init__(self, user_repository, digest_repository):
        self.user_repository = user_repository
        self.digest_repository = digest_repository
    
    async def handle(self, user_id: int, message: dict) -> str:
        # TODO: Показать статистику пользователя:
        # - Сколько дайджестов отправлено
        # - Средняя оценка фидбека
        # - Активность по темам
        return "Команда /stats"