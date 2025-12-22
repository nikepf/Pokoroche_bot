import pytest
from unittest.mock import AsyncMock
from src.pokoroche.commands.digest_cmd import DigestCommand


@pytest.mark.asyncio
async def test_digest_cmd_success():
    use_case = AsyncMock()  # фейковый объект use case
    use_case.execute = AsyncMock(return_value=True)

    cmd = DigestCommand(digest_delivery_use_case=use_case)  # создание команды; даем фейковый use case
    reply = await cmd.handle(user_id=123, message={"text": "/digest"})  # вызов обработчика

    assert reply == "Дайджест отправлен."
    use_case.execute.assert_awaited_once_with(123)  # await + вызван один раз + аргумент user_id


@pytest.mark.asyncio
async def test_digest_cmd_fail():
    use_case = AsyncMock()
    use_case.execute = AsyncMock(return_value=False)

    cmd = DigestCommand(digest_delivery_use_case=use_case)
    reply = await cmd.handle(user_id=123, message={"text": "/digest"})

    assert reply == "Не получилось отправить дайджест."
    use_case.execute.assert_awaited_once_with(123)
