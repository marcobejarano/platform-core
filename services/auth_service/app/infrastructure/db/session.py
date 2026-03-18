from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from services.auth_service.app.observability.decorators.db_healthcheck import (
    db_health_check_observed,
)
from services.auth_service.app.observability.decorators.db_session import (
    db_session_observed,
)
from services.auth_service.app.settings import settings

# -------------------------------------------------------------------
# Engine
# -------------------------------------------------------------------
engine: AsyncEngine = create_async_engine(
    settings.auth_service_database_uri.get_secret_value(),
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# -------------------------------------------------------------------
# Session factory
# -------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# -------------------------------------------------------------------
# FastAPI dependency
# -------------------------------------------------------------------
@db_session_observed(service="auth-service", db="auth")
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


# -------------------------------------------------------------------
# DB health check (normal async function)
# -------------------------------------------------------------------
@db_health_check_observed(service="auth-service", db="auth")
async def test_connection():
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
