import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import unicodedata


def remove_invisible_chars(s: str) -> str:
    # Удаляем все символы, категория которых 'Cc' (Control) или 'Cf' (Format)
    return "".join(c for c in s if unicodedata.category(c) not in ('Cc', 'Cf'))


class IImportanceService(ABC):
    """Интерфейс сервиса анализа важности сообщений"""

    @abstractmethod
    async def calculate_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        """Рассчитать оценку важности сообщения"""
        pass

    @abstractmethod
    async def batch_calculate_importance(self, texts: List[str]) -> List[float]:
        """Пакетный расчет важности для нескольких сообщений"""
        pass


class ImportanceService(IImportanceService):
    """Сервис анализа важности"""

    def __init__(self, ml_client):
        self.ml_client = ml_client

    async def calculate_importance(self, text: str, context: Dict[str, Any] = None) -> float:
        # TODO: Реализовать логику анализа важности:
        # Использовать модели для классификации, учитывать контекст, комбинировать несколько факторов в итоговую оценку
        # Делаю проверку: (переменная не содержит строку) || (переменная - пустая строка) || (переменная - строка с пробелами, переносами строки или табами)
        if text is None or text == "" or text.isspace():
            return 0.0
        # Теперь я сделаю предобработку текста, чтобы сделать его чище.
        # Убираю пробелы в начале и в конце строки.
        text = text.strip()
        # Делаю нормализацию Unicode, чтобы привести текст к единому стандарту и убрать различия, которые модель может принять за разные символы.
        # NFC композирует символы: комбинирует букву + диакритический знак в один символ, если возможно.
        text = unicodedata.normalize("NFC", text)
        # Делаю очистку невидимых символов, оставляем только печатаемые символы и пробелы
        text = remove_invisible_chars(text)
        # Делаю проверку контекста: проверяю, что он действительно словарь
        if not isinstance(context, dict):
            context = {}
        # Удаляю из context пары, в которых ключ или значение пустые
        keys_to_delete = []
        for key, value in context.items():
            if key is None or key == "":
                keys_to_delete.append(key)
            elif value is None or (isinstance(value, str) and value.strip() == ""):
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del context[key]
        # Стандартизирую оставшиеся ключи: привожу к строке, убираю пробелы с начала и с конца, привожу в нижний регистр
        for key in list(context.keys()):
            new_key = str(key).strip().lower()
            if new_key != key:
                context[new_key] = context.pop(key)
        # Сделаю обработку ошибок ML: если ml_client.analyze_importance по какой-то причине падает (например, сеть, таймаут, ошибка сервера), то возвращаю 0.0 и логирую ошибку для отладки, чтобы весь бот не падал
        try:
            score = await self.ml_client.analyze_importance(text, context)
        except Exception as e:
            # Логируем ошибку
            print(f"Ошибка при вызове ML: {e}")
            score = 0.0
        # Нормализация score
        if score < 0.0:
            score = 0.0
        elif score > 1.0:
            score = 1.0
        return score

    async def batch_calculate_importance(self, texts: List[str]) -> List[float]:
        # TODO: Оптимизировать для пакетной обработки
        # Создаю список кортуин
        tasks = [self.calculate_importance(text) for text in texts]
        # Выполняю все корутины параллельно и жду их завершения
        results = await asyncio.gather(*tasks)
        # Возвращаю список результатов (float) в том же порядке, что и входные тексты
        return results
