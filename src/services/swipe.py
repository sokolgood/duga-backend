from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import LocationNotFoundError
from src.core.types import SwipeAction
from src.models.location import Location
from src.models.swipe import Swipe
from src.repositories.swipe import SwipeRepository
from src.services.location import LocationService


class SwipeService:
    def __init__(
        self,
        session: AsyncSession,
        location_service: LocationService,
    ) -> None:
        self.swipe_repo = SwipeRepository(session)
        self.location_service = location_service

    async def get_candidates(
        self,
        user_id: UUID,
        interests: list[str] | None = None,
        coordinates: tuple[float, float] | None = None,
        limit: int = 10,
    ) -> list[tuple[Location, float | None]]:
        # Получаем ID локаций, которые пользователь уже видел
        swiped_ids = await self.swipe_repo.get_swiped_location_ids(user_id)
        exclude_ids = list(set(swiped_ids))

        # Получаем новых кандидатов
        candidates = await self.location_service.get_filtered_locations(
            exclude_ids=exclude_ids, tags=interests, coordinates=coordinates
        )

        return candidates[:limit]

    async def create_swipe(self, user_id: UUID, location_id: UUID, action: SwipeAction) -> None:
        # Проверяем существование локации
        location = await self.location_service.get_location_by_id(location_id)
        if not location:
            raise LocationNotFoundError()

        await self.swipe_repo.create_swipe(user_id, location_id, action)

    async def get_history(
        self, user_id: UUID, limit: int = 20, offset: int = 0, action_filter: SwipeAction | None = None
    ) -> list[Swipe]:
        return await self.swipe_repo.get_user_swipes(
            user_id=user_id, limit=limit, offset=offset, action_filter=action_filter
        )
