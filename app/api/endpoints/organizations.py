from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, Organization as OrganizationSchema
from app.utils.invite import generate_invite_code

router = APIRouter()

@router.post("/", response_model=OrganizationSchema)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    organization = Organization(
        name=org_data.name,
        invite_code=generate_invite_code()
    )
    
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    # Add current user to organization
    current_user.organization_id = organization.id
    db.commit()
    
    return organization

@router.get("/me", response_model=OrganizationSchema)
async def get_my_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.organization:
        raise HTTPException(status_code=404, detail="User not in any organization")
    
    return current_user.organization 