from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings, get_settings
from src.core.database import get_session
from src.models import User
from src.services.auth import AuthService
from src.services.location import LocationService
from src.services.s3 import S3Service
from src.services.user import UserService

security = HTTPBearer()


def get_auth_service(
    session: AsyncSession = Depends(get_session), settings: Settings = Depends(get_settings)
) -> AuthService:
    return AuthService(
        session=session,
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        token_expire_days=settings.access_token_expire_days,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.get_current_user(credentials.credentials)


def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(session=session)


# def get_s3_service(
#     settings: Settings = Depends(get_settings),
# ) -> S3Service:
#     return S3Service(s3_params=settings.s3_params, s3_bucket=settings.s3_bucket)


class MockS3Service:
    from fastapi import UploadFile

    async def upload_file(self, file: UploadFile, path: str) -> str:
        return "https://example.com/file.jpg"


def get_s3_service() -> S3Service:
    return MockS3Service()


def get_location_service(
    session: AsyncSession = Depends(get_session),
) -> LocationService:
    return LocationService(session=session)
