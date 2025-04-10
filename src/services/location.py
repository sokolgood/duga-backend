from uuid import uuid4

from fastapi import UploadFile
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import InvalidLocationDataError, LocationNotFoundError
from src.models.location import Location, Photo
from src.repositories.location import LocationRepository
from src.services.s3 import S3Service


class LocationService:
    def __init__(self, session: AsyncSession, s3_service: S3Service) -> None:
        self.repository = LocationRepository(session)
        self.s3_service = s3_service

    async def create_location(
        self,
        name: str,
        latitude: float,
        longitude: float,
        categories: list[str],
        tags: list[str] | None = None,
        instagram_url: str | None = None,
        working_hours: str | None = None,
        address: str | None = None,
        description: str | None = None,
        rating: float | None = None,
        photos: list[UploadFile] | None = None,
    ) -> Location:
        try:
            location = Location(
                name=name,
                latitude=latitude,
                longitude=longitude,
                categories=categories,
                tags=tags,
                instagram_url=instagram_url,
                working_hours=working_hours,
                address=address,
                description=description,
                rating=rating,
            )

            location = await self.repository.save(location)

            if photos:
                photo_objects = []
                for photo in photos:
                    photo_url = await self.s3_service.upload_file(file=photo, folder=f"locations/{location.id}")
                    photo_objects.append(Photo(id=str(uuid4()), location_id=location.id, photo_url=photo_url))

                await self.repository.save_photos(photo_objects)

            await self.repository.commit()
            return location

        except Exception as e:
            await self.repository.rollback()
            raise InvalidLocationDataError(detail=str(e))

    async def get_location(self, location_id: str) -> Location | None:
        location = await self.repository.get_by_id(location_id)
        if not location:
            raise LocationNotFoundError()
        return location

    async def get_locations(self, skip: int = 0, limit: int = 100, category: str | None = None) -> list[Location]:
        """Получает список локаций"""
        return await self.repository.get_many(skip, limit, category)

    async def update_location(
        self,
        location_id: str,
        name: str | None = None,
        categories: list[str] | None = None,
        tags: list[str] | None = None,
        instagram_url: HttpUrl | None = None,
        working_hours: str | None = None,
        address: str | None = None,
        description: str | None = None,
        rating: float | None = None,
        photos: list[UploadFile] | None = None,
    ) -> Location | None:
        try:
            location = await self.repository.get_by_id(location_id)
            if not location:
                raise LocationNotFoundError()

            # Обновляем основные данные
            update_data = {
                "name": name,
                "categories": categories,
                "tags": tags,
                "instagram_url": instagram_url,
                "working_hours": working_hours,
                "address": address,
                "description": description,
                "rating": rating,
            }
            location = await self.repository.update(location, update_data)

            # Загружаем новые фотографии, если они есть
            if photos:
                photo_objects = []
                for photo in photos:
                    photo_url = await self.s3_service.upload_file(file=photo, folder=f"locations/{location.id}")
                    photo_objects.append(Photo(id=str(uuid4()), location_id=location.id, photo_url=photo_url))

                await self.repository.save_photos(photo_objects)

            await self.repository.commit()
            await self.repository.refresh(location)
            return location

        except Exception as e:
            await self.repository.rollback()
            raise InvalidLocationDataError(detail=str(e))

    async def delete_location(self, location_id: str) -> bool:
        """Удаляет локацию"""
        try:
            location = await self.repository.get_by_id(location_id)
            if not location:
                return False

            # Удаляем фотографии из S3
            for photo in location.photos:
                await self.s3_service.delete_file(photo.photo_url)

            # Удаляем локацию из БД
            await self.repository.delete(location)
            await self.repository.commit()
            return True

        except Exception as e:
            await self.repository.rollback()
            raise InvalidLocationDataError(detail=str(e))
