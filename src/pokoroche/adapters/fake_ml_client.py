import re
from typing import Dict, Any, List
from .ml_client import IMLClient


class FakeMLClient(IMLClient):
    """Тестовый ML клиент-заглушка для локальной разработки"""

    async def analyze_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        if not text:
            return 0.0
        text = text.strip()
        # Берем как один из критериев важности длину текста (считаю текст длины 300 как максимально важный)
        length_score = min(len(text) / 300, 1.0)
        # Дополнительный бонус к важности, который ориентируется на знаки препинания и регистр букв
        urgency_score = 0.0
        if '!' in text or '?' in text:
            urgency_score += 0.1
        # Считаю кол-во заглавных букв
        count_upper = sum(1 for c in text if c.isalpha() and c.isupper())
        # Считаю долю заглавных букв в тексте
        number_count_upper = count_upper / len(text)
        # Если доля заглавных букв больше 30%, то увеличиваю бонус к важности
        if number_count_upper > 0.3:
            urgency_score += 0.1
        final_importance = min(urgency_score + length_score, 1.0)
        return final_importance

    async def extract_topics(self, text: str) -> List[str]:
        if not text:
            return []
        text = text.strip().lower()
        words = text.split()
        # Допустимые символы - русские или латинские буквы, цифры, дефис
        allowed_chars = re.compile(r'[^a-zA-Zа-яА-ЯёЁ0-9-]')
        unique_words = set()
        for word in words:
            # "Очищаю" слово от недопустимых символов
            cleaned_word = allowed_chars.sub('', word)
            # Если слово осталось не пустым, то добавляю его в set
            if cleaned_word:
                unique_words.add(cleaned_word)
        topics = []
        for word in unique_words:
            # Если длина слова больше 4 (исключаю короткие слова по типу и, на, или и тд), то добавляю в список тем
            if len(word) > 4:
                topics.append(word)
        return topics

    async def categorize_message(self, text: str) -> Dict[str, float]:
        topics = await self.extract_topics(text)
        text_lower = text.lower()
        words = text_lower.split()
        number_for_topics = {}
        for topic in topics:
            # Считаю, сколько раз topic встречается среди слов в тексте.
            # Привожу topic к нижнему регистру для совпадения.
            count = words.count(topic.lower())
            number_for_topics[topic] = count
        result = {}
        for topic, count in number_for_topics.items():
            # Высчитываю score - даю базовый бонус 0.5 и добавляю 0.1 за каждое упоминание слова в тексте, беру минимум с 1.0
            score = min(0.5 + 0.1 * count, 1.0)
            result[topic] = score
        return result

    # Имитация состояния работы сервиса
    async def health_check(self) -> bool:
        return True
