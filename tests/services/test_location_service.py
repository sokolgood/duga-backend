from uuid import uuid4

import pytest
from pydantic import HttpUrl

from src.core.exceptions import InvalidLocationDataError, LocationNotFoundError, PhotoNotFoundError
from src.models.location import Location, Photo
from src.services.location import LocationService


@pytest.mark.asyncio
class TestLocationService:
    async def test_create_location(self, session, base_url):
        service = LocationService(session, base_url)
        location = await service.create_location(
            name="Test Location",
            latitude=55.7558,
            longitude=37.6173,
            categories=["restaurant"],
        )

        assert location.name == "Test Location"
        assert location.latitude == 55.7558
        assert location.longitude == 37.6173
        assert location.categories == ["restaurant"]

    async def test_create_location_with_all_fields(self, session, base_url):
        service = LocationService(session, base_url)
        location = await service.create_location(
            name="Test Location",
            latitude=55.7558,
            longitude=37.6173,
            categories=["restaurant"],
            tags=["cozy"],
            instagram_url=HttpUrl("https://instagram.com/test"),
            working_hours="9:00-18:00",
            address="Test Address",
            description="Test Description",
            rating=4.5,
            maps_url=HttpUrl("https://maps.google.com/test"),
        )

        assert location.name == "Test Location"
        assert location.tags == ["cozy"]
        assert location.instagram_url is not None
        assert location.working_hours == "9:00-18:00"

    async def test_get_location_not_found(self, session, base_url, location_id):
        service = LocationService(session, base_url)
        with pytest.raises(LocationNotFoundError):
            await service.get_location(str(location_id))

    async def test_get_location_found(self, session, base_url, location, location_id):
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        result = await service.get_location(str(location_id))
        assert result.id == location_id

    async def test_get_locations(self, session, base_url, location):
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

        service = LocationService(session, base_url)
        result = await service.get_locations()
        assert len(result) == 2

    async def test_get_locations_with_category(self, session, base_url, location):
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

        service = LocationService(session, base_url)
        result = await service.get_locations(category="restaurant")
        assert len(result) == 1
        assert result[0].id == location.id

    async def test_update_location(self, session, base_url, location, location_id):
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        updated = await service.update_location(
            str(location_id),
            name="Updated Name",
            rating=5.0,
        )

        assert updated.name == "Updated Name"
        assert updated.rating == 5.0

    async def test_update_location_not_found(self, session, base_url, location_id):
        service = LocationService(session, base_url)
        with pytest.raises(LocationNotFoundError):
            await service.update_location(str(location_id), name="Updated Name")

    async def test_delete_location(self, session, base_url, location, location_id):
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        await service.delete_location(str(location_id))

        with pytest.raises(LocationNotFoundError):
            await service.get_location(str(location_id))

    async def test_delete_location_not_found(self, session, base_url, location_id):
        service = LocationService(session, base_url)
        with pytest.raises(LocationNotFoundError):
            await service.delete_location(str(location_id))

    async def test_add_location_photos(self, session, base_url, location, location_id, mock_upload_file):
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        result = await service.add_location_photos(str(location_id), [mock_upload_file])

        assert len(result.photos) == 1
        assert result.photos[0].photo_url.startswith(base_url)

    async def test_add_location_photos_empty_list(self, session, base_url, location, location_id):
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        with pytest.raises(InvalidLocationDataError):
            await service.add_location_photos(str(location_id), [])

    async def test_delete_location_photo(self, session, base_url, location, location_id, photo):
        location.photos.append(photo)
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        result = await service.delete_location_photo(str(location_id), str(photo.id))

        assert len(result.photos) == 0

    async def test_delete_location_photo_not_found(self, session, base_url, location, location_id):
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        with pytest.raises(PhotoNotFoundError):
            await service.delete_location_photo(str(location_id), str(uuid4()))

    async def test_update_photo_caption(self, session, base_url, location, location_id, photo):
        location.photos.append(photo)
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        result = await service.update_photo_caption(str(location_id), str(photo.id), "New Caption")

        assert result.photos[0].caption == "New Caption"

    async def test_reorder_photos(self, session, base_url, location, location_id):
        photo1 = Photo(id=uuid4(), location_id=location_id, photo_url="url1", order=1)
        photo2 = Photo(id=uuid4(), location_id=location_id, photo_url="url2", order=2)
        location.photos = [photo1, photo2]
        session.add(location)
        await session.commit()

        # Сохраняем ID для проверки
        photo1_id = photo1.id
        photo2_id = photo2.id

        service = LocationService(session, base_url)
        result = await service.reorder_photos(str(location_id), [str(photo2_id), str(photo1_id)])

        # Проверяем, что photos отсортированы по order
        assert len(result.photos) == 2

        # Находим photos по ID для проверки
        result_photo1 = next((p for p in result.photos if p.id == photo1_id), None)
        result_photo2 = next((p for p in result.photos if p.id == photo2_id), None)

        assert result_photo1 is not None, "photo1 не найден в результате"
        assert result_photo2 is not None, "photo2 не найден в результате"

        # Проверяем order: photo2 должен быть первым (order=0), photo1 вторым (order=1)
        assert result_photo2.order == 0, f"photo2 должен иметь order=0, но имеет {result_photo2.order}"
        assert result_photo1.order == 1, f"photo1 должен иметь order=1, но имеет {result_photo1.order}"

    async def test_reorder_photos_invalid_order(self, session, base_url, location, location_id):
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        with pytest.raises(InvalidLocationDataError):
            await service.reorder_photos(str(location_id), [])

    async def test_get_location_by_id(self, session, base_url, location, location_id):
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        result = await service.get_location_by_id(location_id)
        assert result is not None
        assert result.id == location_id

    async def test_get_locations_by_ids(self, session, base_url, location):
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

        service = LocationService(session, base_url)
        result = await service.get_locations_by_ids([location.id, location2.id])
        assert len(result) == 2

    async def test_get_locations_by_ids_empty(self, session, base_url):
        service = LocationService(session, base_url)
        result = await service.get_locations_by_ids([])
        assert result == []

    async def test_get_filtered_locations(self, session, base_url, location, coordinates):
        session.add(location)
        await session.commit()

        service = LocationService(session, base_url)
        result = await service.get_filtered_locations(
            exclude_ids=None,
            tags=["cozy"],
            coordinates=coordinates,
            radius_km=10.0,
        )
        assert len(result) == 1
