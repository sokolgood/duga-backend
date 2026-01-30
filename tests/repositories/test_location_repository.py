from uuid import uuid4

import pytest

from src.models.location import Location
from src.repositories.location import LocationRepository


@pytest.mark.asyncio
class TestLocationRepository:
    async def test_save(self, session, location):
        repo = LocationRepository(session)
        result = await repo.save(location)
        await session.commit()

        assert result.id == location.id
        assert result.name == location.name

    async def test_get_by_id_not_found(self, session, location_id):
        repo = LocationRepository(session)
        result = await repo.get_by_id(location_id)
        assert result is None

    async def test_get_by_id_found(self, session, location, location_id):
        session.add(location)
        await session.commit()

        repo = LocationRepository(session)
        result = await repo.get_by_id(location_id)
        assert result is not None
        assert result.id == location_id

    async def test_get_by_ids_empty_list(self, session):
        repo = LocationRepository(session)
        result = await repo.get_by_ids([])
        assert result == []

    async def test_get_by_ids(self, session, location):
        location2 = Location(
            id=uuid4(),
            name="Location 2",
            latitude=55.7558,
            longitude=37.6173,
            categories=["cafe"],
        )
        session.add(location)
        session.add(location2)
        await session.commit()

        repo = LocationRepository(session)
        result = await repo.get_by_ids([location.id, location2.id])
        assert len(result) == 2
        assert {loc.id for loc in result} == {location.id, location2.id}

    async def test_get_many(self, session, location):
        location2 = Location(
            id=uuid4(),
            name="Location 2",
            latitude=55.7558,
            longitude=37.6173,
            categories=["cafe"],
        )
        session.add(location)
        session.add(location2)
        await session.commit()

        repo = LocationRepository(session)
        result = await repo.get_many(skip=0, limit=10)
        assert len(result) == 2

    async def test_get_many_with_category(self, session, location):
        location2 = Location(
            id=uuid4(),
            name="Location 2",
            latitude=55.7558,
            longitude=37.6173,
            categories=["cafe"],
        )
        session.add(location)
        session.add(location2)
        await session.commit()

        repo = LocationRepository(session)
        result = await repo.get_many(skip=0, limit=10, category="restaurant")
        assert len(result) == 1
        assert result[0].id == location.id

    async def test_get_filtered_no_filters(self, session, location):
        session.add(location)
        await session.commit()

        repo = LocationRepository(session)
        result = await repo.get_filtered()
        assert len(result) == 1
        assert result[0][0].id == location.id

    async def test_get_filtered_with_exclude_ids(self, session, location):
        location2 = Location(
            id=uuid4(),
            name="Location 2",
            latitude=55.7558,
            longitude=37.6173,
            categories=["cafe"],
        )
        session.add(location)
        session.add(location2)
        await session.commit()

        repo = LocationRepository(session)
        result = await repo.get_filtered(exclude_ids=[location.id])
        assert len(result) == 1
        assert result[0][0].id == location2.id

    async def test_get_filtered_with_tags(self, session, location):
        location2 = Location(
            id=uuid4(),
            name="Location 2",
            latitude=55.7558,
            longitude=37.6173,
            categories=["cafe"],
            tags=["indoor"],
        )
        session.add(location)
        session.add(location2)
        await session.commit()

        repo = LocationRepository(session)
        result = await repo.get_filtered(tags=["cozy"])
        assert len(result) == 1
        assert result[0][0].id == location.id

    async def test_get_filtered_with_coordinates(self, session, location, coordinates):
        session.add(location)
        await session.commit()

        repo = LocationRepository(session)
        result = await repo.get_filtered(coordinates=coordinates, radius_km=10.0)
        assert len(result) == 1
        assert result[0][0].id == location.id
        assert result[0][1] is not None

    async def test_update(self, session, location):
        session.add(location)
        await session.commit()

        repo = LocationRepository(session)
        update_data = {"name": "Updated Name", "rating": 5.0}
        result = await repo.update(location, update_data)
        assert result.name == "Updated Name"
        assert result.rating == 5.0

    async def test_update_photo(self, session, photo):
        session.add(photo)
        await session.commit()

        repo = LocationRepository(session)
        photo.caption = "Updated Caption"
        result = await repo.update_photo(photo)
        assert result.caption == "Updated Caption"

    async def test_delete(self, session, location):
        session.add(location)
        await session.commit()

        repo = LocationRepository(session)
        await repo.delete(location)

        result = await repo.get_by_id(location.id)
        assert result is None

    async def test_commit(self, session, location):
        repo = LocationRepository(session)
        await repo.save(location)
        await repo.commit()

        result = await repo.get_by_id(location.id)
        assert result is not None

    async def test_rollback(self, session, location):
        repo = LocationRepository(session)
        await repo.save(location)
        await repo.rollback()

        result = await repo.get_by_id(location.id)
        assert result is None

    async def test_refresh(self, session, location):
        session.add(location)
        await session.commit()

        location.name = "Changed Name"
        repo = LocationRepository(session)
        await repo.refresh(location)
        assert location.name != "Changed Name"
