from typing import Optional
from pydantic import BaseModel, Field


class GetFilesList(BaseModel):
    page: Optional[int] = Field(1, ge=1, description="Номер страницы")
    page_size: Optional[int] = Field(20, ge=1, description="Размер страницы")


class GetFile(BaseModel):
    id: int = Field(..., ge=1, description="ID файла")


class UploadFile(BaseModel):
    name: str
    extension: Optional[str]
    size: int
    path: str
    comment: Optional[str]


class DeleteFile(BaseModel):
    id: int
