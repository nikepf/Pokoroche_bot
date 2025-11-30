from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
Base = declarative_base()


class Database:
    """Управление асинхронными подключениями к PostgreSQL."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker] = None

    async def connect(self) -> None:
        """Инициализация движка."""
        if self.engine is not None:
            return

        self.engine = create_async_engine(self.database_url, echo=False, future=True)
        self.session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def disconnect(self) -> None:
        """Закрытие подключения к базе данных и освобождение ресурсов."""
        if self.engine is None:
            return

        await self.engine.dispose()
        self.engine = None
        self.session_factory = None

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получение асинхронной сессии для работы с базой данных."""
        if self.session_factory is None:
            raise RuntimeError("Database is not connected. Call `connect()` first.")

        async with self.session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    async def create_tables(self) -> None:
        """Создание всех таблиц в базе данных на основе декларативных моделей."""
        if self.engine is None:
            raise RuntimeError("Database is not connected. Call `connect()` first.")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def health_check(self) -> bool:
        """Проверка доступности базы данных с помощью запроса SELECT 1."""
        if self.engine is None:
            return False

        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False


# TODO: Добавить миграции (alembic / yoyo и т.п.)
