import logging
from uuid import UUID, uuid4

from fastapi import UploadFile, status
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import InvalidLocationDataError, LocationNotFoundError, PhotoNotFoundError
from src.models.location import Location, Photo
from src.repositories.location import LocationRepository
from src.services.file_storage import LocalFileStorage

logger = logging.getLogger(__name__)


class LocationService:
    def __init__(self, session: AsyncSession, base_url: str) -> None:
        self.session = session
        self.repository = LocationRepository(session)
        self.file_storage = LocalFileStorage()
        self.base_url = base_url.rstrip("")  # Убираем trailing slash если есть

    async def create_location(
        self,
        name: str,
        latitude: float,
        longitude: float,
        categories: list[str],
        tags: list[str] | None = None,
        instagram_url: HttpUrl | None = None,
        working_hours: str | None = None,
        address: str | None = None,
        description: str | None = None,
        rating: float | None = None,
        maps_url: HttpUrl | None = None,
    ) -> Location:
        try:
            location = Location(
                id=str(uuid4()),  # Генерируем ID заранее для создания папки
                name=name,
                latitude=latitude,
                longitude=longitude,
                categories=categories,
                tags=tags,
                instagram_url=str(instagram_url) if instagram_url else None,
                working_hours=working_hours,
                address=address,
                description=description,
                rating=rating,
                maps_url=str(maps_url) if maps_url else None,
            )

            location = await self.repository.save(location)
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
        maps_url: HttpUrl | None = None,
    ) -> Location | None:
        """Обновляет данные локации"""
        try:
            location = await self.repository.get_by_id(location_id)
            if not location:
                raise LocationNotFoundError()

            # Обновляем основные данные
            update_data = {
                "name": name,
                "categories": categories,
                "tags": tags,
                "instagram_url": str(instagram_url) if instagram_url else None,
                "working_hours": working_hours,
                "address": address,
                "description": description,
                "rating": rating,
                "maps_url": str(maps_url) if maps_url else None,
            }

            # Удаляем None значения
            update_data = {k: v for k, v in update_data.items() if v is not None}

            location = await self.repository.update(location, update_data)
            await self.repository.commit()
            await self.repository.refresh(location)
            return location

        except LocationNotFoundError:
            raise
        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Ошибка при обновлении локации {location_id}: {e!s}")
            raise InvalidLocationDataError(detail=str(e))

    async def delete_location(self, location_id: str) -> None:
        """Удаляет локацию и все её фотографии"""
        try:
            location = await self.get_location(location_id)

            # Удаляем все фото
            for photo in location.photos:
                try:
                    await self.file_storage.delete_file(location_id, photo.id)
                except Exception as e:
                    logger.error(f"Ошибка при удалении файла {photo.id}: {e!s}")

            await self.repository.delete(location)
            await self.session.commit()

        except LocationNotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка при удалении локации {location_id}: {e!s}")
            raise InvalidLocationDataError(detail="Ошибка при удалении локации")

    async def add_location_photos(self, location_id: str, files: list[UploadFile]) -> Location:
        """Добавляет фотографии к локации"""
        if not files:
            raise InvalidLocationDataError("Список файлов пуст")

        try:
            location = await self.get_location(location_id)

            # Получаем максимальный order существующих фото
            max_order = max((photo.order for photo in location.photos), default=0)

            new_photos = []
            saved_files = []

            try:
                for i, file in enumerate(files):
                    photo_id = uuid4()
                    relative_url = await self.file_storage.save_file(file, location_id, photo_id)
                    # Формируем полный URL
                    full_url = f"{self.base_url}{relative_url}"

                    new_photos.append(Photo(id=photo_id, photo_url=full_url, order=max_order + i + 1))
                    saved_files.append((location_id, photo_id))

                location.photos.extend(new_photos)
                await self.session.commit()
                await self.session.refresh(location)
                return location

            except Exception as e:
                # Откатываем сохраненные файлы в случае ошибки
                for loc_id, photo_id in saved_files:
                    try:
                        await self.file_storage.delete_file(loc_id, photo_id)
                    except Exception as del_error:
                        logger.error(f"Ошибка при удалении файла {photo_id}: {del_error}")
                raise e

        except LocationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при добавлении фото к локации {location_id}: {e!s}")
            raise InvalidLocationDataError(detail="Ошибка при добавлении фотографий")

    async def delete_location_photo(self, location_id: str, photo_id: str) -> Location:
        """Удаляет фотографию из локации"""
        try:
            location = await self.get_location(location_id)

            # Находим фото для удаления
            photo_to_delete = None
            for photo in location.photos:
                if str(photo.id) == photo_id:
                    photo_to_delete = photo
                    break

            if not photo_to_delete:
                raise PhotoNotFoundError()

            # Удаляем файл
            await self.file_storage.delete_file(location_id, photo_id)

            # Удаляем фото из списка
            location.photos.remove(photo_to_delete)

            # Обновляем order оставшихся фото
            deleted_order = photo_to_delete.order
            for photo in location.photos:
                if photo.order > deleted_order:
                    photo.order -= 1

            await self.session.commit()
            await self.session.refresh(location)
            return location

        except (LocationNotFoundError, PhotoNotFoundError):
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка при удалении фото {photo_id} из локации {location_id}: {e!s}")
            raise InvalidLocationDataError(detail="Ошибка при удалении фотографии")

    async def update_photo_caption(
        self,
        location_id: str,
        photo_id: str,
        caption: str,
    ) -> Location:
        """Обновляет подпись к фотографии"""
        try:
            location = await self.get_location(location_id)

            photo = next((p for p in location.photos if str(p.id) == photo_id), None)
            if not photo:
                raise PhotoNotFoundError()

            # Сохраняем текущий порядок
            current_order = photo.order

            # Обновляем подпись
            photo.caption = caption
            photo.order = current_order  # Явно устанавливаем порядок обратно

            await self.session.commit()
            await self.session.refresh(location)
            return location

        except (LocationNotFoundError, PhotoNotFoundError):
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка при обновлении подписи к фото {photo_id}: {e!s}")
            raise InvalidLocationDataError(detail="Ошибка при обновлении подписи к фото")

    async def reorder_photos(
        self,
        location_id: str,
        photo_order: list[str],
    ) -> Location:
        """Изменяет порядок фотографий"""
        try:
            location = await self.repository.get_by_id(location_id)
            if not location:
                raise LocationNotFoundError()

            if not photo_order:
                raise InvalidLocationDataError("Список photo_order не может быть пустым")

            # Проверяем, что все photo_id существуют
            existing_photos = {str(p.id): p for p in location.photos}
            missing_ids = [pid for pid in photo_order if pid not in existing_photos]
            if missing_ids:
                raise PhotoNotFoundError(f"Фотографии не найдены: {', '.join(missing_ids)}")

            # Проверяем, что все фотографии локации присутствуют в списке
            if len(photo_order) != len(location.photos):
                raise InvalidLocationDataError(
                    "Количество фотографий в запросе не совпадает с количеством фотографий локации"
                )

            # Обновляем order для каждой фотографии
            for new_order, photo_id in enumerate(photo_order):
                photo = existing_photos[photo_id]
                photo.order = new_order
                await self.repository.update_photo(photo)

            await self.repository.commit()
            await self.repository.refresh(location)
            return location

        except (LocationNotFoundError, PhotoNotFoundError, InvalidLocationDataError):
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Ошибка при изменении порядка фотографий: {e!s}")
            raise InvalidLocationDataError(detail="Ошибка при изменении порядка фотографий")

    async def get_location_by_id(self, location_id: UUID) -> Location | None:
        """Получает локацию по ID"""
        return await self.repository.get_by_id(location_id)

    async def get_locations_by_ids(self, location_ids: list[UUID]) -> list[Location]:
        """Получает информацию о нескольких локациях по их ID"""
        if not location_ids:
            return []

        return await self.repository.get_by_ids(location_ids)

    async def get_filtered_locations(
        self,
        exclude_ids: list[UUID] | None = None,
        tags: list[str] | None = None,
        coordinates: tuple[float, float] | None = None,
        radius_km: float = 5.0,
    ) -> list[Location]:
        """
        Получает отфильтрованный список локаций

        Args:
            exclude_ids: ID локаций, которые нужно исключить
            tags: список тегов для фильтрации
            coordinates: (lat, lng) координаты центра поиска
            radius_km: радиус поиска в километрах
        """
        return await self.repository.get_filtered(
            exclude_ids=exclude_ids, tags=tags, coordinates=coordinates, radius_km=radius_km
        )