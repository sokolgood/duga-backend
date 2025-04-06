from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class Swipe(BaseModel):
    __tablename__ = "swipes"

    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False)
    liked = Column(Boolean, nullable=False)  # True — лайк, False — дизлайк

    user = relationship("User", back_populates="swipes")
    location = relationship("Location", back_populates="swipes")
