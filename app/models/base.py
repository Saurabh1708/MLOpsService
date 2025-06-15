from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    id: Optional[int] = Field(None, description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 