from urllib.parse import parse_qs, urlparse
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, model_validator


class PhotoCaption(BaseModel):
    caption: str | None = None


class PhotoResponse(BaseModel):
    id: UUID
    url: str = Field(alias="photo_url")
    caption: str | None = None
    order: int = Field(ge=0, description="Порядковый номер фотографии")

    class Config:
        from_attributes = True
        populate_by_name = True


class LocationBase(BaseModel):
    name: str
    categories: list[str]
    tags: list[str] | None = None
    instagram_url: HttpUrl | None = None
    working_hours: str | None = None
    address: str | None = None
    description: str | None = None
    rating: float | None = Field(None, ge=0, le=5)
    maps_url: HttpUrl | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)

    @model_validator(mode="after")
    @classmethod
    def extract_coordinates(cls: type["LocationBase"], model: "LocationBase") -> "LocationBase":
        if model.maps_url:
            try:
                parsed_url = urlparse(str(model.maps_url))
                if "yandex.ru" in parsed_url.netloc:
                    params = parse_qs(parsed_url.query)
                    if "ll" in params:
                        lon, lat = map(float, params["ll"][0].split(","))
                        model.longitude = lon
                        model.latitude = lat
            except Exception:
                pass  # Игнорируем ошибки парсинга

        return model


class LocationCreate(LocationBase):
    pass


class LocationCreateResponse(LocationBase):
    id: UUID

    class Config:
        from_attributes = True


class LocationUpdate(BaseModel):
    name: str | None = None
    categories: list[str] | None = None
    tags: list[str] | None = None
    instagram_url: HttpUrl | None = None
    working_hours: str | None = None
    address: str | None = None
    description: str | None = None
    rating: float | None = Field(None, ge=0, le=5)
    maps_url: HttpUrl | None = None


class LocationResponse(LocationBase):
    """Полная схема локации с фотографиями"""

    id: UUID
    photos: list[PhotoResponse] = []

    class Config:
        from_attributes = True


class PhotoReorderRequest(BaseModel):
    photo_order: list[str] = Field(..., description="Список photo_id в нужном порядке")
