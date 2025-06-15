from typing import Optional
from pydantic import BaseModel

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    invite_code: str
    is_active: bool

    class Config:
        from_attributes = True 