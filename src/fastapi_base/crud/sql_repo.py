"""Implements synchronous CRUD repository for FastAPI applications.

Provides methods for create, read, update, and delete operations using SQLAlchemy.

Classes:
    SQLRepository: Synchronous CRUD repository for SQLAlchemy models.
"""

import logging
import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_base.error_code import ServerErrorCode
from fastapi_base.model import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class SQLRepository(Generic[ModelType]):
    """Synchronous CRUD repository for SQLAlchemy models.

    Provides methods for create, read, update, and delete operations.

    Args:
        model (Type[ModelType]): SQLAlchemy model class.
    """

    def __init__(self, model: type[ModelType]):
        """Initializes the repository with a SQLAlchemy model class.

        Args:
            model (Type[ModelType]): SQLAlchemy model class.
        """
        self.model = model

    def get(self, session: Session, obj_id: Any) -> ModelType | None:
        """Retrieve an object by ID.

        Args:
            session (Session): SQLAlchemy session.
            obj_id (Any): Object ID to query.

        Returns:
            Optional[ModelType]: Retrieved model instance or None.

        Raises:
            BusinessException: On database error.
        """
        try:
            data = session.query(self.model).filter(self.model.id == obj_id, self.model.is_deleted.is_(False)).first()
        except SQLAlchemyError as ex:
            raise ServerErrorCode.DATABASE_ERROR.value(ex) from ex
        logger.debug(f"Get id: {obj_id} from table {self.model.__tablename__.upper()} done")
        return data

    def create(self, session: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new object in the database.

        Args:
            session (Session): SQLAlchemy session.
            obj_in (CreateSchemaType): Pydantic schema for creation.

        Returns:
            ModelType: Created model instance.

        Raises:
            BusinessException: On database error.
        """
        try:
            obj_in_data = obj_in.dict(exclude_unset=True)
            db_obj = self.model(**obj_in_data)  # type: ignore
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        except SQLAlchemyError as ex:
            session.rollback()
            raise ServerErrorCode.DATABASE_ERROR.value(ex) from ex
        logger.debug(f"Insert {db_obj} to table {self.model.__tablename__.upper()} done")
        return db_obj

    def update(
        self,
        session: Session,
        *,
        obj_id: uuid.UUID,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> UpdateSchemaType | dict[str, Any]:
        """Update an object in the database.

        Args:
            session (Session): SQLAlchemy session.
            obj_id (uuid.UUID): Object ID to update.
            obj_in (UpdateSchemaType | Dict[str, Any]): Update data.

        Returns:
            UpdateSchemaType | Dict[str, Any]: Updated data.

        Raises:
            BusinessException: On database error.
        """
        try:
            update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
            session.query(self.model).filter(self.model.id == obj_id).update(update_data)  # type: ignore
            session.commit()
        except SQLAlchemyError as ex:
            session.rollback()
            raise ServerErrorCode.DATABASE_ERROR.value(ex) from ex
        logger.debug(f"Update {update_data} to table {self.model.__tablename__.upper()} done")
        return obj_in

    def delete(
        self,
        session: Session,
        *,
        obj_id: uuid.UUID,
    ) -> None:
        """Soft delete an object in the database.

        Args:
            session (Session): SQLAlchemy session.
            obj_id (uuid.UUID): Object ID to delete.

        Returns:
            None
        Raises:
            BusinessException: On database error.
        """
        try:
            session.query(self.model).filter(self.model.id == obj_id).update({"is_deleted": True})
            session.commit()
            session.expire_all()
        except SQLAlchemyError as ex:
            session.rollback()
            raise ServerErrorCode.DATABASE_ERROR.value(ex) from ex
        logger.debug(f"Delete {obj_id} to table {self.model.__tablename__.upper()} done")
