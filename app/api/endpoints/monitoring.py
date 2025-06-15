from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.models.cluster import Cluster
from app.models.deployment import Deployment
from app.core.enums import DeploymentStatus

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@router.get("/metrics")
async def get_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must be in an organization")
    
    # Get organization clusters
    clusters = db.query(Cluster).filter(
        Cluster.organization_id == current_user.organization_id
    ).all()
    
    # Get deployment statistics
    total_deployments = db.query(Deployment).join(Cluster).filter(
        Cluster.organization_id == current_user.organization_id
    ).count()
    
    running_deployments = db.query(Deployment).join(Cluster).filter(
        Cluster.organization_id == current_user.organization_id,
        Deployment.status == DeploymentStatus.RUNNING
    ).count()
    
    pending_deployments = db.query(Deployment).join(Cluster).filter(
        Cluster.organization_id == current_user.organization_id,
        Deployment.status == DeploymentStatus.PENDING
    ).count()
    
    return {
        "clusters": len(clusters),
        "total_deployments": total_deployments,
        "running_deployments": running_deployments,
        "pending_deployments": pending_deployments,
        "resource_utilization": {
            cluster.id: {
                "name": cluster.name,
                "ram_utilization": (cluster.total_ram_gb - cluster.available_ram_gb) / cluster.total_ram_gb * 100,
                "cpu_utilization": (cluster.total_cpu_cores - cluster.available_cpu_cores) / cluster.total_cpu_cores * 100,
                "gpu_utilization": (cluster.total_gpu_count - cluster.available_gpu_count) / cluster.total_gpu_count * 100 if cluster.total_gpu_count > 0 else 0
            }
            for cluster in clusters
        }
    } 