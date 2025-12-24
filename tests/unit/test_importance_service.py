import pytest
from unittest.mock import AsyncMock
from src.pokoroche.domain.services.importance_service import ImportanceService, remove_invisible_chars


class TestRemoveInvisibleChars:
    def test_remove_invisible_chars_basic(self):
        text = "Hello\u0000World\u200B"
        result = remove_invisible_chars(text)
        assert result == "HelloWorld"
    
    def test_remove_invisible_chars_empty(self):
        assert remove_invisible_chars("") == ""
    
    def test_remove_invisible_chars_only_invisible(self):
        text = "\u0000\u0001\u0002\u0003"
        result = remove_invisible_chars(text)
        assert result == ""
    
    def test_remove_invisible_chars_mixed(self):
        text = "Normal text\u200Cwith\u200Dcontrol\u0007chars"
        result = remove_invisible_chars(text)
        assert result == "Normal textwithcontrolchars"

class TestImportanceService:
    @pytest.fixture
    def mock_ml_client(self):
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_ml_client):
        return ImportanceService(mock_ml_client)
    
    @pytest.mark.asyncio
    async def test_calculate_importance_normal_text(self, service, mock_ml_client):
        mock_ml_client.analyze_importance.return_value = 0.8
        text = "Важное сообщение с контекстом"
        context = {"chat_id": 123, "user_id": 456}
        
        result = await service.calculate_importance(text, context)
        
        assert result == 0.8
        mock_ml_client.analyze_importance.assert_called_once_with(text, context)
    
    @pytest.mark.asyncio
    async def test_calculate_importance_empty_text(self, service, mock_ml_client):
        result = await service.calculate_importance("")
        assert result == 0.0
        mock_ml_client.analyze_importance.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_calculate_importance_whitespace_text(self, service, mock_ml_client):
        result = await service.calculate_importance("   \n\t  ")
        assert result == 0.0
        mock_ml_client.analyze_importance.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_calculate_importance_none_text(self, service, mock_ml_client):
        result = await service.calculate_importance(None)
        assert result == 0.0
        mock_ml_client.analyze_importance.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_calculate_importance_text_normalization(self, service, mock_ml_client):
        mock_ml_client.analyze_importance.return_value = 0.7
        text = "  Текст с пробелами  \n"
        
        await service.calculate_importance(text)
        
        call_args = mock_ml_client.analyze_importance.call_args[0]
        assert call_args[0] == "Текст с пробелами"
    
    @pytest.mark.asyncio
    async def test_calculate_importance_context_cleaning(self, service, mock_ml_client):
        mock_ml_client.analyze_importance.return_value = 0.6
        text = "Текст"
        context = {
            "": "empty_key",
            "normal_key": "value",
            "key_with_empty_value": "",
            "  KEY_WITH_SPACES  ": "value",
            None: "none_key"
        }
        
        await service.calculate_importance(text, context)
        
        call_kwargs = mock_ml_client.analyze_importance.call_args[1]
        cleaned_context = call_kwargs.get('context', {})
        
        assert "normal_key" in cleaned_context
        assert "key_with_spaces" in cleaned_context
        assert "" not in cleaned_context
        assert "key_with_empty_value" not in cleaned_context
        assert None not in cleaned_context
    
    @pytest.mark.asyncio
    async def test_calculate_importance_ml_error(self, service, mock_ml_client):
        mock_ml_client.analyze_importance.side_effect = Exception("ML Error")
        text = "Текст"
        
        result = await service.calculate_importance(text)
        
        assert result == 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_importance_score_normalization(self, service, mock_ml_client):
        mock_ml_client.analyze_importance.return_value = 1.5
        result = await service.calculate_importance("Текст")
        assert result == 1.0
        
        mock_ml_client.analyze_importance.return_value = -0.5
        result = await service.calculate_importance("Текст")
        assert result == 0.0
        
        mock_ml_client.analyze_importance.return_value = 0.75
        result = await service.calculate_importance("Текст")
        assert result == 0.75
    
    @pytest.mark.asyncio
    async def test_batch_calculate_importance(self, service, mock_ml_client):
        mock_ml_client.analyze_importance.side_effect = [0.1, 0.2, 0.3]
        texts = ["Текст1", "Текст2", "Текст3"]
        
        results = await service.batch_calculate_importance(texts)
        
        assert len(results) == 3
        assert results == [0.1, 0.2, 0.3]
        assert mock_ml_client.analyze_importance.call_count == 3
    
    @pytest.mark.asyncio
    async def test_batch_calculate_importance_empty(self, service, mock_ml_client):
        results = await service.batch_calculate_importance([])
        assert results == []
        mock_ml_client.analyze_importance.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_invisible_chars_removal(self, service, mock_ml_client):
        mock_ml_client.analyze_importance.return_value = 0.5
        text = "Текст\u200Bс\u0000невидимыми\u200Cсимволами"
        
        await service.calculate_importance(text)
        
        call_args = mock_ml_client.analyze_importance.call_args[0]
        assert call_args[0] == "Текстсневидимымисимволами"
    
    @pytest.mark.asyncio
    async def test_unicode_normalization(self, service, mock_ml_client):
        mock_ml_client.analyze_importance.return_value = 0.5
        text = "café"
        
        await service.calculate_importance(text)
        
        call_args = mock_ml_client.analyze_importance.call_args[0]
        assert len(call_args[0]) == 4