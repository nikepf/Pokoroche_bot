# src/pokoroche/infrastructure/config/config.py
import os
from typing import Optional


class DatabaseConfig:
    def __init__(self):
        self.url = os.getenv("DATABASE_URL")
        self.name = os.getenv("DB_NAME", "pokoroche")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "password")


class RedisConfig:
    def __init__(self):
        self.url = os.getenv("REDIS_URL", "redis://redis:6379")


class MLServiceConfig:
    def __init__(self):
        self.url = os.getenv("ML_SERVICE_URL", "http://ml_mock:8000")


class BotConfig:
    def __init__(self):
        self.token = os.getenv("BOT_TOKEN")
        if not self.token:
            raise ValueError("BOT_TOKEN не задан!")


class AppConfig:
    def __init__(self):
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")


class ApplicationConfig:
    def __init__(self):
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.ml_service = MLServiceConfig()
        self.bot = BotConfig()
        self.app = AppConfig()
        if not self.database.url:
            raise ValueError("DATABASE_URL не задан!")
        if not self.bot.token:
            raise ValueError("BOT_TOKEN не задан!")


def load_config() -> ApplicationConfig:
    return ApplicationConfig()