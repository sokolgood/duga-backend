from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Float

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

    async def get_by_id(self, location_id: UUID) -> Location | None:
        """Получает локацию по ID"""
        query = select(Location).where(Location.id == location_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, location_ids: list[UUID]) -> list[Location]:
        """Получает список локаций по их ID"""
        if not location_ids:
            return []

        query = select(Location).where(Location.id.in_(location_ids))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_filtered(
        self,
        exclude_ids: list[UUID] | None = None,
        tags: list[str] | None = None,
        coordinates: tuple[float, float] | None = None,
        radius_km: float = 5.0,
    ) -> list[tuple[Location, float | None]]:
        """
        Получает отфильтрованный список локаций с расстояниями

        Args:
            exclude_ids: ID локаций для исключения
            tags: список тегов для фильтрации
            coordinates: (lat, lng) координаты центра поиска
            radius_km: радиус поиска в километрах

        Returns:
            list[tuple[Location, float | None]]: Список кортежей (локация, расстояние в км)
        """
        # Начинаем с базового запроса
        query = select(Location)

        # Применяем базовые фильтры
        conditions = []

        # Исключаем локации по ID
        if exclude_ids:
            conditions.append(Location.id.notin_(exclude_ids))

        # Фильтруем по тегам
        if tags:
            # Для поиска локаций с хотя бы одним из тегов
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(Location.tags.cast(JSONB).contains([tag]))
            conditions.append(or_(*tag_conditions))

        # Применяем базовые условия
        if conditions:
            query = query.where(and_(*conditions))

        # Если нет координат, просто возвращаем отфильтрованные локации
        if not coordinates:
            query = query.order_by(func.random())
            result = await self.session.execute(query)
            return [(row, None) for row in result.scalars().all()]

        # Если есть координаты, добавляем расчет расстояния
        lat, lng = coordinates
        radius_earth_km = 6371.0  # Радиус Земли в км

        # Конвертируем координаты в радианы
        lat_rad = func.radians(cast(lat, Float))
        lng_rad = func.radians(cast(lng, Float))
        lat2_rad = func.radians(cast(Location.latitude, Float))
        lng2_rad = func.radians(cast(Location.longitude, Float))

        # Разница координат
        dlat = lat2_rad - lat_rad
        dlng = lng2_rad - lng_rad

        # Формула гаверсинусов
        a = func.pow(func.sin(dlat / 2), 2) + func.cos(lat_rad) * func.cos(lat2_rad) * func.pow(func.sin(dlng / 2), 2)

        c = 2 * func.asin(func.sqrt(a))
        distance = (radius_earth_km * c).label("distance")

        # Добавляем расчет расстояния к основному запросу
        query = (
            select(Location, distance)
            .where(and_(*conditions) if conditions else True)
            .where(distance <= radius_km)
            .order_by(distance)
        )

        result = await self.session.execute(query)
        locations = result.all()
        return [(location[0], location[1]) for location in locations]

    async def get_many(self, skip: int = 0, limit: int = 100, category: str | None = None) -> list[Location]:
        """Получает список локаций с пагинацией и фильтрацией по категории"""
        query = select(Location).options(selectinload(Location.photos))

        if category:
            query = query.where(Location.categories.contains([category]))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, location: Location, update_data: dict) -> Location:
        """Обновляет данные локации"""
        for key, value in update_data.items():
            if value is not None:
                setattr(location, key, value)
        return location

    async def update_photo(self, photo: Photo) -> Photo:
        """Обновляет данные фотографии"""
        self.session.add(photo)
        return photo

    async def delete_photo(self, photo: Photo) -> None:
        """Удаляет фотографию из БД"""
        await self.session.delete(photo)

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
        """Обновляет данные локации из БД"""
        await self.session.refresh(location)
