from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings, get_settings
from src.core.database import get_session
from src.models import User
from src.services.auth import AuthService

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
