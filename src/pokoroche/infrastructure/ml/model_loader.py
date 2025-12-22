import pickle
import aiofiles
from pathlib import Path


class ModelLoader:
    def __init__(self, model_path: str):
        # Путь к папке или файлу с моделями
        self.model_path = model_path
        # Атрибуты для моделей
        self.topic_model = None
        self.importance_model = None

    async def load_models(self) -> bool:
        try:
            # Проверяю, существует ли путь к моделям
            if not Path(self.model_path).exists():
                # Если не существует, то выбрасываю соответствующее исключение
                raise FileNotFoundError("Путь к моделям не найден")
            # Загружаю модель для анализа тем
            topic_model_file = Path(self.model_path) / "topic_model.pkl"
            # Проверяю, существует ли соответствующий файл
            if not topic_model_file.exists():
                # Если не существует, то выбрасываю соответствующее исключение
                raise FileNotFoundError("Файл topic_model.pkl не найден")
            # Открываю файл (асинхронно) с моделью для чтения в бинарном режиме (тк pickle сохраняет объекты в специальном двоичном формате, а не как обычный текст)
            async with aiofiles.open(topic_model_file, "rb") as file:
                data = await file.read()
            # Чтение бинарных данных (асинхронно) из файла и превращение их обратно в Python-объект (модель для анализа тем) и сохранение загруженной модели в атрибут
            self.topic_model = pickle.loads(data)
            # Загружаю модель для анализа важности сообщения
            importance_model_file = Path(self.model_path) / "importance_model.pkl"
            # Проверяю, существует ли соответствующий файл
            if not importance_model_file.exists():
                # Если не существует, то выбрасываю соответствующее исключение
                raise FileNotFoundError("Файл importance_model.pkl не найден")
            # Открываю файл (асинхронно) с моделью для чтения в бинарном режиме (тк pickle сохраняет объекты в специальном двоичном формате, а не как обычный текст)
            async with aiofiles.open(importance_model_file, "rb") as file:
                data = await file.read()
                # Чтение бинарных данных (асинхронно) из файла и превращение их обратно в Python-объект (модель для анализа важности сообщения) и сохранение загруженной модели в атрибут
            self.importance_model = pickle.loads(data)
            return True
        except Exception as e:
            print(f"Ошибка при запуске моделей:", e)
            return False
