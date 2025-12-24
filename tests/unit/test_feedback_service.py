import pytest
from unittest.mock import AsyncMock, MagicMock
from src.pokoroche.domain.services.feedback_service import FeedbackService

class TestFeedbackService:
    @pytest.fixture
    def mock_db_client(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_ml_client(self):
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_db_client, mock_ml_client):
        return FeedbackService(mock_db_client, mock_ml_client)
    
    @pytest.mark.asyncio
    async def test_save_feedback_new(self, service, mock_db_client):
        mock_db_client.get_feedback.return_value = None
        
        await service.save_feedback(
            user_id=123,
            chat_id=456,
            digest_id="digest_789",
            score=1
        )
        
        mock_db_client.insert_feedback.assert_called_once_with({
            "user_id": 123,
            "chat_id": 456,
            "digest_id": "digest_789",
            "score": 1
        })
        mock_db_client.update_feedback.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_feedback_update(self, service, mock_db_client):
        mock_db_client.get_feedback.return_value = MagicMock(score=0)
        
        await service.save_feedback(
            user_id=123,
            chat_id=456,
            digest_id="digest_789",
            score=1
        )
        
        mock_db_client.update_feedback.assert_called_once_with(123, "digest_789", 1)
        mock_db_client.insert_feedback.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_feedback_invalid_user_id(self, service):
        with pytest.raises(ValueError, match="user_id must be positive"):
            await service.save_feedback(
                user_id=0,
                chat_id=456,
                digest_id="digest_789",
                score=1
            )
        
        with pytest.raises(ValueError, match="user_id must be positive"):
            await service.save_feedback(
                user_id=-1,
                chat_id=456,
                digest_id="digest_789",
                score=1
            )
    
    @pytest.mark.asyncio
    async def test_save_feedback_invalid_chat_id(self, service):
        with pytest.raises(ValueError, match="chat_id must be positive"):
            await service.save_feedback(
                user_id=123,
                chat_id=0,
                digest_id="digest_789",
                score=1
            )
    
    @pytest.mark.asyncio
    async def test_save_feedback_invalid_digest_id(self, service):
        with pytest.raises(ValueError, match="digest_id must be a non-empty string"):
            await service.save_feedback(
                user_id=123,
                chat_id=456,
                digest_id="",
                score=1
            )
        
        with pytest.raises(ValueError, match="digest_id must be a non-empty string"):
            await service.save_feedback(
                user_id=123,
                chat_id=456,
                digest_id="   ",
                score=1
            )
        
        with pytest.raises(ValueError, match="digest_id must be a non-empty string"):
            await service.save_feedback(
                user_id=123,
                chat_id=456,
                digest_id=None,
                score=1
            )
    
    @pytest.mark.asyncio
    async def test_save_feedback_invalid_score(self, service):
        with pytest.raises(ValueError, match="score must be between 0 and 1"):
            await service.save_feedback(
                user_id=123,
                chat_id=456,
                digest_id="digest_789",
                score=-1
            )
        
        with pytest.raises(ValueError, match="score must be between 0 and 1"):
            await service.save_feedback(
                user_id=123,
                chat_id=456,
                digest_id="digest_789",
                score=2
            )
    
    @pytest.mark.asyncio
    async def test_get_feedback_for_digest_normal(self, service, mock_db_client):
        mock_feedback_list = [
            MagicMock(score=1),
            MagicMock(score=1),
            MagicMock(score=0),
            MagicMock(score=1),
            MagicMock(score=0),
        ]
        mock_db_client.get_feedback_for_digest.return_value = mock_feedback_list
        
        result = await service.get_feedback_for_digest("digest_123")
        
        assert result == {"positive": 3, "negative": 2}
        mock_db_client.get_feedback_for_digest.assert_called_once_with("digest_123")
    
    @pytest.mark.asyncio
    async def test_get_feedback_for_digest_empty(self, service, mock_db_client):
        mock_db_client.get_feedback_for_digest.return_value = []
        
        result = await service.get_feedback_for_digest("digest_123")
        
        assert result == {"positive": 0, "negative": 0}
    
    @pytest.mark.asyncio
    async def test_get_feedback_for_digest_none(self, service, mock_db_client):
        mock_db_client.get_feedback_for_digest.return_value = None
        
        result = await service.get_feedback_for_digest("digest_123")
        
        assert result == {"positive": 0, "negative": 0}
    
    @pytest.mark.asyncio
    async def test_get_feedback_for_digest_invalid_digest_id(self, service):
        with pytest.raises(ValueError, match="digest_id must be a non-empty string"):
            await service.get_feedback_for_digest("")
        
        with pytest.raises(ValueError, match="digest_id must be a non-empty string"):
            await service.get_feedback_for_digest(None)
    
    @pytest.mark.asyncio
    async def test_save_feedback_edge_cases(self, service, mock_db_client):
        mock_db_client.get_feedback.return_value = None
        
        await service.save_feedback(
            user_id=1,
            chat_id=1,
            digest_id="a",
            score=0
        )
        
        mock_db_client.insert_feedback.assert_called_once()
        
        await service.save_feedback(
            user_id=999999,
            chat_id=999999,
            digest_id="digest_" + "x" * 100,
            score=1
        )