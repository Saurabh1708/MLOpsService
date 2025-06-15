from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, UUID4
from app.core.enums import DeploymentStatus, DeploymentPriority

class DeploymentBase(BaseModel):
    name: str
    cluster_id: UUID4
    docker_image: str
    required_ram_gb: float
    required_cpu_cores: int
    required_gpu_count: int
    priority: DeploymentPriority = DeploymentPriority.MEDIUM
    meta_data: Optional[Dict[str, Any]] = None

class DeploymentCreate(DeploymentBase):
    pass

class Deployment(DeploymentBase):
    id: UUID4
    user_id: UUID4
    status: DeploymentStatus
    created_at: datetime
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True 