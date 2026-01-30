from uuid import uuid4

import pytest

from src.core.exceptions import LocationNotFoundError
from src.core.types import SwipeAction
from src.models.location import Location
from src.models.swipe import Swipe
from src.services.location import LocationService
from src.services.swipe import SwipeService


@pytest.mark.asyncio
class TestSwipeService:
    async def test_get_candidates(self, session, user_id, location, base_url):
        location2 = Location(
            id=uuid4(),
            name="Location 2",
            latitude=55.7558,
            longitude=37.6173,
            categories=["cafe"],
            tags=["cozy"],
        )
        session.add(location)
        session.add(location2)
        await session.commit()

        location_service = LocationService(session, base_url)
        service = SwipeService(session, location_service)
        result = await service.get_candidates(user_id, interests=["cozy"], limit=10)

        assert len(result) == 2

    async def test_get_candidates_excludes_swiped(self, session, user_id, location, base_url):
        location2 = Location(
            id=uuid4(),
            name="Location 2",
            latitude=55.7558,
            longitude=37.6173,
            categories=["cafe"],
        )
        swipe = Swipe(
            id=uuid4(),
            user_id=user_id,
            location_id=location.id,
            action=SwipeAction.LIKE,
        )
        session.add(location)
        session.add(location2)
        session.add(swipe)
        await session.commit()

        location_service = LocationService(session, base_url)
        service = SwipeService(session, location_service)
        result = await service.get_candidates(user_id, limit=10)

        assert len(result) == 1
        assert result[0][0].id == location2.id

    async def test_get_candidates_with_coordinates(self, session, user_id, location, base_url, coordinates):
        session.add(location)
        await session.commit()

        location_service = LocationService(session, base_url)
        service = SwipeService(session, location_service)
        result = await service.get_candidates(user_id, coordinates=coordinates, limit=10)

        assert len(result) == 1

    async def test_get_candidates_with_limit(self, session, user_id, base_url):
        for i in range(5):
            location = Location(
                id=uuid4(),
                name=f"Location {i}",
                latitude=55.7558,
                longitude=37.6173,
                categories=["cafe"],
            )
            session.add(location)
        await session.commit()

        location_service = LocationService(session, base_url)
        service = SwipeService(session, location_service)
        result = await service.get_candidates(user_id, limit=3)

        assert len(result) == 3

    async def test_create_swipe(self, session, user_id, location, location_id, base_url):
        session.add(location)
        await session.commit()

        location_service = LocationService(session, base_url)
        service = SwipeService(session, location_service)
        await service.create_swipe(user_id, location_id, SwipeAction.LIKE)

        from src.repositories.swipe import SwipeRepository

        repo = SwipeRepository(session)
        swiped_ids = await repo.get_swiped_location_ids(user_id)
        assert location_id in swiped_ids

    async def test_create_swipe_location_not_found(self, session, user_id, base_url):
        location_service = LocationService(session, base_url)
        service = SwipeService(session, location_service)

        with pytest.raises(LocationNotFoundError):
            await service.create_swipe(user_id, uuid4(), SwipeAction.LIKE)

    async def test_get_history(self, session, user_id, location, base_url):
        swipe1 = Swipe(
            id=uuid4(),
            user_id=user_id,
            location_id=location.id,
            action=SwipeAction.LIKE,
        )
        swipe2 = Swipe(
            id=uuid4(),
            user_id=user_id,
            location_id=location.id,
            action=SwipeAction.DISLIKE,
        )
        session.add(location)
        session.add(swipe1)
        session.add(swipe2)
        await session.commit()

        location_service = LocationService(session, base_url)
        service = SwipeService(session, location_service)
        result = await service.get_history(user_id)

        assert len(result) == 2

    async def test_get_history_with_filter(self, session, user_id, location, base_url):
        swipe1 = Swipe(
            id=uuid4(),
            user_id=user_id,
            location_id=location.id,
            action=SwipeAction.LIKE,
        )
        swipe2 = Swipe(
            id=uuid4(),
            user_id=user_id,
            location_id=location.id,
            action=SwipeAction.DISLIKE,
        )
        session.add(location)
        session.add(swipe1)
        session.add(swipe2)
        await session.commit()

        location_service = LocationService(session, base_url)
        service = SwipeService(session, location_service)
        result = await service.get_history(user_id, action_filter=SwipeAction.LIKE)

        assert len(result) == 1
        assert result[0].action == SwipeAction.LIKE

    async def test_get_history_with_limit(self, session, user_id, location, base_url):
        for _ in range(5):
            swipe = Swipe(
                id=uuid4(),
                user_id=user_id,
                location_id=location.id,
                action=SwipeAction.LIKE,
            )
            session.add(swipe)
        session.add(location)
        await session.commit()

        location_service = LocationService(session, base_url)
        service = SwipeService(session, location_service)
        result = await service.get_history(user_id, limit=3)

        assert len(result) == 3
