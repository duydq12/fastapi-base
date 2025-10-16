"""Unit tests for SQLAsyncRepository (asynchronous CRUD) in fastwings.

Covers async create and get operations using a mock SQLAlchemy model and async session.
"""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from fastwings.crud.sql_async_repo import SQLAsyncRepository
from fastwings.model import Base


class MockModel(Base):
    """Mock SQLAlchemy model for testing SQLAsyncRepository.

    Table: async_mock_items
    Fields:
        - id: integer primary key
        - name: string
        - is_deleted: boolean (soft delete flag)
    """
    __tablename__ = "async_mock_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")


class MockCreateSchema(BaseModel):
    """Pydantic schema for creating a MockModel object asynchronously."""
    name: str


class MockUpdateSchema(BaseModel):
    """Pydantic schema for updating a MockModel object asynchronously."""
    name: str


@pytest.fixture
def repo_setup():
    """Provides a consistent setup for repository tests.

    Yields:
        A tuple containing the repository instance, the mock model instance,
        and the mock session.
    """
    # 1. Create a mock item that will be "found" in the database
    obj_id = uuid.uuid4()
    mock_item = MockModel(id=obj_id, name="initial_name")

    # 2. Set up the mock session
    mock_session = AsyncMock()

    # 1. Mock the session.scalars(...) call used by the .get() method
    mock_scalars_result = MagicMock()
    mock_scalars_result.first.return_value = mock_item
    mock_session.scalars.return_value = mock_scalars_result

    # 2. Mock the session.execute(...) call used by .update() and .delete()
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.first.return_value = mock_item
    mock_session.execute.return_value = mock_execute_result

    # 3. The `add` method is synchronous, so replace it with a standard mock
    mock_session.add = MagicMock()

    # 4. Create the repository instance
    repo = SQLAsyncRepository(MockModel)

    return repo, mock_item, mock_session


@pytest.mark.asyncio
async def test_async_get_object(repo_setup):
    """Tests retrieving an object asynchronously using the scalars() path."""
    repo, mock_item, mock_session = repo_setup

    result = await repo.get(mock_session, mock_item.id)

    # Assert that the correct method, scalars(), was awaited.
    mock_session.scalars.assert_awaited_once()
    assert result is not None
    assert result.id == mock_item.id


@pytest.mark.asyncio
async def test_async_create_object(repo_setup):
    """Tests creating an object asynchronously."""
    repo, _, mock_session = repo_setup
    create_schema = MockCreateSchema(name="new_item_name")

    # The `create` method should return the newly created object
    created_obj = await repo.create(mock_session, obj_in=create_schema)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()
    assert created_obj.name == "new_item_name"


@pytest.mark.asyncio
async def test_async_update_object(repo_setup):
    """Tests updating an object asynchronously."""
    repo, mock_item, mock_session = repo_setup
    update_schema = MockUpdateSchema(name="updated_name")

    result = await repo.update(mock_session, obj_id=mock_item.id, obj_in=update_schema)

    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(mock_item)
    assert mock_item.name == "updated_name"
    assert result == update_schema


@pytest.mark.asyncio
async def test_async_delete_object(repo_setup):
    """Tests deleting an object asynchronously."""
    repo, mock_item, mock_session = repo_setup

    await repo.delete(mock_session, obj_id=mock_item.id)

    mock_session.execute.assert_awaited_once()
    mock_session.delete.assert_awaited_once_with(mock_item)
    mock_session.commit.assert_awaited_once()
