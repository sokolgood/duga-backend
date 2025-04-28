import logging

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile, status

from src.api.deps import get_location_service
from src.schemas.location import (
    LocationCreate,
    LocationCreateResponse,
    LocationResponse,
    LocationUpdate,
    PhotoReorderRequest,
)
from src.services.location import LocationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationResponse])
async def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: str | None = None,
    location_service: LocationService = Depends(get_location_service),
) -> list[LocationResponse]:
    """Получение списка локаций с пагинацией и фильтрацией по категории"""
    locations = await location_service.get_locations(skip=skip, limit=limit, category=category)
    return [LocationResponse.model_validate(loc).model_dump() for loc in locations]


@router.post("", response_model=LocationResponse)
async def create_location(
    data: LocationCreate, location_service: LocationService = Depends(get_location_service)
) -> LocationCreateResponse:
    """Создание локации без фотографий"""
    location = await location_service.create_location(
        name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
        categories=data.categories,
        tags=data.tags,
        instagram_url=data.instagram_url,
        working_hours=data.working_hours,
        address=data.address,
        description=data.description,
        rating=data.rating,
        maps_url=data.maps_url,
    )
    return LocationCreateResponse.model_validate(location)


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: str, location_service: LocationService = Depends(get_location_service)
) -> LocationResponse:
    """Получение информации о локации"""
    location = await location_service.get_location(location_id)
    return LocationResponse.model_validate(location)


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: str, data: LocationUpdate, location_service: LocationService = Depends(get_location_service)
) -> LocationResponse:
    """Обновление данных локации (без фотографий)"""
    location = await location_service.update_location(
        location_id,
        name=data.name,
        categories=data.categories,
        tags=data.tags,
        instagram_url=data.instagram_url,
        working_hours=data.working_hours,
        address=data.address,
        description=data.description,
        rating=data.rating,
    )
    return LocationResponse.model_validate(location)


@router.delete("/{location_id}", status_code=204)
async def delete_location(location_id: str, location_service: LocationService = Depends(get_location_service)) -> None:
    """Удаление локации и всех её фотографий"""
    await location_service.delete_location(location_id)


# Эндпоинты для работы с фотографиями
@router.post("/{location_id}/photos", response_model=LocationResponse)
async def upload_location_photos(
    location_id: str,
    photos: list[UploadFile] = File(...),
    location_service: LocationService = Depends(get_location_service),
) -> LocationResponse:
    """Загрузка фотографий для локации"""
    try:
        logger.info(f"Загрузка фото для локации {location_id}")
        logger.info(f"Количество фото: {len(photos)}")

        location = await location_service.add_location_photos(
            location_id=location_id,
            files=photos,
        )
        result = LocationResponse.model_validate(location).model_dump()
        logger.info(f"Фото успешно загружены. Результат: {result}")
        return result

    except HTTPException as e:
        # Пробрасываем HTTP ошибки как есть
        logger.error(f"Ошибка при загрузке фото: {e!s}")
        raise
    except Exception as e:
        # Все остальные ошибки логируем и возвращаем 500
        logger.error(f"Неожиданная ошибка при загрузке фото: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неожиданная ошибка при загрузке фото"
        )


@router.delete("/{location_id}/photos/{photo_id}", response_model=LocationResponse)
async def delete_location_photo(
    location_id: str, photo_id: str, location_service: LocationService = Depends(get_location_service)
) -> LocationResponse:
    """Удаление конкретной фотографии локации"""
    location = await location_service.delete_location_photo(
        location_id=location_id,
        photo_id=photo_id,
    )
    return LocationResponse.model_validate(location)


@router.patch("/{location_id}/photos/{photo_id}/caption", response_model=LocationResponse)
async def update_photo_caption(
    location_id: str,
    photo_id: str,
    caption: str = Body(..., embed=True),
    location_service: LocationService = Depends(get_location_service),
) -> LocationResponse:
    """Обновление подписи к фотографии"""
    try:
        location = await location_service.update_photo_caption(
            location_id=location_id,
            photo_id=photo_id,
            caption=caption,
        )
        return LocationResponse.model_validate(location)
    except HTTPException as e:
        logger.error(f"Ошибка при обновлении подписи: {e!s}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обновлении подписи: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неожиданная ошибка при обновлении подписи"
        )


@router.patch("/{location_id}/photos/reorder", response_model=LocationResponse)
async def reorder_photos(
    location_id: str,
    data: PhotoReorderRequest,
    location_service: LocationService = Depends(get_location_service),
) -> LocationResponse:
    """Изменение порядка фотографий"""
    location = await location_service.reorder_photos(
        location_id=location_id,
        photo_order=data.photo_order,
    )
    return LocationResponse.model_validate(location)
