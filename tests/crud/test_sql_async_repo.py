"""Unit tests for SQLAsyncRepository and SoftDeletableAsyncRepository; SQLRepository and SoftDeletableAsyncRepository.

Covers async CRUD, soft-delete, bulk operations, pagination, and upsert.
Uses real SQLAlchemy models and proper async session mocking.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import VARCHAR
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlmodel import Field

from fastwings.crud.sql_async_repo import (
    SoftDeletableAsyncRepository,
    SQLAsyncRepository,
)
from fastwings.crud.sql_repo import (
    SoftDeletableRepository,
    SQLRepository,
)
from fastwings.model import AuditableDbModel, BaseModel, DbModel


class TestModel(BaseModel, table=True):
    """Test model using FastWings' BaseModel (UUID PK, audit, soft-delete)."""
    name: str = Field(VARCHAR(50), nullable=False)
    email: str = Field(VARCHAR(255), nullable=False)


class TestCreateSchema(PydanticBaseModel):
    name: str
    email: str


class TestUpdateSchema(PydanticBaseModel):
    name: str


class TrulyNonSoftModel(AuditableDbModel, DbModel, table=True):
    name: str = Field(VARCHAR(50), nullable=False)
    # No SoftDeletableDbModel mixin


# --- Fixtures ---
@pytest.fixture
def mock_asession() -> AsyncMock:
    """Provides a properly configured mock AsyncSession."""
    session = AsyncMock(spec=AsyncSession)

    # Mock execute().scalars().first() chain
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    execute_mock = MagicMock()
    execute_mock.scalars.return_value = scalars_mock
    session.execute.return_value = execute_mock

    # Mock add (synchronous)
    session.add = MagicMock()
    session.add_all = MagicMock()

    # Mock flush and refresh (async)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    return session


@pytest.fixture
def arepo() -> SQLAsyncRepository[TestModel, TestCreateSchema, TestUpdateSchema]:
    """Repository for non-soft-deletable operations."""
    return SQLAsyncRepository(TestModel)


@pytest.fixture
def soft_arepo() -> SoftDeletableAsyncRepository[TestModel, TestCreateSchema, TestUpdateSchema]:
    """Repository for soft-deletable operations."""
    return SoftDeletableAsyncRepository(TestModel)


def create_mock_model(**kwargs) -> TestModel:
    """Create a TestModel instance with optional overrides."""
    defaults = {
        "id": uuid.uuid4(),
        "name": "test_name",
        "email": "test@example.com",
        "is_deleted": False,
    }
    defaults.update(kwargs)
    return TestModel(**defaults)


@pytest.mark.asyncio
async def test_aget_found(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test retrieving an existing object by ID."""
    obj = create_mock_model()
    mock_asession.execute.return_value.scalars().first.return_value = obj

    result = await arepo.get(mock_asession, obj.id)

    assert result == obj
    mock_asession.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_aget_not_found(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test retrieving a non-existent object returns None."""
    obj = None
    mock_asession.execute.return_value.scalars().first.return_value = obj

    result = await arepo.get(mock_asession, uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_acreate(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test creating a new object."""
    schema = TestCreateSchema(name="New User", email="new@example.com")

    # Mock the created object
    created_obj = create_mock_model(name=schema.name, email=schema.email)
    mock_asession.flush.side_effect = lambda objs: setattr(objs[0], 'id', created_obj.id)
    mock_asession.refresh.side_effect = lambda obj: None  # No-op

    result = await arepo.create(mock_asession, obj_in=schema)

    # Verify model creation and session calls
    mock_asession.add.assert_called_once()
    added_obj = mock_asession.add.call_args[0][0]
    assert isinstance(added_obj, TestModel)
    assert added_obj.name == schema.name
    assert added_obj.email == schema.email

    mock_asession.flush.assert_awaited_once()
    mock_asession.refresh.assert_awaited_once()
    assert result.id is not None
    assert result.name == schema.name


@pytest.mark.asyncio
async def test_aupdate(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test updating an existing object."""
    obj = create_mock_model()
    mock_asession.execute.return_value.scalars().first.return_value = obj

    schema = TestUpdateSchema(name="Updated Name")
    result = await arepo.update(mock_asession, obj_id=obj.id, obj_in=schema)

    assert obj.name == "Updated Name"
    assert result.name == "Updated Name"
    mock_asession.flush.assert_awaited_once()
    mock_asession.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_aupdate_not_found(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test updating a non-existent object raises ValueError."""
    mock_asession.execute.return_value.scalars().first.return_value = None

    with pytest.raises(ValueError, match="not found"):
        await arepo.update(mock_asession, obj_id=uuid.uuid4(), obj_in=TestUpdateSchema(name="test"))


@pytest.mark.asyncio
async def test_adelete(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test deleting an existing object."""
    obj = create_mock_model()
    mock_asession.execute.return_value.scalars().first.return_value = obj

    await arepo.delete(mock_asession, obj_id=obj.id)

    mock_asession.delete.assert_awaited_once_with(obj)
    mock_asession.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_acreate_multi(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test creating multiple objects."""
    schemas = [
        TestCreateSchema(name="User 1", email="u1@example.com"),
        TestCreateSchema(name="User 2", email="u2@example.com"),
    ]

    result = await arepo.create_multi(mock_asession, objs_in=schemas)

    mock_asession.add_all.assert_called_once()
    added_objs = mock_asession.add_all.call_args[0][0]
    assert len(added_objs) == 2
    assert all(isinstance(obj, TestModel) for obj in added_objs)
    assert added_objs[0].name == "User 1"
    assert added_objs[1].name == "User 2"

    mock_asession.flush.assert_awaited_once()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_aupdate_multi(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test bulk update operation."""
    mock_asession.execute.return_value.rowcount = 3

    count = await arepo.update_multi(mock_asession, values={"name": "Bulk Updated"}, email="test@example.com")

    assert count == 3
    mock_asession.execute.assert_awaited_once()
    mock_asession.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_adelete_multi(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test bulk delete operation."""
    mock_asession.execute.return_value.rowcount = 2

    count = await arepo.delete_multi(mock_asession, name="ToDelete")

    assert count == 2
    mock_asession.execute.assert_awaited_once()
    mock_asession.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_aget_multi(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test retrieving multiple objects with filters."""
    obj1 = create_mock_model(name="Alice")
    obj2 = create_mock_model(name="Bob")
    mock_asession.execute.return_value.scalars().all.return_value = [obj1, obj2]

    results = await arepo.get_multi(mock_asession, offset=0, limit=10, name="A%")

    assert len(results) == 2
    assert results[0].name == "Alice"
    mock_asession.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_apaginate(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test pagination returns items and total count."""
    items = [create_mock_model(name=f"Item{i}") for i in range(2)]
    mock_asession.execute.return_value.scalars().all.return_value = items
    mock_asession.execute.return_value.scalar_one.return_value = 42

    results, total = await arepo.paginate(mock_asession, page=1, per_page=10)

    assert len(results) == 2
    assert total == 42
    assert mock_asession.execute.await_count == 2


@pytest.mark.asyncio
async def test_aupsert_create(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test upsert creates a new record when no match."""
    mock_asession.execute.return_value.scalars().first.return_value = None
    schema = TestCreateSchema(name="New", email="new@example.com")

    obj, created = await arepo.upsert(mock_asession, obj_in=schema, match_fields=["email"])

    assert created is True
    mock_asession.add.assert_called_once()
    mock_asession.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_aupsert_update(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test upsert updates existing record when match found."""
    existing = create_mock_model(email="exists@example.com")
    mock_asession.execute.return_value.scalars().first.return_value = existing
    schema = TestUpdateSchema(name="Updated")

    obj, created = await arepo.upsert(mock_asession, obj_in=schema, match_fields=["name"])

    assert created is False
    assert existing.name == "Updated"
    mock_asession.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_asoft_delete(soft_arepo: SoftDeletableAsyncRepository, mock_asession: AsyncMock):
    """Test soft-delete marks record as deleted."""
    obj = create_mock_model()
    mock_asession.execute.return_value.scalars().first.return_value = obj

    await soft_arepo.delete(mock_asession, obj_id=obj.id)

    assert obj.is_deleted is True
    mock_asession.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_asoft_delete_multi(soft_arepo: SoftDeletableAsyncRepository, mock_asession: AsyncMock):
    """Test bulk soft-delete uses UPDATE statement."""
    mock_asession.execute.return_value.rowcount = 5

    count = await soft_arepo.delete_multi(mock_asession, name="ToDelete")

    assert count == 5
    # Verify the update sets is_deleted=True
    call_args = mock_asession.execute.call_args[0][0]
    assert "is_deleted" in str(call_args)


@pytest.mark.asyncio
async def test_arestore(soft_arepo: SoftDeletableAsyncRepository, mock_asession: AsyncMock):
    """Test restoring a soft-deleted record."""
    obj = create_mock_model(is_deleted=True)
    # Mock include_deleted() query
    mock_asession.execute.return_value.scalars().first.return_value = obj

    result = await soft_arepo.restore(mock_asession, obj_id=obj.id)

    assert result.is_deleted is False
    mock_asession.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_ahard_delete(soft_arepo: SoftDeletableAsyncRepository, mock_asession: AsyncMock):
    """Test hard-delete permanently removes record."""
    obj = create_mock_model(is_deleted=True)
    mock_asession.execute.return_value.scalars().first.return_value = obj

    await soft_arepo.hard_delete(mock_asession, obj_id=obj.id)

    mock_asession.delete.assert_awaited_once_with(obj)
    mock_asession.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_aupsert_invalid_match_field(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test upsert raises error for invalid match field."""
    schema = TestCreateSchema(name="Test", email="test@example.com")

    with pytest.raises(ValueError, match="Invalid match_fields"):
        await arepo.upsert(mock_asession, obj_in=schema, match_fields=["invalid_field"])


@pytest.mark.asyncio
async def test_aupdate_multi_empty_values(arepo: SQLAsyncRepository, mock_asession: AsyncMock):
    """Test update_multi raises error for empty values."""
    with pytest.raises(ValueError, match="Update values cannot be empty"):
        await arepo.update_multi(mock_asession, values={})


@pytest.mark.asyncio
async def test_asoft_repo_on_non_soft_model():
    """Test SoftDeletableAsyncRepository raises error on non-soft-deletable model."""
    with pytest.raises(TypeError, match="soft_delete method"):
        SoftDeletableAsyncRepository(TrulyNonSoftModel)


@pytest.fixture
def mock_session() -> MagicMock:
    """Provides a properly configured mock AsyncSession."""
    session = MagicMock(spec=Session)

    # Mock execute().scalars().first() chain
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    execute_mock = MagicMock()
    execute_mock.scalars.return_value = scalars_mock
    session.execute.return_value = execute_mock

    # Mock add (synchronous)
    session.add = MagicMock()
    session.add_all = MagicMock()

    # Mock flush and refresh (async)
    session.flush = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()

    return session


@pytest.fixture
def repo() -> SQLRepository[TestModel, TestCreateSchema, TestUpdateSchema]:
    """Repository for non-soft-deletable operations."""
    return SQLRepository(TestModel)


@pytest.fixture
def soft_repo() -> SoftDeletableRepository[TestModel, TestCreateSchema, TestUpdateSchema]:
    """Repository for soft-deletable operations."""
    return SoftDeletableRepository(TestModel)


def test_get_found(repo: SQLRepository, mock_session: MagicMock):
    """Test retrieving an existing object by ID."""
    obj = create_mock_model()
    mock_session.execute.return_value.scalars().first.return_value = obj

    result = repo.get(mock_session, obj.id)

    assert result == obj
    mock_session.execute.assert_called_once()


def test_get_not_found(repo: SQLRepository, mock_session: MagicMock):
    """Test retrieving a non-existent object returns None."""
    obj = None
    mock_session.execute.return_value.scalars().first.return_value = obj

    result = repo.get(mock_session, uuid.uuid4())
    assert result is None


def test_create(repo: SQLRepository, mock_session: MagicMock):
    """Test creating a new object."""
    schema = TestCreateSchema(name="New User", email="new@example.com")

    # Mock the created object
    created_obj = create_mock_model(name=schema.name, email=schema.email)
    mock_session.flush.side_effect = lambda objs: setattr(objs[0], 'id', created_obj.id)
    mock_session.refresh.side_effect = lambda obj: None  # No-op

    result = repo.create(mock_session, obj_in=schema)

    # Verify model creation and session calls
    mock_session.add.assert_called_once()
    added_obj = mock_session.add.call_args[0][0]
    assert isinstance(added_obj, TestModel)
    assert added_obj.name == schema.name
    assert added_obj.email == schema.email

    mock_session.flush.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.id is not None
    assert result.name == schema.name


def test_update(repo: SQLRepository, mock_session: MagicMock):
    """Test updating an existing object."""
    obj = create_mock_model()
    mock_session.execute.return_value.scalars().first.return_value = obj

    schema = TestUpdateSchema(name="Updated Name")
    result = repo.update(mock_session, obj_id=obj.id, obj_in=schema)

    assert obj.name == "Updated Name"
    assert result.name == "Updated Name"
    mock_session.flush.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_update_not_found(repo: SQLRepository, mock_session: MagicMock):
    """Test updating a non-existent object raises ValueError."""
    mock_session.execute.return_value.scalars().first.return_value = None

    with pytest.raises(ValueError, match="not found"):
        repo.update(mock_session, obj_id=uuid.uuid4(), obj_in=TestUpdateSchema(name="test"))


def test_delete(repo: SQLRepository, mock_session: MagicMock):
    """Test deleting an existing object."""
    obj = create_mock_model()
    mock_session.execute.return_value.scalars().first.return_value = obj

    repo.delete(mock_session, obj_id=obj.id)

    mock_session.delete.assert_called_once_with(obj)
    mock_session.flush.assert_called_once()


def test_create_multi(repo: SQLRepository, mock_session: MagicMock):
    """Test creating multiple objects."""
    schemas = [
        TestCreateSchema(name="User 1", email="u1@example.com"),
        TestCreateSchema(name="User 2", email="u2@example.com"),
    ]

    result = repo.create_multi(mock_session, objs_in=schemas)

    mock_session.add_all.assert_called_once()
    added_objs = mock_session.add_all.call_args[0][0]
    assert len(added_objs) == 2
    assert all(isinstance(obj, TestModel) for obj in added_objs)
    assert added_objs[0].name == "User 1"
    assert added_objs[1].name == "User 2"

    mock_session.flush.assert_called_once()
    assert len(result) == 2


def test_update_multi(repo: SQLRepository, mock_session: MagicMock):
    """Test bulk update operation."""
    mock_session.execute.return_value.rowcount = 3

    count = repo.update_multi(mock_session, values={"name": "Bulk Updated"}, email="test@example.com")

    assert count == 3
    mock_session.execute.assert_called_once()
    mock_session.flush.assert_called_once()


def test_delete_multi(repo: SQLRepository, mock_session: MagicMock):
    """Test bulk delete operation."""
    mock_session.execute.return_value.rowcount = 2

    count = repo.delete_multi(mock_session, name="ToDelete")

    assert count == 2
    mock_session.execute.assert_called_once()
    mock_session.flush.assert_called_once()


def test_get_multi(repo: SQLRepository, mock_session: MagicMock):
    """Test retrieving multiple objects with filters."""
    obj1 = create_mock_model(name="Alice")
    obj2 = create_mock_model(name="Bob")
    mock_session.execute.return_value.scalars().all.return_value = [obj1, obj2]

    results = repo.get_multi(mock_session, offset=0, limit=10, name="A%")

    assert len(results) == 2
    assert results[0].name == "Alice"
    mock_session.execute.assert_called_once()


def test_paginate(repo: SQLRepository, mock_session: MagicMock):
    """Test pagination returns items and total count."""
    items = [create_mock_model(name=f"Item{i}") for i in range(2)]
    mock_session.execute.return_value.scalars().all.return_value = items
    mock_session.execute.return_value.scalar_one.return_value = 42

    results, total = repo.paginate(mock_session, page=1, per_page=10)

    assert len(results) == 2
    assert total == 42
    assert mock_session.execute.call_count == 2


def test_upsert_create(repo: SQLRepository, mock_session: MagicMock):
    """Test upsert creates a new record when no match."""
    mock_session.execute.return_value.scalars().first.return_value = None
    schema = TestCreateSchema(name="New", email="new@example.com")

    obj, created = repo.upsert(mock_session, obj_in=schema, match_fields=["email"])

    assert created is True
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()


def test_upsert_update(repo: SQLRepository, mock_session: MagicMock):
    """Test upsert updates existing record when match found."""
    existing = create_mock_model(email="exists@example.com")
    mock_session.execute.return_value.scalars().first.return_value = existing
    schema = TestUpdateSchema(name="Updated")

    obj, created = repo.upsert(mock_session, obj_in=schema, match_fields=["name"])

    assert created is False
    assert existing.name == "Updated"
    mock_session.flush.assert_called_once()


# --- Soft-Delete Repository Tests ---
def test_soft_delete(soft_repo: SoftDeletableRepository, mock_session: MagicMock):
    """Test soft-delete marks record as deleted."""
    obj = create_mock_model()
    mock_session.execute.return_value.scalars().first.return_value = obj

    soft_repo.delete(mock_session, obj_id=obj.id)

    assert obj.is_deleted is True
    mock_session.flush.assert_called_once()


def test_soft_delete_multi(soft_repo: SoftDeletableRepository, mock_session: MagicMock):
    """Test bulk soft-delete uses UPDATE statement."""
    mock_session.execute.return_value.rowcount = 5

    count = soft_repo.delete_multi(mock_session, name="ToDelete")

    assert count == 5
    # Verify the update sets is_deleted=True
    call_args = mock_session.execute.call_args[0][0]
    assert "is_deleted" in str(call_args)


def test_restore(soft_repo: SoftDeletableRepository, mock_session: MagicMock):
    """Test restoring a soft-deleted record."""
    obj = create_mock_model(is_deleted=True)
    # Mock include_deleted() query
    mock_session.execute.return_value.scalars().first.return_value = obj

    result = soft_repo.restore(mock_session, obj_id=obj.id)

    assert result.is_deleted is False
    mock_session.flush.assert_called_once()


def test_hard_delete(soft_repo: SoftDeletableRepository, mock_session: MagicMock):
    """Test hard-delete permanently removes record."""
    obj = create_mock_model(is_deleted=True)
    mock_session.execute.return_value.scalars().first.return_value = obj

    soft_repo.hard_delete(mock_session, obj_id=obj.id)

    mock_session.delete.assert_called_once_with(obj)
    mock_session.flush.assert_called_once()


def test_upsert_invalid_match_field(repo: SQLRepository, mock_session: MagicMock):
    """Test upsert raises error for invalid match field."""
    schema = TestCreateSchema(name="Test", email="test@example.com")

    with pytest.raises(ValueError, match="Invalid match_fields"):
        repo.upsert(mock_session, obj_in=schema, match_fields=["invalid_field"])


def test_update_multi_empty_values(repo: SQLRepository, mock_session: MagicMock):
    """Test update_multi raises error for empty values."""
    with pytest.raises(ValueError, match="Update values cannot be empty"):
        repo.update_multi(mock_session, values={})


def test_soft_repo_on_non_soft_model():
    """Test SoftDeletableAsyncRepository raises error on non-soft-deletable model."""
    with pytest.raises(TypeError, match="soft_delete method"):
        SoftDeletableRepository(TrulyNonSoftModel)
