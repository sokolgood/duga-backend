from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models import User
from src.repositories.user import UserRepository


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.user_repo = UserRepository(session)

    async def update_user(
        self,
        user: User,
        email: str | None = None,
        full_name: str | None = None,
        preferences: list[str] | None = None,
    ) -> User:
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if preferences is not None:
            user.preferences = preferences

        return await self.user_repo.update(user)
