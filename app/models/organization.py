from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    invite_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default='now()')
    is_active = Column(Boolean, default=True)
    
    users = relationship("User", back_populates="organization")
    clusters = relationship("Cluster", back_populates="organization") 