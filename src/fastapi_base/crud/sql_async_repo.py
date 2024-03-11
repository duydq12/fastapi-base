"""doc."""

import logging
import uuid

from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_base.error_code import ServerErrorCode
from fastapi_base.model import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class SQLAsyncRepository(Generic[ModelType]):
    """Define BaseSQL repository object."""

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, session: AsyncSession, obj_id: Any) -> Optional[ModelType]:
        """Define method get data by query id."""
        try:
            data = (
                await session.scalars(
                    select(self.model).where(self.model.id == obj_id).where(self.model.is_deleted.is_(False))
                )
            ).first()
        except SQLAlchemyError as ex:
            raise ServerErrorCode.DATABASE_ERROR.value(ex)
        logger.debug(f"Get id: {obj_id} from table {self.model.__tablename__.upper()} done")
        return data

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Define method create base for repository."""
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)  # type: ignore
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        except SQLAlchemyError as ex:
            raise ServerErrorCode.DATABASE_ERROR.value(ex)
        logger.debug(f"Insert {db_obj} to table {self.model.__tablename__.upper()} done")
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        obj_id: uuid.UUID,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Union[UpdateSchemaType, Dict[str, Any]]:
        """Define method update base for repository."""
        try:
            obj = await session.get(self.model, obj_id)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            obj.__dict__.update(update_data)
            await session.commit()
        except SQLAlchemyError as ex:
            raise ServerErrorCode.DATABASE_ERROR.value(ex)
        logger.debug(f"Update {update_data} to table {self.model.__tablename__.upper()} done")
        return obj_in

    async def delete(
        self,
        session: AsyncSession,
        *,
        obj_id: uuid.UUID,
    ) -> None:
        """Define method delete base for repository."""
        try:
            obj = await session.get(self.model, obj_id)
            obj.is_deleted = True
            await session.commit()
        except SQLAlchemyError as ex:
            raise ServerErrorCode.DATABASE_ERROR.value(ex)
        logger.debug(f"Delete {obj_id} to table {self.model.__tablename__.upper()} done")
