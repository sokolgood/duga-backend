from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.core.types import SwipeAction


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class LocationCandidate(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    address: str | None = None
    rating: float | None = None
    working_hours: str | None = None
    image_url: str | None = None
    distance_km: float | None = None

    # Приватные поля для вычисления координат
    latitude: float = Field(exclude=True)
    longitude: float = Field(exclude=True)

    @computed_field
    def coordinates(self) -> Coordinates:
        return Coordinates(lat=self.latitude, lng=self.longitude)

    model_config = ConfigDict(from_attributes=True)


class SwipeActionRequest(BaseModel):
    location_id: UUID
    action: SwipeAction

    model_config = {
        "json_schema_extra": {"example": {"location_id": "123e4567-e89b-12d3-a456-426614174000", "action": "like"}}
    }


class SwipeHistoryItem(BaseModel):
    id: UUID
    user_id: UUID
    location_id: UUID
    action: SwipeAction
    created_at: datetime
    location: LocationCandidate | None = None

    model_config = ConfigDict(from_attributes=True)
