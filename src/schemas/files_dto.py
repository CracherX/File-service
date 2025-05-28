from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FileDTO(BaseModel):
    id: int
    name: str
    extension: Optional[str]
    size: int
    path: str
    created_at: datetime
    updated_at: Optional[datetime]
    comment: Optional[str]

    class Config:
        from_attributes = True
