from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.core.enums import DeploymentStatus, DeploymentPriority

class DeploymentBase(BaseModel):
    name: str
    docker_image: str
    required_ram_gb: float
    required_cpu_cores: int
    required_gpu_count: int
    priority: DeploymentPriority = DeploymentPriority.MEDIUM
    meta_data: Optional[Dict[str, Any]] = None

class DeploymentCreate(DeploymentBase):
    cluster_id: int

class Deployment(DeploymentBase):
    id: int
    user_id: int
    cluster_id: int
    status: DeploymentStatus
    created_at: datetime
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True 