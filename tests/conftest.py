from collections.abc import AsyncGenerator
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from faker import Faker
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.core.types import SwipeAction
from src.models import Base, Location, PhoneVerification, Photo, User
from src.models.swipe import Swipe

fake = Faker("ru_RU")

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def user_id() -> UUID:
    return uuid4()


@pytest.fixture
def location_id() -> UUID:
    return uuid4()


@pytest.fixture
def phone_number() -> str:
    return fake.phone_number()


@pytest.fixture
def email() -> str:
    return fake.email()


@pytest.fixture
def user(user_id: UUID, phone_number: str) -> User:
    return User(
        id=user_id,
        phone_number=phone_number,
        email=fake.email(),
        city="moscow",
        is_phone_verified=True,
        full_name=fake.name(),
        preferences=["restaurant", "cafe"],
    )


@pytest.fixture
def location(location_id: UUID) -> Location:
    return Location(
        id=location_id,
        name=fake.company(),
        latitude=55.7558,
        longitude=37.6173,
        categories=["restaurant", "cafe"],
        tags=["cozy", "outdoor"],
        address=fake.address(),
        description=fake.text(),
        rating=4.5,
    )


@pytest.fixture
def photo(location_id: UUID) -> Photo:
    return Photo(
        id=uuid4(),
        location_id=location_id,
        photo_url="https://example.com/photo.jpg",
        caption="Test photo",
        order=1,
    )


@pytest.fixture
def swipe(user_id: UUID, location_id: UUID) -> Swipe:
    return Swipe(
        id=uuid4(),
        user_id=user_id,
        location_id=location_id,
        action=SwipeAction.LIKE,
    )


@pytest.fixture
def phone_verification(phone_number: str) -> PhoneVerification:
    return PhoneVerification(
        id=uuid4(),
        phone_number=phone_number,
        code="1234",
        expires_at=datetime.now() + timedelta(minutes=5),
    )


@pytest.fixture
def expired_phone_verification(phone_number: str) -> PhoneVerification:
    return PhoneVerification(
        id=uuid4(),
        phone_number=phone_number,
        code="5678",
        expires_at=datetime.now() - timedelta(minutes=1),
    )


@pytest.fixture
def mock_upload_file(tmp_path: Path) -> UploadFile:
    file_path = tmp_path / "test_image.jpg"
    file_path.write_bytes(b"fake image content")
    file_obj = open(file_path, "rb")
    return UploadFile(
        filename="test_image.jpg",
        file=file_obj,
    )


class TestSettings:
    secret_key: str = "test-secret-key"
    algorithm: str = "HS256"
    access_token_expire_days: int = 7
    file_storage_path: str = "http://localhost:8080"


@pytest.fixture
def settings() -> TestSettings:
    return TestSettings()


@pytest.fixture
def base_url() -> str:
    return "http://localhost:8080"


@pytest.fixture
def coordinates() -> tuple[float, float]:
    return (55.7558, 37.6173)


@pytest.fixture
def mock_file_storage_path(tmp_path: Path) -> Path:
    storage_path = tmp_path / "test_storage"
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path
