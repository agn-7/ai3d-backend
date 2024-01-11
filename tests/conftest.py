import pytest_asyncio

from contextlib import contextmanager
from unittest.mock import patch

from sqlalchemy.ext.asyncio import AsyncSession

from . import client
from ai3d import utils


@pytest_asyncio.fixture()
async def db() -> AsyncSession:
    async with client.async_session() as session:
        await client.create_tables()
        yield session
        await client.drop_tables()


@pytest_asyncio.fixture()
@contextmanager
def mock_get_hashed_password():
    original_get_hashed_password = utils.get_hashed_password
    try:
        # Mocking utils.get_hashed_password function
        def mock_get_hashed_password(password: str) -> str:
            return "hashed" + password

        utils.get_hashed_password = mock_get_hashed_password
        yield
    finally:
        # Unmocking the original function
        utils.get_hashed_password = original_get_hashed_password


@pytest_asyncio.fixture
def mock_generate_ai_response():
    with patch("ai3d.modules.generate_ai_response") as mock:
        mock.return_value = "AI response"
        yield mock
