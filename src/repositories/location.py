from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.location import Location, Photo


class LocationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, location: Location) -> Location:
        """Сохраняет локацию в БД"""
        self.session.add(location)
        return location

    async def save_photos(self, photos: list[Photo]) -> None:
        """Сохраняет фотографии в БД"""
        for photo in photos:
            self.session.add(photo)

    async def get_by_id(self, location_id: str) -> Location | None:
        """Получает локацию по ID"""
        query = select(Location).options(selectinload(Location.photos)).where(Location.id == location_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_many(self, skip: int = 0, limit: int = 100, category: str | None = None) -> list[Location]:
        """Получает список локаций с фильтрацией по категории"""
        query = select(Location).options(selectinload(Location.photos)).offset(skip).limit(limit)

        if category:
            query = query.where(Location.categories.contains([category]))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, location: Location, update_data: dict) -> Location:
        """Обновляет данные локации"""
        for field, value in update_data.items():
            setattr(location, field, value)
        return location

    async def delete(self, location: Location) -> None:
        """Удаляет локацию из БД"""
        await self.session.delete(location)

    async def commit(self) -> None:
        """Сохраняет изменения в БД"""
        await self.session.commit()

    async def rollback(self) -> None:
        """Откатывает изменения в БД"""
        await self.session.rollback()

    async def refresh(self, location: Location) -> None:
        """Обновляет состояние объекта из БД"""
        await self.session.refresh(location)
