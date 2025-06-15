from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Cluster(Base):
    __tablename__ = "clusters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Resource specifications
    total_ram_gb = Column(Float, nullable=False)
    total_cpu_cores = Column(Integer, nullable=False)
    total_gpu_count = Column(Integer, nullable=False)
    
    # Available resources (updated dynamically)
    available_ram_gb = Column(Float, nullable=False)
    available_cpu_cores = Column(Integer, nullable=False)
    available_gpu_count = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default='now()')
    is_active = Column(Boolean, default=True)
    
    organization = relationship("Organization", back_populates="clusters")
    owner = relationship("User", back_populates="clusters")
    deployments = relationship("Deployment", back_populates="cluster") 