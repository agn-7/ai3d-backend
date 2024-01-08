import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from . import client
from ai3d import utils


@pytest_asyncio.fixture()
async def db() -> AsyncSession:
    async with client.async_session() as session:
        await client.create_tables()
        yield session
        await client.drop_tables()


# Mocking utils.get_hashed_password function
def mock_get_hashed_password(password: str) -> str:
    return "hashed" + password

utils.get_hashed_password = mock_get_hashed_password
