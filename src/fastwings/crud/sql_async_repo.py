"""Implements asynchronous CRUD repository for FastAPI applications.

Provides async methods for create, read, update, and delete operations using SQLAlchemy.

Classes:
    SQLAsyncRepository: Asynchronous CRUD repository for SQLAlchemy models.
    SoftDeletableAsyncRepository: Async repository supporting soft deletion.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Generic, TypeVar, cast

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from fastwings.crud.sql_query_builder import QueryBuilder, SoftDeletableQueryBuilder
from fastwings.model import BaseModel

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from sqlalchemy import ColumnElement

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticBaseModel)

logger = logging.getLogger(__name__)


class SQLAsyncRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Asynchronous CRUD repository for SQLAlchemy models.

    Provides async methods for create, read, update, and delete operations.

    Attributes:
        model (type[ModelType]): SQLAlchemy model class.
        model_id_column (ColumnElement[Any]): Column representing the model's ID.
    """

    def __init__(self, model: type[ModelType]):
        """Initializes the repository with a SQLAlchemy model class.

        Args:
            model (type[ModelType]): SQLAlchemy model class.

        Raises:
            TypeError: If the model cannot be inspected or has no primary key.
        """
        self.model = model

        # Get the ID column properly from the mapper
        mapper = inspect(self.model)
        if mapper is None:
            raise TypeError(f"Could not inspect model {self.model.__name__}")

        pk_columns = list(mapper.primary_key)
        if len(pk_columns) == 0:
            raise TypeError(f"Model {self.model.__name__} has no primary key")

        # Use the first primary key column (most models have single PK)
        self.model_id_column: ColumnElement[Any] = pk_columns[0]

    def query(self) -> QueryBuilder[ModelType]:
        """Creates a new QueryBuilder instance for this repository's model.

        Returns:
            QueryBuilder[ModelType]: A new query builder instance.

        Example:
            users = await repo.query() \
                .add_filters(User.is_active == True) \
                .order_by(User.created_at.desc()) \
                .limit(10) \
                .all(session)
        """
        return QueryBuilder(self.model)

    async def get(self, session: AsyncSession, obj_id: Any) -> ModelType | None:
        """Asynchronously retrieve an object by ID.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (Any): Object ID to query.

        Returns:
            ModelType | None: Retrieved model instance or None.
        """
        stmt = self.query().add_filters(self.model.id == obj_id).limit(1).as_select()
        result = await session.execute(stmt)
        data: ModelType | None = result.scalars().first()

        logger.debug(f"Get id: {obj_id} from table {self.model.__tablename__.upper()} done")
        return data

    async def get_by(
        self,
        session: AsyncSession,
        *,
        order_by: Sequence[ColumnElement[Any]] | None = None,
        **filters: Any
    ) -> ModelType | None:
        """Retrieve a single object by filter conditions.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            order_by (Sequence[ColumnElement[Any]] | None, optional): Columns to order by. Defaults to model ID column.
            **filters: Filter conditions (e.g., email="user@example.com").

        Returns:
            ModelType | None: Retrieved model instance or None.
        """
        stmt = self.query() \
            .add_filters(**filters) \
            .order_by(*(order_by if order_by is not None else [self.model_id_column])) \
            .limit(1) \
            .as_select()
        result = await session.execute(stmt)
        data: ModelType | None = result.scalars().first()

        logger.debug(f"Get by {filters} from table {self.model.__tablename__.upper()} done")
        return data

    async def get_multi(
        self,
        session: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        order_by: Sequence[ColumnElement[Any]] | None = None,
        **filters: Any
    ) -> Sequence[ModelType]:
        """Retrieve multiple objects with optional pagination and filters.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.
            order_by (Sequence[ColumnElement[Any]] | None, optional): Columns to order by. Defaults to model ID column.
            **filters: Filter conditions.

        Returns:
            Sequence[ModelType]: List of model instances.
        """
        stmt = self.query() \
            .add_filters(**filters) \
            .order_by(*(order_by if order_by is not None else [self.model_id_column])) \
            .offset(offset) \
            .limit(limit) \
            .as_select()
        result = await session.execute(stmt)
        data: Sequence[ModelType] = result.scalars().all()

        logger.debug(
            f"Get multi (offset={offset}, limit={limit}) from table {self.model.__tablename__.upper()} done"
        )
        return data

    async def get_all(
        self,
        session: AsyncSession,
        *,
        order_by: Sequence[ColumnElement[Any]] | None = None,
        **filters: Any
    ) -> Sequence[ModelType]:
        """Retrieve all objects matching the given filters.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            order_by (Sequence[ColumnElement[Any]] | None, optional): Columns to order by. Defaults to model ID column.
            **filters: Filter conditions.

        Returns:
            Sequence[ModelType]: List of all matching model instances.
        """
        stmt = self.query() \
            .add_filters(**filters) \
            .order_by(*(order_by if order_by is not None else [self.model_id_column])) \
            .as_select()
        result = await session.execute(stmt)
        data: Sequence[ModelType] = result.scalars().all()

        logger.debug(f"Get all from table {self.model.__tablename__.upper()} done")
        return data

    async def count(
        self,
        session: AsyncSession,
        **filters: Any
    ) -> int:
        """Count objects matching the given filters.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            **filters: Filter conditions.

        Returns:
            int: Number of matching records.
        """
        stmt = self.query().add_filters(**filters).as_count()
        result = await session.execute(stmt)
        count: int = cast(int, result.scalar_one())

        logger.debug(f"Count from table {self.model.__tablename__.upper()}: {count}")
        return count

    async def exists(
        self,
        session: AsyncSession,
        **filters: Any
    ) -> bool:
        """Check if any object exists matching the given filters.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            **filters: Filter conditions.

        Returns:
            bool: True if at least one matching record exists.
        """
        stmt = self.query().add_filters(**filters).as_exists()
        result = await session.execute(stmt)
        exists: bool = cast(bool, result.scalar_one())

        logger.debug(f"Exists check in table {self.model.__tablename__.upper()}: {exists}")
        return exists

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: CreateSchemaType,
    ) -> ModelType:
        """Asynchronously create a new object in the database.

        Uses the model's from_data method for proper validation.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_in (CreateSchemaType): Pydantic schema for creation.

        Returns:
            ModelType: Created model instance.
        """
        db_obj: ModelType = self.model.from_data(obj_in)
        session.add(db_obj)

        await session.flush([db_obj])
        await session.refresh(db_obj)

        logger.debug(f"Insert to table {self.model.__tablename__.upper()} done")
        return db_obj

    async def create_multi(
        self,
        session: AsyncSession,
        *,
        objs_in: list[CreateSchemaType],
    ) -> list[ModelType]:
        """Create multiple objects in a single transaction.

        Uses the model's from_data method for proper validation.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            objs_in (list[CreateSchemaType]): List of creation schemas.

        Returns:
            list[ModelType]: List of created model instances.
        """
        db_objs: list[ModelType] = [self.model.from_data(obj_in) for obj_in in objs_in]
        session.add_all(db_objs)
        await session.flush(db_objs)

        logger.debug(f"Bulk insert {len(db_objs)} records to table {self.model.__tablename__.upper()} done")
        return db_objs

    async def update(
        self,
        session: AsyncSession,
        *,
        obj_id: Any,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """Asynchronously update an object in the database.

        Uses the model's update method for proper validation and field protection.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (Any): Object ID to update.
            obj_in (UpdateSchemaType | dict[str, Any]): Update data.

        Returns:
            ModelType: Updated model instance.

        Raises:
            ValueError: If the object with the given ID is not found.
        """
        obj = await self.get(session, obj_id)
        if obj is None:
            raise ValueError(f"Object with id {obj_id} not found.")

        # Use the model's update method which handles view_only_fields and validation
        obj.update(obj_in)

        await session.flush([obj])
        await session.refresh(obj)

        logger.debug(f"Update in table {self.model.__tablename__.upper()} done")
        return obj

    async def update_multi(
        self,
        session: AsyncSession,
        *,
        values: dict[str, Any],
        **filters: Any
    ) -> int:
        """Update multiple records matching the filters.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            values (dict[str, Any]): Values to update.
            **filters: Filter conditions to select records to update.

        Returns:
            int: Number of updated records.

        Raises:
            ValueError: If values is empty.
        """
        if not values:
            raise ValueError("Update values cannot be empty")

        stmt = self.query().add_filters(**filters).as_update(values)
        result = await session.execute(stmt)

        await session.flush()
        updated_count: int = result.rowcount or 0

        logger.debug(f"Bulk update {updated_count} records in table {self.model.__tablename__.upper()} done")
        return updated_count

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

        Raises:
            ValueError: If the object with the given ID is not found.
        """
        obj = await self.get(session, obj_id)
        if obj is None:
            raise ValueError(f"Object with id {obj_id} not found.")

        await session.delete(obj)
        await session.flush()

        logger.debug(f"Delete {obj_id} from table {self.model.__tablename__.upper()} done")

    async def delete_multi(
        self,
        session: AsyncSession,
        **filters: Any
    ) -> int:
        """Delete multiple records matching the filters.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            **filters: Filter conditions to select records to delete.

        Returns:
            int: Number of deleted records.
        """
        stmt = self.query().add_filters(**filters).as_delete()
        result = await session.execute(stmt)

        await session.flush()
        deleted_count: int = result.rowcount or 0

        logger.debug(f"Bulk delete {deleted_count} records from table {self.model.__tablename__.upper()} done")
        return deleted_count

    async def paginate(
        self,
        session: AsyncSession,
        *,
        page: int = 1,
        per_page: int = 20,
        order_by: Sequence[ColumnElement[Any]] | None = None,
        **filters: Any
    ) -> tuple[Sequence[ModelType], int]:
        """Paginate results with total count.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            page (int, optional): Page number (1-indexed). Defaults to 1.
            per_page (int, optional): Number of items per page. Defaults to 20.
            order_by (Sequence[ColumnElement[Any]] | None, optional): Columns to order by. Defaults to model ID column.
            **filters: Filter conditions.

        Returns:
            tuple[Sequence[ModelType], int]: Tuple of (items, total_count).
        """
        # Get paginated items
        items_stmt = self.query() \
            .add_filters(**filters) \
            .order_by(*(order_by if order_by is not None else [self.model_id_column])) \
            .paginate(page, per_page) \
            .as_select()

        items_result = await session.execute(items_stmt)
        items: Sequence[ModelType] = items_result.scalars().all()

        # Get total count
        count_stmt = self.query().add_filters(**filters).as_count()
        count_result = await session.execute(count_stmt)
        total: int = cast(int, count_result.scalar_one())

        logger.debug(
            f"Paginate (page={page}, per_page={per_page}) from table {self.model.__tablename__.upper()} done"
        )
        return items, total

    async def upsert(
        self,
        session: AsyncSession,
        *,
        obj_in: CreateSchemaType | UpdateSchemaType,
        match_fields: list[str],
    ) -> tuple[ModelType, bool]:
        """Insert or update based on matching fields.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_in (CreateSchemaType | UpdateSchemaType): Data to insert/update.
            match_fields (list[str]): Fields to match for existing record.

        Returns:
            tuple[ModelType, bool]: Tuple of (model_instance, was_created).

        Raises:
            ValueError: If match_fields is empty or contains invalid field names.
        """
        if not match_fields:
            raise ValueError("match_fields cannot be empty")

        obj_data = obj_in.model_dump(exclude_unset=True)

        # Validate that all match_fields exist in the model
        mapper = inspect(self.model)
        if mapper is not None:
            model_columns = set(mapper.columns.keys())
            invalid_fields = [f for f in match_fields if f not in model_columns]
            if invalid_fields:
                raise ValueError(f"Invalid match_fields: {invalid_fields}. Not found in model.")

        # Build filters from match fields
        filters = {field: obj_data[field] for field in match_fields if field in obj_data}

        if len(filters) != len(match_fields):
            missing = set(match_fields) - set(filters.keys())
            raise ValueError(f"match_fields {missing} not found in input data")

        # Try to find existing record
        existing = await self.get_by(session, **filters)

        if existing:
            # Update existing using model's update method
            existing.update(obj_in)
            db_obj = existing
            was_created = False
        else:
            # Create new using model's from_data method
            db_obj = self.model.from_data(obj_in)
            session.add(db_obj)
            was_created = True

        await session.flush([db_obj])
        await session.refresh(db_obj)

        action = "Created" if was_created else "Updated"
        logger.debug(f"{action} in table {self.model.__tablename__.upper()} done")
        return db_obj, was_created


class SoftDeletableAsyncRepository(SQLAsyncRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Asynchronous CRUD repository supporting soft deletion.

    Provides utilities for querying and soft-deleting data on BaseModel with is_deleted field.
    """

    def __init__(self, model: type[ModelType]):
        """Initializes the repository and validates soft-delete support.

        Args:
            model (type[ModelType]): SQLAlchemy model class.

        Raises:
            TypeError: If the model doesn't support soft deletion.
        """
        super().__init__(model)

        # Validate that the model has soft_delete method
        if not hasattr(self.model, "soft_delete"):
            raise TypeError(
                f"Model {self.model.__name__} does not have a soft_delete method. "
                "Ensure it inherits from SoftDeletableDbModel."
            )

    def query(self) -> SoftDeletableQueryBuilder[ModelType]:
        """Creates a new SoftDeletableQueryBuilder instance for this repository's model.

        Returns:
            SoftDeletableQueryBuilder[ModelType]: A new query builder instance.
        """
        return SoftDeletableQueryBuilder(self.model)

    async def delete(
        self,
        session: AsyncSession,
        *,
        obj_id: Any,
    ) -> None:
        """Soft-deletes an object in the database.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (Any): Object ID to delete.

        Raises:
            ValueError: If the object with the given ID is not found.
        """
        obj = await self.get(session, obj_id)
        if obj is None:
            raise ValueError(f"Object with id {obj_id} not found.")

        obj.soft_delete()
        await session.flush([obj])

        logger.debug(f"Soft delete {obj_id} from table {self.model.__tablename__.upper()} done")

    async def delete_multi(
        self,
        session: AsyncSession,
        **filters: Any
    ) -> int:
        """Soft-deletes multiple records matching the filters using bulk update.

        This is more efficient than fetching and updating each record individually.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            **filters: Filter conditions to select records to delete.

        Returns:
            int: Number of soft-deleted records.
        """
        # Use bulk update to set is_deleted = True
        stmt = self.query().add_filters(**filters).as_update({"is_deleted": True})
        result = await session.execute(stmt)

        await session.flush()
        deleted_count: int = result.rowcount or 0

        logger.debug(f"Bulk soft delete {deleted_count} records from table {self.model.__tablename__.upper()} done")
        return deleted_count

    async def restore(
        self,
        session: AsyncSession,
        *,
        obj_id: Any,
    ) -> ModelType:
        """Restores a soft-deleted object.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (Any): Object ID to restore.

        Returns:
            ModelType: The restored model instance.

        Raises:
            ValueError: If the object with the given ID is not found.
        """
        # Query including deleted records
        stmt = self.query().include_deleted().add_filters(self.model.id == obj_id).limit(1).as_select()
        result = await session.execute(stmt)
        obj: ModelType | None = result.scalars().first()

        if obj is None:
            raise ValueError(f"Object with id {obj_id} not found.")

        obj.is_deleted = False
        await session.flush([obj])
        await session.refresh(obj)

        logger.debug(f"Restore {obj_id} in table {self.model.__tablename__.upper()} done")
        return obj

    async def restore_multi(
        self,
        session: AsyncSession,
        **filters: Any
    ) -> int:
        """Restores multiple soft-deleted records matching the filters.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            **filters: Filter conditions to select records to restore.

        Returns:
            int: Number of restored records.
        """
        # Build query that includes deleted records
        stmt = self.query().only_deleted().add_filters(**filters).as_update({"is_deleted": False})
        result = await session.execute(stmt)

        await session.flush()
        restored_count: int = result.rowcount or 0

        logger.debug(f"Bulk restore {restored_count} records in table {self.model.__tablename__.upper()} done")
        return restored_count

    async def hard_delete(
        self,
        session: AsyncSession,
        *,
        obj_id: Any,
    ) -> None:
        """Permanently deletes an object from the database (bypasses soft delete).

        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (Any): Object ID to permanently delete.

        Raises:
            ValueError: If the object with the given ID is not found.
        """
        # Query including deleted records
        stmt = self.query().include_deleted().add_filters(self.model.id == obj_id).limit(1).as_select()
        result = await session.execute(stmt)
        obj: ModelType | None = result.scalars().first()

        if obj is None:
            raise ValueError(f"Object with id {obj_id} not found.")

        await session.delete(obj)
        await session.flush()

        logger.debug(f"Hard delete {obj_id} from table {self.model.__tablename__.upper()} done")

    async def hard_delete_multi(
        self,
        session: AsyncSession,
        **filters: Any
    ) -> int:
        """Permanently deletes multiple records from the database (bypasses soft delete).

        Args:
            session (AsyncSession): SQLAlchemy async session.
            **filters: Filter conditions to select records to permanently delete.

        Returns:
            int: Number of permanently deleted records.
        """
        stmt = self.query().include_deleted().add_filters(**filters).as_delete()
        result = await session.execute(stmt)

        await session.flush()
        deleted_count: int = result.rowcount or 0

        logger.debug(f"Hard delete {deleted_count} records from table {self.model.__tablename__.upper()} done")
        return deleted_count
