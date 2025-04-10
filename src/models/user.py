from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    city = Column(String(255), nullable=True)
    is_phone_verified = Column(Boolean, default=False)
    full_name = Column(String(255), nullable=True)
    preferences = Column(JSON, nullable=True)

    swipes = relationship("Swipe", back_populates="user", cascade="all, delete-orphan")
    routes = relationship("Route", back_populates="user", cascade="all, delete-orphan")


class PhoneVerification(BaseModel):
    __tablename__ = "phone_verifications"

    phone_number = Column(String(20), nullable=False)
    code = Column(String(10), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)

    user = relationship("User", backref="verifications")
