import pytest
from src.pokoroche.adapters.fake_ml_client import FakeMLClient

class TestFakeMLClient:
    @pytest.fixture
    def client(self):
        return FakeMLClient()
    
    @pytest.mark.asyncio
    async def test_analyze_importance_empty_text(self, client):
        result = await client.analyze_importance("")
        assert result == 0.0
    
    @pytest.mark.asyncio
    async def test_analyze_importance_length_score(self, client):
        short_text = "Короткий"
        short_result = await client.analyze_importance(short_text)
        
        medium_text = "a" * 150
        medium_result = await client.analyze_importance(medium_text)
        
        long_text = "a" * 400
        long_result = await client.analyze_importance(long_text)
        
        assert short_result < medium_result < long_result
        assert long_result == 1.0
        assert medium_result == pytest.approx(150/300)
    
    @pytest.mark.asyncio
    async def test_analyze_importance_urgency_score(self, client):
        normal_text = "Обычное сообщение"
        normal_score = await client.analyze_importance(normal_text)
        
        exclamation_text = "Срочно! Важно!"
        exclamation_score = await client.analyze_importance(exclamation_text)
        
        question_text = "Что делать?"
        question_score = await client.analyze_importance(question_text)
        
        assert exclamation_score > normal_score
        assert question_score > normal_score
    
    @pytest.mark.asyncio
    async def test_analyze_importance_uppercase_score(self, client):
        lower_text = "текст без заглавных букв"
        lower_score = await client.analyze_importance(lower_text)
        
        upper_text = "ВАЖНОЕ СООБЩЕНИЕ С МНОГИМИ ЗАГЛАВНЫМИ"
        upper_score = await client.analyze_importance(upper_text)
        
        assert upper_score > lower_score
    
    @pytest.mark.asyncio
    async def test_extract_topics_empty(self, client):
        result = await client.extract_topics("")
        assert result == []
    
    @pytest.mark.asyncio
    async def test_extract_topics_basic(self, client):
        text = "Программирование на Python и разработка на Java"
        result = await client.extract_topics(text)
        
        assert "программирование" in result
        assert "разработка" in result
        assert "python" in result
        assert "java" in result
    
    @pytest.mark.asyncio
    async def test_extract_topics_short_words_filtered(self, client):
        text = "и на или но с для"
        result = await client.extract_topics(text)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_extract_topics_special_chars(self, client):
        text = "C++ разработка! Python?! JavaScript-программирование."
        result = await client.extract_topics(text)
        
        assert "c" in result
        assert "разработка" in result
        assert "python" in result
        assert "javascript-программирование" in result
    
    @pytest.mark.asyncio
    async def test_extract_topics_case_insensitive(self, client):
        text = "Python PYTHON python"
        result = await client.extract_topics(text)
        
        assert len(result) == 1
        assert result[0] == "python"
    
    @pytest.mark.asyncio
    async def test_categorize_message_basic(self, client):
        text = "Python Python разработка"
        result = await client.categorize_message(text)
        
        assert "python" in result
        assert "разработка" in result
        assert result["python"] == pytest.approx(0.7)
        assert result["разработка"] == pytest.approx(0.6)
    
    @pytest.mark.asyncio
    async def test_categorize_message_score_cap(self, client):
        text = "слово " * 10
        result = await client.categorize_message(text)
        
        assert result["слово"] == 1.0
    
    @pytest.mark.asyncio
    async def test_categorize_message_no_long_words(self, client):
        text = "и или на с"
        result = await client.categorize_message(text)
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        result = await client.health_check()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_context_parameter_ignored(self, client):
        result_without_context = await client.analyze_importance("Текст")
        result_with_context = await client.analyze_importance("Текст", {"chat_id": 123})
        
        assert result_without_context == result_with_context