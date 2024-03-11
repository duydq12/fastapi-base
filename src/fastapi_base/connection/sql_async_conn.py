import asyncio
import contextlib

from socket import gaierror
from typing import Any, AsyncIterator

import decouple

from asyncpg.exceptions._base import PostgresError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select

DB_HOST = decouple.config("DB_HOST")
DB_NAME = decouple.config("DB_NAME")
DB_USER = decouple.config("DB_USER")
DB_PASSWORD = decouple.config("DB_PASSWORD")
DB_ENGINE = decouple.config("DB_ENGINE")


# Heavily inspired by https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
class SessionManager(object):
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = None):
        if not engine_kwargs:
            engine_kwargs = {"pool_pre_ping": True}
        else:
            engine_kwargs.update({"pool_pre_ping": True})
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    async def close(self) -> None:
        if self._engine is None:
            raise Exception("SessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
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
        if self._sessionmaker is None:
            raise Exception("SessionManager is not initialized")

        session = self._sessionmaker()
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
    async with sessionmanager.session() as session:
        yield session


async def is_database_online():
    try:
        async for session in get_db_session():
            async with session:
                await asyncio.wait_for(session.execute(select(1)), timeout=30)
    except (SQLAlchemyError, PostgresError, gaierror, TimeoutError):
        return False
    return True


if __name__ == "__main__":
    asyncio.run(is_database_online())
