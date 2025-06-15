from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.core.enums import DeploymentStatus, DeploymentPriority

class Deployment(Base):
    __tablename__ = "deployments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False)
    docker_image = Column(String, nullable=False)
    
    # Resource requirements
    required_ram_gb = Column(Float, nullable=False)
    required_cpu_cores = Column(Integer, nullable=False)
    required_gpu_count = Column(Integer, nullable=False)
    
    # Scheduling and status
    priority = Column(SQLEnum(DeploymentPriority), default=DeploymentPriority.MEDIUM)
    status = Column(SQLEnum(DeploymentStatus), default=DeploymentStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default='now()')
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    meta_data = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="deployments")
    cluster = relationship("Cluster", back_populates="deployments") 