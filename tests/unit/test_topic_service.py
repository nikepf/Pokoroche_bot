import pytest
from unittest.mock import AsyncMock
from src.pokoroche.domain.services.topic_service import TopicService, remove_invisible_chars

class TestTopicService:
    @pytest.fixture
    def mock_ml_client(self):
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_ml_client):
        return TopicService(mock_ml_client)
    
    @pytest.mark.asyncio
    async def test_extract_topics_normal(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = ["программирование", "python", "разработка"]
        text = "Обсуждение программирования на Python"
        
        result = await service.extract_topics(text)
        
        assert result == ["программирование", "python", "разработка"]
        mock_ml_client.extract_topics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_topics_empty_text(self, service, mock_ml_client):
        result = await service.extract_topics("")
        assert result == []
        mock_ml_client.extract_topics.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_extract_topics_whitespace(self, service, mock_ml_client):
        result = await service.extract_topics("   \n\t  ")
        assert result == []
        mock_ml_client.extract_topics.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_extract_topics_none(self, service, mock_ml_client):
        result = await service.extract_topics(None)
        assert result == []
        mock_ml_client.extract_topics.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_extract_topics_text_normalization(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = ["тема"]
        text = "  Текст с пробелами  \n"
        
        await service.extract_topics(text)
        
        call_args = mock_ml_client.extract_topics.call_args[0]
        assert call_args[0] == "Текст с пробелами"
    
    @pytest.mark.asyncio
    async def test_extract_topics_ml_error(self, service, mock_ml_client):
        mock_ml_client.extract_topics.side_effect = Exception("ML Error")
        text = "Текст"
        
        result = await service.extract_topics(text)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_extract_topics_wrong_format(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = "не список"
        
        result = await service.extract_topics("Текст")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_extract_topics_normalization(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = [
            "  Программирование  ",
            "PYTHON",
            "разработка-софта",
            "c++",
            "тест123",
            "тест!!",
            "",
            123,
            "   "
        ]
        
        result = await service.extract_topics("Текст")
        
        assert result == ["программирование", "python", "разработка-софта", "c", "тест123"]
    
    @pytest.mark.asyncio
    async def test_extract_topics_duplicates(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = ["python", "Python", "PYTHON"]
        
        result = await service.extract_topics("Текст")
        
        assert len(result) == 1
        assert result == ["python"]
    
    @pytest.mark.asyncio
    async def test_categorize_message_basic(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = ["программирование", "python"]
        text = "Программирование на Python, Python, Python"
        
        result = await service.categorize_message(text)
        
        assert "программирование" in result
        assert "python" in result
        assert result["программирование"] == pytest.approx(0.6)
        assert result["python"] == pytest.approx(0.8)
    
    @pytest.mark.asyncio
    async def test_categorize_message_score_capping(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = ["слово"]
        text = "слово слово слово слово слово слово"
        
        result = await service.categorize_message(text)

        assert result["слово"] == pytest.approx(1.0)
    
    @pytest.mark.asyncio
    async def test_categorize_message_case_insensitive(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = ["python"]
        text = "Python PYTHON python"
        
        result = await service.categorize_message(text)
        
        assert result["python"] == pytest.approx(0.8)
    
    @pytest.mark.asyncio
    async def test_categorize_message_empty_text(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = []
        text = ""
        
        result = await service.categorize_message(text)
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_invisible_chars_in_topics(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = ["тема"]
        text = "Текст\u200Bс\u0000невидимыми\u200Cсимволами"
        
        await service.extract_topics(text)
        
        call_args = mock_ml_client.extract_topics.call_args[0]
        assert call_args[0] == "Текстсневидимымисимволами"
    
    @pytest.mark.asyncio
    async def test_unicode_normalization_in_topics(self, service, mock_ml_client):
        mock_ml_client.extract_topics.return_value = ["тема"]
        text = "café"
        
        await service.extract_topics(text)
        
        call_args = mock_ml_client.extract_topics.call_args[0]
        assert len(call_args[0]) == 4