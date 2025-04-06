from sqlalchemy import JSON, UUID, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel


class Route(BaseModel):
    __tablename__ = "routes"

    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    meta = Column(JSON, nullable=True)  # Настроение, ожидания, описание маршрута

    user = relationship("User", back_populates="routes")
    locations = relationship("RouteLocation", back_populates="route", cascade="all, delete-orphan")


class RouteLocation(BaseModel):
    __tablename__ = "route_locations"

    route_id = Column(UUID, ForeignKey("routes.id"), nullable=False)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False)
    order = Column(Integer, nullable=False)  # Порядок следования точки в маршруте

    route = relationship("Route", back_populates="locations")
    location = relationship("Location", back_populates="route_associations")
