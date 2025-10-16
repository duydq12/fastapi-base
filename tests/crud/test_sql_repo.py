"""Unit tests for SQLRepository (synchronous CRUD) in fastapi_base.

Covers create, read, update, and soft delete operations using a mock SQLAlchemy model and session.
"""
import uuid
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel
from sqlalchemy import UUID as UUID_SQL
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_base.crud.sql_repo import SQLRepository
from fastapi_base.model import Base


class MockModel(Base):
    """Mock SQLAlchemy model for testing SQLRepository.

    Table: mock_items
    Fields:
        - id: UUID primary key
        - name: string
        - is_deleted: boolean (soft delete flag)
    """
    __tablename__ = "mock_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID_SQL, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")


class MockCreateSchema(BaseModel):
    """Pydantic schema for creating a MockModel object."""
    name: str


class MockUpdateSchema(BaseModel):
    """Pydantic schema for updating a MockModel object."""
    name: str


@pytest.fixture
def repo_setup():
    """Provides a consistent setup for repository tests.

    Yields:
        A tuple containing the repository instance, a mock model instance,
        and the mock session.
    """
    # 1. Create a mock item that will be "found" in the database
    obj_id = uuid.uuid4()
    mock_item = MockModel(id=obj_id, name="initial_name")

    # 2. Set up the mock session and the chain of query calls
    mock_session = MagicMock()
    query_chain = mock_session.query.return_value.filter.return_value
    query_chain.first.return_value = mock_item

    # 3. Create the repository instance
    repo = SQLRepository(MockModel)

    return repo, mock_item, mock_session, query_chain


def test_get_object(repo_setup):
    """Tests retrieving an object by ID."""
    repo, mock_item, mock_session, _ = repo_setup

    result = repo.get(mock_session, mock_item.id)

    mock_session.query.assert_called_once_with(MockModel)
    assert result is not None
    assert result.id == mock_item.id
    assert result.name == "initial_name"


def test_create_object(repo_setup):
    """Tests creating a new object."""
    repo, _, mock_session, _ = repo_setup
    create_schema = MockCreateSchema(name="new_item_name")

    created_obj = repo.create(mock_session, obj_in=create_schema)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert created_obj.name == "new_item_name"


def test_update_object(repo_setup):
    """Tests updating an existing object."""
    repo, mock_item, mock_session, query_chain = repo_setup
    update_schema = MockUpdateSchema(name="updated_name")

    result = repo.update(mock_session, obj_id=mock_item.id, obj_in=update_schema)

    query_chain.update.assert_called_once_with({"name": "updated_name"})
    mock_session.commit.assert_called_once()
    assert result == update_schema


def test_delete_object(repo_setup):
    """Tests soft-deleting an object."""
    repo, mock_item, mock_session, query_chain = repo_setup

    repo.delete(mock_session, obj_id=mock_item.id)

    query_chain.update.assert_called_once_with({"is_deleted": True})
    mock_session.commit.assert_called_once()
