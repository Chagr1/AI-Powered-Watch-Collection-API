from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


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