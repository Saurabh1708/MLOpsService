from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.enums import DeploymentStatus
from app.db.base import get_db
from app.models.user import User
from app.models.deployment import Deployment
from app.models.cluster import Cluster
from app.schemas.deployment import DeploymentCreate, Deployment as DeploymentSchema
from app.services.scheduler import scheduler

router = APIRouter()

@router.post("/", response_model=DeploymentSchema)
async def create_deployment(
    deployment_data: DeploymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify cluster exists and user has access
    cluster = db.query(Cluster).filter(
        Cluster.id == deployment_data.cluster_id,
        Cluster.organization_id == current_user.organization_id
    ).first()
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    deployment = Deployment(
        name=deployment_data.name,
        user_id=current_user.id,
        cluster_id=deployment_data.cluster_id,
        docker_image=deployment_data.docker_image,
        required_ram_gb=deployment_data.required_ram_gb,
        required_cpu_cores=deployment_data.required_cpu_cores,
        required_gpu_count=deployment_data.required_gpu_count,
        priority=deployment_data.priority,
        meta_data=deployment_data.meta_data
    )
    
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    
    # Add to scheduler queue
    scheduler.add_deployment(deployment)
    
    return deployment

@router.get("/", response_model=List[DeploymentSchema])
async def list_deployments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deployments = db.query(Deployment).filter(
        Deployment.user_id == current_user.id
    ).order_by(Deployment.created_at.desc()).all()
    
    return deployments

@router.get("/{deployment_id}", response_model=DeploymentSchema)
async def get_deployment(
    deployment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deployment = db.query(Deployment).filter(
        Deployment.id == deployment_id,
        Deployment.user_id == current_user.id
    ).first()
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return deployment

@router.delete("/{deployment_id}")
async def cancel_deployment(
    deployment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deployment = db.query(Deployment).filter(
        Deployment.id == deployment_id,
        Deployment.user_id == current_user.id
    ).first()
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    if deployment.status == DeploymentStatus.RUNNING:
        # Deallocate resources
        cluster = db.query(Cluster).filter(Cluster.id == deployment.cluster_id).first()
        scheduler._deallocate_resources(deployment, cluster, db)
    
    deployment.status = DeploymentStatus.FAILED
    deployment.completed_at = datetime.now()
    db.commit()
    
    return {"message": "Deployment cancelled successfully"} 