from fastapi import UploadFile
from pydantic import BaseModel, Field, HttpUrl


class PhotoCreate(BaseModel):
    caption: str | None = None


class PhotoUpload(PhotoCreate):
    file: UploadFile


class PhotoResponse(BaseModel):
    id: str
    photo_url: HttpUrl
    caption: str | None = None


class LocationBase(BaseModel):
    name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    categories: list[str]
    tags: list[str] | None = None
    instagram_url: HttpUrl | None = None
    working_hours: str | None = None
    address: str | None = None
    description: str | None = None
    rating: float | None = Field(None, ge=0, le=5)


class LocationCreate(LocationBase):
    photos: list[PhotoUpload] | None = None


class LocationUpdate(BaseModel):
    name: str | None = None
    categories: list[str] | None = None
    tags: list[str] | None = None
    instagram_url: HttpUrl | None = None
    working_hours: str | None = None
    address: str | None = None
    description: str | None = None
    rating: float | None = Field(None, ge=0, le=5)


class LocationResponse(LocationBase):
    id: str
    rating: float = 0.0
    photos: list[PhotoResponse] = []

    class Config:
        from_attributes = True
