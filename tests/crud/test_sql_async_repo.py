"""Unit tests for SQLAsyncRepository (asynchronous CRUD) in fastapi_base.

Covers async create and get operations using a mock SQLAlchemy model and async session.
"""
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_base.crud.sql_async_repo import SQLAsyncRepository
from fastapi_base.model import Base


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

@pytest.mark.asyncio
async def test_async_get_object(mock_async_db_session):
    """Tests retrieving an object asynchronously by ID using SQLAsyncRepository.get().

    Asserts that the returned object matches the mock and is not None.
    """
    mock_item = MockModel(name="async_item", id=1)
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_item
    mock_async_db_session.scalars.return_value = mock_scalars
    repo = SQLAsyncRepository(MockModel)
    result = await repo.get(mock_async_db_session, 1)
    mock_async_db_session.scalars.assert_called_once()
    assert result is not None
    assert result.name == "async_item"

@pytest.mark.asyncio
async def test_async_create_object(mock_async_db_session):
    """Tests creating an object asynchronously using SQLAsyncRepository.create().

    Asserts that the created object has the expected name and session methods are called.
    """
    repo = SQLAsyncRepository(MockModel)
    create_schema = MockCreateSchema(name="new_async_item")
    db_obj = await repo.create(mock_async_db_session, obj_in=create_schema)
    mock_async_db_session.add.assert_called_once()
    mock_async_db_session.commit.assert_awaited_once()
    mock_async_db_session.refresh.assert_awaited_once()
    assert db_obj.name == "new_async_item"
