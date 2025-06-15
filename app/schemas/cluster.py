from typing import Optional
from pydantic import BaseModel, UUID4

class ClusterBase(BaseModel):
    name: str
    total_ram_gb: float
    total_cpu_cores: int
    total_gpu_count: int

class ClusterCreate(ClusterBase):
    pass

class Cluster(ClusterBase):
    id: UUID4
    organization_id: UUID4
    owner_id: UUID4
    available_ram_gb: float
    available_cpu_cores: int
    available_gpu_count: int
    is_active: bool

    class Config:
        from_attributes = True 