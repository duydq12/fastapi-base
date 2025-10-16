"""Implements asynchronous CRUD repository for FastAPI applications.

Provides async methods for create, read, update, and delete operations using SQLAlchemy.

Classes:
    SQLAsyncRepository: Asynchronous CRUD repository for SQLAlchemy models.
"""

import logging
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from fastwings.error_code import ServerErrorCode
from fastwings.model import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class SQLAsyncRepository(Generic[ModelType]):
    """Asynchronous CRUD repository for SQLAlchemy models.

    Provides async methods for create, read, update, and delete operations.

    Args:
        model (Type[ModelType]): SQLAlchemy model class.
    """

    def __init__(self, model: type[ModelType]):
        """Initializes the repository with a SQLAlchemy model class.

        Args:
            model (Type[ModelType]): SQLAlchemy model class.
        """
        self.model = model

    async def get(self, session: AsyncSession, obj_id: Any) -> ModelType | None:
        """Asynchronously retrieve an object by ID.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (Any): Object ID to query.

        Returns:
            Optional[ModelType]: Retrieved model instance or None.

        Raises:
            BusinessException: On database error.
        """
        try:
            data = (await session.scalars(select(self.model).where(self.model.id == obj_id))).first()
        except SQLAlchemyError as ex:
            raise ServerErrorCode.DATABASE_ERROR.value(ex) from ex
        logger.debug(f"Get id: {obj_id} from table {self.model.__tablename__.upper()} done")
        return data

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Asynchronously create a new object in the database.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_in (CreateSchemaType): Pydantic schema for creation.

        Returns:
            ModelType: Created model instance.

        Raises:
            BusinessException: On database error.
        """
        try:
            obj_in_data = obj_in.model_dump(exclude_unset=True)
            db_obj = self.model(**obj_in_data)  # type: ignore
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        except SQLAlchemyError as ex:
            await session.rollback()
            raise ServerErrorCode.DATABASE_ERROR.value(ex) from ex
        logger.debug(f"Insert {db_obj} to table {self.model.__tablename__.upper()} done")
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        obj_id: Any,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> UpdateSchemaType | dict[str, Any]:
        """Asynchronously update an object in the database.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (Any): Object ID to update.
            obj_in (UpdateSchemaType | Dict[str, Any]): Update data.

        Returns:
            UpdateSchemaType | Dict[str, Any]: Updated data.

        Raises:
            BusinessException: On database error.
        """
        try:
            obj = (await session.execute(select(self.model).where(self.model.id == obj_id))).scalars().first()
            update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(obj, key, value)
            await session.commit()
            await session.refresh(obj)
        except SQLAlchemyError as ex:
            await session.rollback()
            raise ServerErrorCode.DATABASE_ERROR.value(ex) from ex
        logger.debug(f"Update {update_data} to table {self.model.__tablename__.upper()} done")
        return obj_in

    async def delete(
        self,
        session: AsyncSession,
        *,
        obj_id: Any,
    ) -> None:
        """Asynchronously delete an object in the database.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (Any): Object ID to delete.

        Returns:
            None
        Raises:
            BusinessException: On database error.
        """
        try:
            obj = (await session.execute(select(self.model).where(self.model.id == obj_id))).scalars().first()
            await session.delete(obj)
            await session.commit()
        except SQLAlchemyError as ex:
            await session.rollback()
            raise ServerErrorCode.DATABASE_ERROR.value(ex) from ex
        logger.debug(f"Delete {obj_id} to table {self.model.__tablename__.upper()} done")
