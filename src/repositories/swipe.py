from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.types import SwipeAction
from src.models.swipe import Swipe


class SwipeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_swipe(self, user_id: UUID, location_id: UUID, action: SwipeAction) -> Swipe:
        swipe = Swipe(user_id=user_id, location_id=location_id, action=action)
        self.session.add(swipe)
        await self.session.commit()
        return swipe

    async def get_user_swipes(
        self, user_id: UUID, limit: int = 20, offset: int = 0, action_filter: SwipeAction | None = None
    ) -> list[Swipe]:
        query = select(Swipe).where(Swipe.user_id == user_id).options(selectinload(Swipe.location))

        if action_filter:
            query = query.where(Swipe.action == action_filter)

        query = query.order_by(Swipe.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_swiped_location_ids(self, user_id: UUID) -> list[UUID]:
        query = select(Swipe.location_id).where(Swipe.user_id == user_id)
        result = await self.session.execute(query)
        return [row[0] for row in result]
