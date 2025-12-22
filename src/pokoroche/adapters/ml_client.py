import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import hashlib
import aiohttp
import json


class IMLClient(ABC):
    """Интерфейс для взаимодействия с ML сервисом"""

    @abstractmethod
    async def analyze_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        """Получить оценку важности текста (0.0 - 1.0)"""
        pass

    @abstractmethod
    async def extract_topics(self, text: str) -> List[str]:
        """Извлечь список тем из текста"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Проверить доступность ML сервиса"""
        pass


class MLClient(IMLClient):
    """Реализация ML клиента"""

    def __init__(self, ml_service_url: str, timeout: int = 30, max_retries: int = 3):
        self.ml_service_url = ml_service_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    async def analyze_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        """Реализация HTTP запроса к ML сервису для анализа важности"""
        url = f"{self.ml_service_url}/importance"
        payload = {"text": text, "context": context or {}}

        for _ in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=self.timeout) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        return float(data["importance"])
            except Exception:
                continue
        # Если в тексте нечего анализировать, то мы возвращаем 0.0
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
        """Извлечение списка тем из текста."""
        url = f"{self.ml_service_url}/topics"
        payload = {"text": text}

        for _ in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=self.timeout) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        return list(data["topics"])
            except Exception:
                continue
        # Если текст пустой, то возвращаю пустой список
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

    async def health_check(self) -> bool:
        """Проверка, доступен ли ML сервер"""
        url = f"{self.ml_service_url}/health"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, timeout=self.timeout) as resp:
                    return resp.status == 200
        except Exception:
            return False


class CachedMLClient(MLClient):
    """ML клиент с кешированием результатов в Redis"""

    CACHE_TTL = 3600  # Значение будет находиться в кеше CACHE_TTL секунд

    def __init__(self, ml_service_url: str, redis_client, timeout: int = 30, max_retries: int = 3):
        super().__init__(ml_service_url, timeout, max_retries)
        self.redis = redis_client

    def _generate_cache_key(self, text: str, prefix: str) -> str:
        """Генерируем уникальный ключ для Redis по тексту"""
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"{prefix}:{text_hash}"

    async def analyze_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        """Анализ важности с кешированием"""
        key = self._generate_cache_key(text, "importance")

        cached = await self.redis.get(key)
        if cached:
            print("CACHE HIT (Redis)")
            return float(cached)
        
        print("CACHE MISS (calling ML)")
        result = await super().analyze_importance(text, context)
        await self.redis.set(key, str(result), expire=self.CACHE_TTL)
        return result

    async def extract_topics(self, text: str) -> List[str]:
        """Извлечение тем с кешированием"""
        key = self._generate_cache_key(text, "topics")

        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        result = await super().extract_topics(text)
        await self.redis.set(key, json.dumps(result), expire=self.CACHE_TTL)
        return result
