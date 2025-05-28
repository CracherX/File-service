import os
from typing import List, Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from starlette.responses import FileResponse

from src.core import responses
from src.core.container import Container
from src.schemas import request_dto
from src.schemas.files_dto import FileDTO
from src.schemas.request_dto import UpdateFile
from src.services.files_service import FilesService

router = APIRouter()


@router.get(
    "/files",
    response_model=List[FileDTO],
    summary="Получить список файлов",
    description="Возвращает список файлов с поддержкой пагинации и фильтрации по пути.",
)
@inject
def get_files(
        dto: request_dto.GetFilesList = Depends(),
        file_service: FilesService = Depends(Provide[Container.file_service])
):
    return file_service.list_files(dto.page, dto.page_size, dto.path)


@router.get(
    "/file",
    response_model=FileDTO,
    summary="Получить файл по ID",
    description="Возвращает информацию о файле по его идентификатору.",
)
@inject
def get_file(
        dto: request_dto.GetFile = Depends(),
        file_service: FilesService = Depends(Provide[Container.file_service])
):
    return file_service.get_file(dto.id)


@router.delete(
    "/file",
    status_code=status.HTTP_200_OK,
    summary="Удалить файл",
    description="Удаляет файл по ID. Если файл не найден — возвращает ошибку 404.",
    responses={
        404: {"description": "Файл не найден"}
    }
)
@inject
async def delete_file(
        dto: request_dto.DeleteFile = Depends(),
        file_service: FilesService = Depends(Provide[Container.file_service])
):
    deleted = await file_service.delete_file(dto.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Файл не найден")

    return responses.DeleteResponse(dto.id)


@router.patch(
    "/file",
    response_model=FileDTO,
    summary="Обновить данные о файле",
    description="Изменяет название, путь или комментарий к файлу. Также обновляется дата изменения.",
)
@inject
async def update_file(
        dto: UpdateFile,
        file_service: FilesService = Depends(Provide[Container.file_service])
):
    updated = await file_service.update_file(dto)
    if not updated:
        raise HTTPException(status_code=404, detail="Файл не найден")

    return updated


@router.post(
    "/file",
    response_model=FileDTO,
    summary="Загрузить файл",
    description="Загружает файл с дополнительными метаданными, такими как путь и комментарий.",
)
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
    return await file_service.upload_file(file_dto, content)


@router.get(
    "/file/{file_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Скачать файл",
    description="Скачивает файл из хранилища по ID. Возвращает бинарные данные.",
)
@inject
def download_file(
        file_id: int,
        file_service: FilesService = Depends(Provide[Container.file_service])
):
    response = file_service.download_file(file_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(
        path=response.path,
        filename=response.filename,
        media_type="application/octet-stream"
    )
