from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base
from sqlalchemy import ForeignKey



class WatchDB(Base):
    __tablename__ = "watches"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), index=True)
    model_name = Column(String(100))


    is_automatic = Column(Boolean)
    movement_type = Column(String(50))
    case_size_mm = Column(Float)
    crystal_type = Column(String(50))
    water_resistance_m = Column(Integer)
    strap_type = Column(String(50))
    power_reserve_hours = Column(Integer, nullable=True)


    ai_confidence = Column(Float)
    needs_verification = Column(Boolean, default=False)


    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserDB", back_populates="watches")
    price = Column(Float, nullable=True, default=0.0)


class FavoriteDB(Base):
    __tablename__ = "favorites"


    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    watch_id = Column(Integer, ForeignKey("watches.id", ondelete="CASCADE"), primary_key=True)


class ReviewDB(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)


    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    watch_id = Column(Integer, ForeignKey("watches.id", ondelete="CASCADE"))