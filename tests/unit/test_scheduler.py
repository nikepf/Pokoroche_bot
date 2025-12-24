import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, time
import pytz
from src.pokoroche.infrastructure.scheduler import Scheduler


@pytest.fixture
def scheduler():
    return Scheduler(
        user_repository=AsyncMock(),
        digest_repository=AsyncMock(),
        telegram_bot=AsyncMock(),
        digest_delivery_uc=AsyncMock(),
        check_interval=10
    )


@pytest.fixture
def mock_user():
    user = Mock()
    user.telegram_id = 123456
    user.settings = {"digest_time": "20:00", "timezone": "Europe/Moscow"}
    return user


class TestSchedulerBasicMethods:
    
    def test_parse_valid_time(self, scheduler):
        assert scheduler._parse_digest_time("20:00") == time(20, 0)
        assert scheduler._parse_digest_time("09:05") == time(9, 5)
        assert scheduler._parse_digest_time("00:00") == time(0, 0)
    
    def test_parse_invalid_time(self, scheduler):
        assert scheduler._parse_digest_time("invalid") is None
        assert scheduler._parse_digest_time("25:00") is None
        assert scheduler._parse_digest_time("20:60") is None
        assert scheduler._parse_digest_time("") is None
        assert scheduler._parse_digest_time(None) is None
    
    def test_get_timezone(self, scheduler):
        tz = scheduler._get_user_timezone("Europe/Moscow")
        assert isinstance(tz, pytz.timezone)
        
        default_tz = scheduler._get_user_timezone("Invalid/Zone")
        assert str(default_tz) == "Europe/Moscow"
    
    def test_is_digest_time(self, scheduler):
        user_time = time(20, 0)
        
        now = datetime(2023, 1, 1, 20, 0, 15)
        assert scheduler._is_digest_time(user_time, now) is True
        
        now = datetime(2023, 1, 1, 19, 0, 15)
        assert scheduler._is_digest_time(user_time, now) is False
        
        now = datetime(2023, 1, 1, 20, 1, 15)
        assert scheduler._is_digest_time(user_time, now) is False
        
        now = datetime(2023, 1, 1, 20, 0, 31)
        assert scheduler._is_digest_time(user_time, now) is False


@pytest.mark.asyncio
class TestSchedulerCoreLogic:
    
    async def test_no_users(self, scheduler):
        scheduler.user_repo.get_all.return_value = []
        await scheduler.check_and_send_digests()
        scheduler.digest_delivery_uc.execute.assert_not_called()
    
    async def test_user_disabled_digest(self, scheduler, mock_user):
        mock_user.can_receive_digest.return_value = False
        scheduler.user_repo.get_all.return_value = [mock_user]
        
        await scheduler.check_and_send_digests()
        scheduler.digest_delivery_uc.execute.assert_not_called()
    
    @patch('src.pokoroche.infrastructure.scheduler.datetime')
    async def test_send_digest_at_correct_time(self, mock_datetime, scheduler, mock_user):
        mock_now = datetime(2023, 1, 1, 20, 0, 15)
        mock_datetime.now.return_value = mock_now
        
        mock_user.can_receive_digest.return_value = True
        scheduler.user_repo.get_all.return_value = [mock_user]
        scheduler.digest_delivery_uc.execute.return_value = True
        
        await scheduler.check_and_send_digests()
        scheduler.digest_delivery_uc.execute.assert_called_once_with(123456)
    
    @patch('src.pokoroche.infrastructure.scheduler.datetime')
    async def test_not_send_digest_at_wrong_time(self, mock_datetime, scheduler, mock_user):
        mock_now = datetime(2023, 1, 1, 19, 0, 15)
        mock_datetime.now.return_value = mock_now
        
        mock_user.can_receive_digest.return_value = True
        scheduler.user_repo.get_all.return_value = [mock_user]
        
        await scheduler.check_and_send_digests()
        scheduler.digest_delivery_uc.execute.assert_not_called()
    
    async def test_exception_handling(self, scheduler, mock_user):
        mock_user.can_receive_digest.side_effect = Exception("Test error")
        scheduler.user_repo.get_all.return_value = [mock_user]
        
        await scheduler.check_and_send_digests()


@pytest.mark.asyncio
class TestSchedulerStateManagement:
    
    async def test_start_and_stop(self, scheduler):
        task = await scheduler.start()
        assert scheduler.is_running is True
        assert scheduler.task is not None
        
        status = scheduler.get_status()
        assert status["is_running"] is True
        assert status["task_active"] is True
        
        await scheduler.stop()
        assert scheduler.is_running is False
        assert scheduler.task is None
    
    async def test_start_when_already_running(self, scheduler):
        scheduler.is_running = True
        await scheduler.start()
    
    async def test_stop_when_not_running(self, scheduler):
        scheduler.is_running = False
        await scheduler.stop()
    
    async def test_run_once(self, scheduler):
        with patch.object(scheduler, 'check_and_send_digests') as mock_check:
            await scheduler.run_once()
            mock_check.assert_called_once()


@pytest.mark.asyncio
class TestSchedulerEdgeCases:
    
    @patch('src.pokoroche.infrastructure.scheduler.datetime')
    async def test_multiple_users(self, mock_datetime, scheduler):
        mock_now = datetime(2023, 1, 1, 20, 0, 15)
        mock_datetime.now.return_value = mock_now
        
        users = []
        for i in range(3):
            user = Mock()
            user.telegram_id = i
            user.can_receive_digest.return_value = True
            user.settings = {"digest_time": "20:00", "timezone": "Europe/Moscow"}
            users.append(user)
        
        scheduler.user_repo.get_all.return_value = users
        
        await scheduler.check_and_send_digests()
        
        assert scheduler.digest_delivery_uc.execute.call_count == 3
    
    async def test_user_without_settings(self, scheduler):
        user = Mock()
        user.telegram_id = 123
        user.settings = None
        user.can_receive_digest.return_value = True
        
        scheduler.user_repo.get_all.return_value = [user]
        
        await scheduler.check_and_send_digests()
        scheduler.digest_delivery_uc.execute.assert_not_called()
    
    async def test_run_loop_exception_handling(self, scheduler):
        scheduler.is_running = True
        
        call_count = 0
        async def mock_check():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test error")
            else:
                scheduler.is_running = False
        
        scheduler.check_and_send_digests = mock_check
        await scheduler._run_loop()
        
        assert call_count == 2


def test_scheduler_custom_interval():
    scheduler = Scheduler(
        user_repository=AsyncMock(),
        digest_repository=AsyncMock(),
        telegram_bot=AsyncMock(),
        digest_delivery_uc=AsyncMock(),
        check_interval=30
    )
    
    assert scheduler.check_interval == 30
    status = scheduler.get_status()
    assert status["check_interval"] == 30