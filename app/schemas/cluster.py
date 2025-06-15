from typing import Optional
from pydantic import BaseModel

class ClusterBase(BaseModel):
    name: str
    total_ram_gb: float
    total_cpu_cores: int
    total_gpu_count: int

class ClusterCreate(ClusterBase):
    pass

class Cluster(ClusterBase):
    id: int
    organization_id: int
    owner_id: int
    available_ram_gb: float
    available_cpu_cores: int
    available_gpu_count: int
    is_active: bool

    class Config:
        from_attributes = True 