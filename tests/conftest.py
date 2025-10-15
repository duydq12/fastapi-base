"""Pytest configuration and fixtures for fastapi_base test suite.

Provides mock database session objects for synchronous and asynchronous tests.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_db_session():
    """Provides a MagicMock for the synchronous SQLAlchemy session.

    Mocks query, filter, first, and update methods for repository tests.
    """
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = MagicMock()
    session.query.return_value.filter.return_value.update.return_value = None
    return session

@pytest.fixture
def mock_async_db_session():
    """Provides an AsyncMock for the asynchronous SQLAlchemy session.

    Mocks execute and scalars chain for async repository tests.
    """
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = AsyncMock()
    session.execute.return_value = mock_result
    return session
