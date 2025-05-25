from sqlalchemy import UUID, Column, ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from src.core.types import SwipeAction

from .base import BaseModel


class Swipe(BaseModel):
    __tablename__ = "swipes"

    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False)
    action = Column(SQLAlchemyEnum(SwipeAction), nullable=False)

    user = relationship("User", back_populates="swipes")
    location = relationship("Location", back_populates="swipes", lazy="selectin")
