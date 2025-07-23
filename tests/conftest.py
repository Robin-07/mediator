import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from mediator.main import app
from mediator.core.database import Base, get_session

# Use a separate test DB
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/test_db"

engine_test = create_async_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


async def override_get_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="session")
async def setup_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client(setup_test_db):
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac
