from pathlib import Path
from typing import List, Optional
from uuid import uuid4
from shutil import move
import aiofiles.os
from src.repositories.file_repositry import FileRepository
from src.schemas.request_dto import UploadFile, UpdateFile
from src.schemas.files_dto import FileDTO, DownloadFileDTO
from src.core.config import Config


class FilesService:
    def __init__(self, repository: FileRepository, config: Config):
        self._repository = repository
        self._config = config

    def list_files(
            self, page: int = 0,
            page_size: int = 100,
            path_contains: Optional[str] = None
    ) -> List[FileDTO]:
        offset = (page - 1) * page_size
        files = self._repository.get_files(offset, page_size, path_contains)
        return [FileDTO.from_orm(file) for file in files]

    def get_file(self, file_id: int = 1) -> FileDTO:
        return FileDTO.from_orm(self._repository.get_file(file_id))

    async def upload_file(self, dto: UploadFile, content: bytes) -> FileDTO:
        path = Path(__file__).resolve().parent.parent / self._config.UPLOAD_DIR / dto.path
        path.mkdir(parents=True, exist_ok=True)

        file_path = path / f"{dto.name}.{dto.extension}"

        if file_path.exists():
            unique_suffix = uuid4().hex[:8]
            new_name = f"{dto.name}_{unique_suffix}"
            file_path = path / f"{new_name}.{dto.extension}"
            dto.name = new_name

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return FileDTO.from_orm(self._repository.add_file(dto))

    async def delete_file(self, file_id: int) -> bool:
        file = self._repository.get_file(file_id)
        if not file:
            return False

        full_path = Path(
            __file__).resolve().parent.parent / self._config.UPLOAD_DIR / file.path / f"{file.name}.{file.extension}"

        if full_path.exists():
            await aiofiles.os.remove(full_path)

        self._repository.delete_file(file_id)
        return True

    def download_file(self, file_id: int) -> DownloadFileDTO | None:
        file = self._repository.get_file(file_id)
        if not file:
            return None

        base_dir = Path(__file__).resolve().parent.parent
        full_path = base_dir / self._config.UPLOAD_DIR / file.path / f"{file.name}.{file.extension}"

        if not full_path.exists():
            return None

        return DownloadFileDTO(
            path=str(full_path),
            filename=f"{file.name}.{file.extension}",
        )

    async def update_file(self, dto: UpdateFile) -> Optional[FileDTO]:
        file = self._repository.get_file(dto.id)
        if not file:
            return None

        old_path = Path(__file__).resolve().parent.parent / self._config.UPLOAD_DIR / file.path / f"{file.name}.{file.extension}"

        new_name = dto.name or file.name
        new_path = dto.path or file.path
        new_full_path = Path(__file__).resolve().parent.parent / self._config.UPLOAD_DIR / new_path
        new_full_path.mkdir(parents=True, exist_ok=True)

        new_file_path = new_full_path / f"{new_name}.{file.extension}"

        if dto.name or dto.path:
            if old_path.exists():
                move(str(old_path), str(new_file_path))

        updated_file = self._repository.update_file(
            file_id=dto.id,
            name=new_name,
            path=new_path,
            comment=dto.comment
        )

        return FileDTO.from_orm(updated_file)

