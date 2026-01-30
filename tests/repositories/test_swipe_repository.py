from uuid import uuid4

import pytest

from src.core.types import SwipeAction
from src.models.swipe import Swipe
from src.repositories.swipe import SwipeRepository


@pytest.mark.asyncio
class TestSwipeRepository:
    async def test_create_swipe(self, session, user_id, location_id):
        repo = SwipeRepository(session)
        result = await repo.create_swipe(user_id, location_id, SwipeAction.LIKE)
        assert result.user_id == user_id
        assert result.location_id == location_id
        assert result.action == SwipeAction.LIKE

    async def test_get_user_swipes(self, session, swipe, user_id):
        swipe2 = Swipe(
            id=uuid4(),
            user_id=user_id,
            location_id=uuid4(),
            action=SwipeAction.DISLIKE,
        )
        session.add(swipe)
        session.add(swipe2)
        await session.commit()

        repo = SwipeRepository(session)
        result = await repo.get_user_swipes(user_id, limit=10, offset=0)
        assert len(result) == 2

    async def test_get_user_swipes_with_filter(self, session, swipe, user_id):
        swipe2 = Swipe(
            id=uuid4(),
            user_id=user_id,
            location_id=uuid4(),
            action=SwipeAction.DISLIKE,
        )
        session.add(swipe)
        session.add(swipe2)
        await session.commit()

        repo = SwipeRepository(session)
        result = await repo.get_user_swipes(user_id, limit=10, offset=0, action_filter=SwipeAction.LIKE)
        assert len(result) == 1
        assert result[0].action == SwipeAction.LIKE

    async def test_get_user_swipes_with_limit(self, session, user_id):
        for _ in range(5):
            swipe = Swipe(
                id=uuid4(),
                user_id=user_id,
                location_id=uuid4(),
                action=SwipeAction.LIKE,
            )
            session.add(swipe)
        await session.commit()

        repo = SwipeRepository(session)
        result = await repo.get_user_swipes(user_id, limit=3, offset=0)
        assert len(result) == 3

    async def test_get_swiped_location_ids(self, session, swipe, user_id, location_id):
        location_id2 = uuid4()
        swipe2 = Swipe(
            id=uuid4(),
            user_id=user_id,
            location_id=location_id2,
            action=SwipeAction.DISLIKE,
        )
        session.add(swipe)
        session.add(swipe2)
        await session.commit()

        repo = SwipeRepository(session)
        result = await repo.get_swiped_location_ids(user_id)
        assert len(result) == 2
        assert location_id in result
        assert location_id2 in result

    async def test_get_swiped_location_ids_empty(self, session, user_id):
        repo = SwipeRepository(session)
        result = await repo.get_swiped_location_ids(user_id)
        assert result == []
