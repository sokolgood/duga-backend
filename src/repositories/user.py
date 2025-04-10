from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import PhoneVerification, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_phone(self, phone_number: str) -> User | None:
        result = await self.session.execute(select(User).where(User.phone_number == phone_number))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_verification(self, phone_number: str) -> PhoneVerification | None:
        result = await self.session.execute(
            select(PhoneVerification)
            .where(PhoneVerification.phone_number == phone_number)
            .where(PhoneVerification.expires_at > datetime.now())
        )
        return result.scalar_one_or_none()

    async def create_verification(self, verification: PhoneVerification) -> PhoneVerification:
        self.session.add(verification)
        await self.session.commit()
        return verification

    async def delete_verification(self, verification: PhoneVerification) -> None:
        await self.session.delete(verification)
        await self.session.commit()
