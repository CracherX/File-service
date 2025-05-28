import os
from typing import List, Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status

from src.core import responses
from src.core.container import Container
from src.schemas import request_dto
from src.schemas.files_dto import FileDTO
from src.services.files_service import FilesService

router = APIRouter()


@router.get("/files", response_model=List[FileDTO])
@inject
def get_files(
        dto: request_dto.GetFilesList = Depends(),
        file_service: FilesService = Depends(Provide[Container.file_service])
):
    return file_service.list_all_files(dto.page, dto.page_size)


@router.get("/file", response_model=FileDTO)
@inject
def get_file(
        dto: request_dto.GetFile = Depends(),
        file_service: FilesService = Depends(Provide[Container.file_service])
):
    return file_service.get_file(dto.id)


@router.delete("/file", status_code=status.HTTP_200_OK)
@inject
def delete_file(
        dto: request_dto.DeleteFile = Depends(),
        file_service: FilesService = Depends(Provide[Container.file_service])
):
    deleted = file_service.delete_file(dto.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Файл не найден")

    return responses.DeleteResponse(dto.id)


@router.post("/upload", response_model=FileDTO)
@inject
async def upload_file(
        upload: UploadFile = File(...),
        comment: Optional[str] = Form(None),
        path: str = Form(...),
        file_service: FilesService = Depends(Provide[Container.file_service]),
):
    content = await upload.read()

    filename = upload.filename
    name = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1].lstrip(".")
    size = len(content)

    file_dto = request_dto.UploadFile(
        name=name,
        extension=extension,
        size=size,
        path=path,
        comment=comment,
    )
    return file_service.upload_file(file_dto, content)
