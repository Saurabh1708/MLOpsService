from typing import Optional
from pydantic import BaseModel, UUID4

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: UUID4
    invite_code: str
    is_active: bool

    class Config:
        from_attributes = True 