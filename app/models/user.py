from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    is_public = Column(Boolean, default=False)
    share_token = Column(String, unique=True, index=True, nullable=True)


    watches = relationship("WatchDB", back_populates="owner", cascade="all, delete-orphan")