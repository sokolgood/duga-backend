from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_location_service, get_session
from src.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from src.services.location import LocationService

router = APIRouter(prefix="/location", tags=["location"])


@router.post("", response_model=LocationResponse)
async def create_location(
    data: LocationCreate, location_service: LocationService = Depends(get_location_service)
) -> LocationResponse:
    files = [(photo.file, photo.caption) for photo in (data.photos or [])]

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
        files=files,
    )
    return LocationResponse.model_validate(location)


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: str, location_service: LocationService = Depends(get_location_service)
) -> LocationResponse:
    location = await location_service.get_location(location_id)
    return LocationResponse.model_validate(location)


@router.get("", response_model=list[LocationResponse])
async def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: str | None = None,
    location_service: LocationService = Depends(get_location_service),
) -> list[LocationResponse]:
    locations = await location_service.get_locations(skip=skip, limit=limit, category=category)
    return [LocationResponse.model_validate(loc) for loc in locations]


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: str, data: LocationUpdate, location_service: LocationService = Depends(get_location_service)
) -> LocationResponse:
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
        photos=data.photos,
    )
    return LocationResponse.model_validate(location)


@router.delete("/{location_id}", status_code=204)
async def delete_location(location_id: str, session: AsyncSession = Depends(get_session)) -> None:
    service = LocationService(session)
    await service.delete_location(location_id)
