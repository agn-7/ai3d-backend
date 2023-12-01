from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from .config import settings

engine: AsyncEngine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.unicode_string()
)
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    future=True,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
