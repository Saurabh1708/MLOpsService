from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.models.cluster import Cluster
from app.schemas.cluster import ClusterCreate, Cluster as ClusterSchema

router = APIRouter()

@router.post("/", response_model=ClusterSchema)
async def create_cluster(
    cluster_data: ClusterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must be in an organization")
    
    cluster = Cluster(
        name=cluster_data.name,
        organization_id=current_user.organization_id,
        owner_id=current_user.id,
        total_ram_gb=cluster_data.total_ram_gb,
        total_cpu_cores=cluster_data.total_cpu_cores,
        total_gpu_count=cluster_data.total_gpu_count,
        available_ram_gb=cluster_data.total_ram_gb,
        available_cpu_cores=cluster_data.total_cpu_cores,
        available_gpu_count=cluster_data.total_gpu_count
    )
    
    db.add(cluster)
    db.commit()
    db.refresh(cluster)
    
    return cluster

@router.get("/", response_model=List[ClusterSchema])
async def list_clusters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.organization_id:
        return []
    
    clusters = db.query(Cluster).filter(
        Cluster.organization_id == current_user.organization_id,
        Cluster.is_active == True
    ).all()
    
    return clusters 