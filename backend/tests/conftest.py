import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.session import Base
from app.db import session as db_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def prepare_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    # override app's session engine and sessionmaker for tests
    db_session.engine = engine
    db_session.AsyncSessionLocal = async_session
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

@pytest.fixture
async def client(prepare_db):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac
