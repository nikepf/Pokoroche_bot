from pydantic import BaseSettings
from typing import Optional

class DatabaseSettings(BaseSettings):
    """Настройки базы данных"""
    database_url: Optional[str] = None
    db_name: str = "pokoroche"
    db_user: str = "postgres"
    db_password: str = "password"

class RedisSettings(BaseSettings):
    """Настройки Redis"""
    redis_url: str = "redis://localhost:6379"

class MLServiceSettings(BaseSettings):
    """Настройки ML сервиса"""
    ml_service_url: str = "http://localhost:8001"

class BotSettings(BaseSettings):
    """Настройки бота"""
    bot_token: str

class AppSettings(BaseSettings):
    """Общие настройки приложения"""
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"

class ApplicationConfig(BaseSettings):
    """Основной класс конфигурации"""

    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    ml_service: MLServiceSettings = MLServiceSettings()
    bot: BotSettings = BotSettings()
    app: AppSettings = AppSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def load_config() -> ApplicationConfig:
    """Загрузить конфигурацию"""
    return ApplicationConfig()
