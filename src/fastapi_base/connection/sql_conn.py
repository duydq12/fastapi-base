import contextlib
import logging
import os
from typing import Iterator, Any

from sqlalchemy import create_engine, Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.orm import Session, sessionmaker
from tenacity import retry, stop_after_attempt, wait_fixed

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_ENGINE = os.getenv("DB_ENGINE")

logger = logging.getLogger(__name__)


class SessionManager(object):
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = None):
        if not engine_kwargs:
            engine_kwargs = {"pool_pre_ping": True}
        else:
            engine_kwargs.update({"pool_pre_ping": True})
        self._engine = create_engine(host, **engine_kwargs)
        self._sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    def close(self) -> None:
        if self._engine is None:
            raise Exception("SessionManager is not initialized")
        self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.contextmanager
    def connect(self) -> Iterator[Connection]:
        if self._engine is None:
            raise Exception("SessionManager is not initialized")

        with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        if self._sessionmaker is None:
            raise Exception("SessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


if DB_ENGINE == "postgre":
    engine = "postgresql+psycopg2"
elif DB_ENGINE == "mysql":
    engine = "mysql+pymysql"
else:
    raise ValueError(f"Not support for engine: {DB_ENGINE}")

str_connection = f"{engine}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
sessionmanager = SessionManager(str_connection)


def get_db_session() -> Iterator[Session]:
    """doc."""
    with sessionmanager.session() as session:
        yield session


@retry(
    stop=stop_after_attempt(30),
    wait=wait_fixed(1),
)
def is_database_online():
    try:
        for session in get_db_session():
            with session:
                session.execute(select(1))
    except (SQLAlchemyError, TimeoutError):
        return False
    return True


if __name__ == '__main__':
    is_database_online()
