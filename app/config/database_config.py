from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.config import settings
from app.entity.base import Base

# 1. Create the asynchronous database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=settings.SQL_LOG
)

# 2. Create the asynchronous session factory
# expire_on_commit=False prevents SQLAlchemy from throwing errors if you access an object after committing
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# 3. Create the FastAPI Dependency
# This generator function will be injected into your routes to provide a fresh, non-blocking database session per request
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Legacy alias for older imports and test utilities
get_database = get_db