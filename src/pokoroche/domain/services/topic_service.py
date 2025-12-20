import re
import unicodedata
from abc import ABC, abstractmethod
from typing import List, Dict


def remove_invisible_chars(s: str) -> str:
    # Удаляем все символы, категория которых 'Cc' (Control) или 'Cf' (Format)
    return "".join(c for c in s if unicodedata.category(c) not in ('Cc', 'Cf'))


class ITopicService(ABC):
    """Интерфейс сервиса определения и классификации тем"""

    @abstractmethod
    async def extract_topics(self, text: str) -> List[str]:
        """Извлечь релевантные темы из текста"""
        pass

    @abstractmethod
    async def categorize_message(self, text: str) -> Dict[str, float]:
        """Классифицировать сообщение по темам с оценками уверенности"""
        pass


class TopicService(ITopicService):
    """Сервис определения тем"""

    def __init__(self, ml_client):
        self.ml_client = ml_client

    async def extract_topics(self, text: str) -> List[str]:
        # TODO: Реализовать извлечение тем
        # Делаю проверку: (переменная не содержит строку) || (переменная - пустая строка) || (переменная - строка с пробелами, переносами строки или табами)
        if text is None or text == "" or text.isspace():
            return []
        # Теперь я сделаю предобработку текста, чтобы сделать его чище.
        # Убираю пробелы в начале и в конце строки.
        text = text.strip()
        # Делаю нормализацию Unicode, чтобы привести текст к единому стандарту и убрать различия, которые модель может принять за разные символы.
        # NFC композирует символы: комбинирует букву + диакритический знак в один символ, если возможно.
        text = unicodedata.normalize("NFC", text)
        # Делаю очистку невидимых символов, оставляем только печатаемые символы и пробелы
        text = remove_invisible_chars(text)
        try:
            topics = await self.ml_client.extract_topics(text)
        except Exception as e:
            # Логируем ошибку
            print(f"Ошибка при вызове ML: {e}")
            return []
        # Делаю проверку на корректность формата вывода
        if not isinstance(topics, list):
            return []
        # Делаю нормализацию вывода.
        # Добавляю разрешённые символы для тем: буквы a-z, а-я, ё, цифры, дефис
        allowed_topics = re.compile(r'[^a-zа-яё0-9-]')
        normalized: List[str] = []
        # Создаю set, чтобы не было повторов в темах
        topics_set = set()
        for topic in topics:
            if not isinstance(topic, str):
                continue
            t_norm = topic.strip().lower()
            # Удаляю все символы, кроме разрешённых
            t_norm = allowed_topics.sub('', t_norm)
            if t_norm == "":
                continue
            if t_norm in topics_set:
                continue
            topics_set.add(t_norm)
            normalized.append(t_norm)
        return normalized

    async def categorize_message(self, text: str) -> Dict[str, float]:
        # TODO: Реализовать многоклассовую классификацию
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
