from typing import Dict, Any


class DigestCommand:
    """Обработчик команды /digest"""

    def __init__(self, digest_delivery_use_case):
        self.digest_delivery_use_case = digest_delivery_use_case  # собирает и отправляет дайджест пользователю

    async def handle(self, user_id: int, message: Dict[str, Any]) -> str:
        """Обработка /digest"""
        ok = await self.digest_delivery_use_case.execute(user_id)
        if ok:
            return "Дайджест отправлен."
        return "Не получилось отправить дайджест."
