from typing import Optional
from pydantic import BaseModel, Field


class GetFilesList(BaseModel):
    page: Optional[int] = Field(1, ge=1, description="Номер страницы")
    page_size: Optional[int] = Field(20, ge=1, description="Размер страницы")
    path: Optional[str] = Field(None, description="Поиск всех файлов по указанному пути")


class GetFile(BaseModel):
    id: int = Field(None, ge=1, description="ID файла")


class UploadFile(BaseModel):
    name: str
    extension: Optional[str]
    size: int
    path: str
    comment: Optional[str]


class DeleteFile(BaseModel):
    id: int = Field(description="ID файла")


class UpdateFile(BaseModel):
    id: int
    name: Optional[str] = Field(None, max_length=255)
    path: Optional[str] = Field(None, max_length=1024)
    comment: Optional[str] = None
