from enum import Enum as PyEnum

from sqlalchemy import (
    JSON,
    UUID,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class InteractionType(PyEnum):
    LIKE = "like"
    HIDE = "hide"
    FAVORITE = "favorite"


class Location(BaseModel):
    __tablename__ = "locations"

    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    categories = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)

    instagram_url = Column(String(255), nullable=True)
    working_hours = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    maps_url = Column(String(255), nullable=True)

    description = Column(String(2048), nullable=True)  # История, детали и т. д.
    rating = Column(Float, default=0.0)

    swipes = relationship("Swipe", back_populates="location", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="location", cascade="all, delete-orphan", order_by="Photo.order")
    route_associations = relationship("RouteLocation", back_populates="location", cascade="all, delete-orphan")
    user_interactions = relationship("UserLocationInteraction", back_populates="location", cascade="all, delete-orphan")


class Photo(BaseModel):
    __tablename__ = "photos"

    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False)
    photo_url = Column(String(512), nullable=False)
    caption = Column(String(255), nullable=True)
    order = Column(Integer, nullable=False, default=0)

    location = relationship("Location", back_populates="photos")


class UserLocationInteraction(BaseModel):
    __tablename__ = "user_location_interactions"

    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False)
    interaction_type = Column(Enum(InteractionType), nullable=False)

    user = relationship("User", back_populates="location_interactions")
    location = relationship("Location", back_populates="user_interactions")
