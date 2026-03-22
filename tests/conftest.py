from collections.abc import AsyncIterator

import pytest_asyncio
import fakeredis.aioredis as fake_aioredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.api import create_app
from src.api.deps import get_redis
from src.config import settings
from src.domain.enums import ResourceType
from src.infra.models import Base, Item, Role, RolePermission, User
from src.infra.session import get_async_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

settings.database_url = TEST_DATABASE_URL

@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        yield engine
    finally:
        await engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def test_session_maker(test_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(test_engine, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_schema(test_engine: AsyncEngine) -> AsyncIterator[None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

@pytest_asyncio.fixture(scope="session")
async def redis_client() -> AsyncIterator[fake_aioredis.FakeRedis]:
    redis = fake_aioredis.FakeRedis(decode_responses=True)

    await redis.flushdb()
    try:
        yield redis
    finally:
        await redis.flushdb()
        await redis.aclose()

@pytest_asyncio.fixture(scope="session")
async def app(
    test_session_maker: async_sessionmaker[AsyncSession],
    redis_client: fake_aioredis.FakeRedis,
):
    application = create_app()

    async def override_get_async_session() -> AsyncIterator[AsyncSession]:
        async with test_session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()

    async def override_get_redis() -> fake_aioredis.FakeRedis:
        return redis_client

    application.dependency_overrides[get_async_session] = override_get_async_session
    application.dependency_overrides[get_redis] = override_get_redis

    yield application

    application.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client

@pytest_asyncio.fixture(autouse=True)
async def clean_state(
    test_session_maker: async_sessionmaker[AsyncSession],
    redis_client: fake_aioredis.FakeRedis,
) -> None:
    async with test_session_maker() as session:
        await session.execute(delete(RolePermission))
        await session.execute(delete(User))
        await session.execute(delete(Role))
        await session.execute(delete(Item))
        await session.commit()

    await redis_client.flushdb()

@pytest_asyncio.fixture(autouse=True)
async def seed_roles(
    clean_state: None,
    test_session_maker: async_sessionmaker[AsyncSession],
) -> dict[str, int]:
    async with test_session_maker() as session:
        admin = Role(name="admin")
        moderator = Role(name="moderator")
        user = Role(name="user")
        session.add_all([admin, moderator, user])
        await session.flush()

        for resource in ResourceType:
            session.add(
                RolePermission(
                    role_id=admin.id,
                    resource=resource,
                    can_read=True,
                    can_write=True,
                    can_delete=True,
                )
            )

        session.add(
            RolePermission(
                role_id=moderator.id,
                resource=ResourceType.ITEMS,
                can_read=True,
                can_write=True,
                can_delete=True,
            )
        )
        session.add(
            RolePermission(
                role_id=moderator.id,
                resource=ResourceType.USERS,
                can_read=True,
                can_write=False,
                can_delete=False,
            )
        )
        session.add(
            RolePermission(
                role_id=moderator.id,
                resource=ResourceType.ROLES,
                can_read=False,
                can_write=False,
                can_delete=False,
            )
        )

        session.add(
            RolePermission(
                role_id=user.id,
                resource=ResourceType.ITEMS,
                can_read=True,
                can_write=False,
                can_delete=False,
            )
        )
        session.add(
            RolePermission(
                role_id=user.id,
                resource=ResourceType.USERS,
                can_read=False,
                can_write=False,
                can_delete=False,
            )
        )
        session.add(
            RolePermission(
                role_id=user.id,
                resource=ResourceType.ROLES,
                can_read=False,
                can_write=False,
                can_delete=False,
            )
        )

        await session.commit()

        return {
            "admin": admin.id,
            "moderator": moderator.id,
            "user": user.id,
        }