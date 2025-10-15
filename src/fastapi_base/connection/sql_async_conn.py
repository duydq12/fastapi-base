"""Implements asynchronous database connection management for FastAPI applications.

Provides async session manager and utilities for database health checks.
"""

import asyncio
import contextlib
from collections.abc import AsyncIterator
from socket import gaierror
from typing import Any

import decouple
from asyncpg.exceptions._base import PostgresError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select

DB_HOST = decouple.config("DB_HOST")
DB_NAME = decouple.config("DB_NAME")
DB_USER = decouple.config("DB_USER")
DB_PASSWORD = decouple.config("DB_PASSWORD")
DB_ENGINE = decouple.config("DB_ENGINE")
DB_POOL_SIZE = decouple.config("DB_POOL_SIZE", cast=int, default=10)


# Heavily inspired by https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
class SessionManager:
    """Manages asynchronous SQLAlchemy engine and session creation for FastAPI applications.

    Provides context managers for async database connections and sessions.

    Args:
        host (str): Database connection string.
        engine_kwargs (dict, optional): Additional engine configuration.
    """

    def __init__(self, host: str, engine_kwargs: dict[str, Any] | None = None):
        """Initializes the SessionManager with async engine and sessionmaker.

        Args:
            host (str): Database connection string.
            engine_kwargs (dict, optional): Additional engine configuration.
        """
        if not engine_kwargs:
            engine_kwargs = {"pool_pre_ping": True, "pool_size": DB_POOL_SIZE}
        else:
            engine_kwargs.update({"pool_pre_ping": True, "pool_size": DB_POOL_SIZE})
        self._engine: AsyncEngine | None = create_async_engine(host, **engine_kwargs)
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine, expire_on_commit=False
        )

    async def close(self) -> None:
        """Closes the async engine and sessionmaker, releasing resources.

        Raises:
            Exception: If SessionManager is not initialized.
        """
        if self._engine is None:
            raise Exception("SessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Async context manager for database connection.

        Yields:
            AsyncConnection: An active async database connection.

        Raises:
            Exception: If SessionManager is not initialized.
        """
        if self._engine is None:
            raise Exception("SessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Async context manager for database session.

        Yields:
            AsyncSession: An active async database session.

        Raises:
            Exception: If SessionManager is not initialized.
        """
        if self._sessionmaker is None:
            raise Exception("SessionManager is not initialized")

        async with self._sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


if DB_ENGINE == "postgre":
    engine = "postgresql+asyncpg"
elif DB_ENGINE == "mysql":
    engine = "mysql+asyncmy"
else:
    raise ValueError(f"Not support for engine: {DB_ENGINE}")

str_connection = f"{engine}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
sessionmanager = SessionManager(str_connection)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Provides an async generator for yielding a database session using SessionManager.

    Yields:
        AsyncSession: An active async database session.
    """
    async with sessionmanager.session() as session:
        yield session


async def is_database_online() -> bool:
    """Checks if the database is online by executing a simple query.

    Returns:
        bool: True if database is online, False otherwise.
    """
    try:
        async for session in get_db_session():
            async with session:
                await asyncio.wait_for(session.execute(select(1)), timeout=30)
    except (SQLAlchemyError, PostgresError, gaierror, TimeoutError):
        return False
    return True


if __name__ == "__main__":
    asyncio.run(is_database_online())
