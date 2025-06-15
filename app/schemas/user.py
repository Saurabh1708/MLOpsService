from typing import Optional
from pydantic import BaseModel, UUID4

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    invite_code: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: UUID4
    organization_id: Optional[UUID4]
    is_active: bool

    class Config:
        from_attributes = True 