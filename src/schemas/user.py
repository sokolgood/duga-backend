from uuid import UUID

from pydantic import BaseModel, EmailStr

from src.schemas.auth import PhoneNumber


class UserBase(BaseModel):
    phone_number: PhoneNumber
    email: EmailStr | None = None
    city: str | None = None
    full_name: str | None = None
    preferences: dict | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    city: str | None = None
    full_name: str | None = None
    preferences: dict | None = None


class UserInDB(UserBase):
    id: UUID
    is_phone_verified: bool

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    pass
