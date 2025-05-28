import os
from pathlib import Path
from typing import List
from src.repositories.file_repositry import FileRepository
from src.schemas.request_dto import UploadFile
from src.schemas.files_dto import FileDTO
from src.core.config import Config


class FilesService:
    def __init__(self, repository: FileRepository, config: Config):
        self._repository = repository
        self._config = config

    def list_all_files(self, page: int = 0, page_size: int = 100) -> List[FileDTO]:
        files = self._repository.get_all_files(page, page_size)
        return [FileDTO.from_orm(file) for file in files]

    def get_file(self, file_id: int = 1) -> FileDTO:
        return FileDTO.from_orm(self._repository.get_file(file_id))

    def upload_file(self, dto: UploadFile, content: bytes) -> FileDTO:
        path = f"{Path(__file__).resolve().parent.parent}{self._config.UPLOAD_DIR}{dto.path}/{dto.name}{dto.extension}"

        with open(path, "wb") as f:
            f.write(content)

        return FileDTO.from_orm(self._repository.add_file(dto))

    def delete_file(self, file_id: int):
        file = self._repository.get_file(file_id)
        if not file:
            return False

        full_path = os.path.join(f'{Path(__file__).resolve().parent.parent}{self._config.UPLOAD_DIR}', file.path,
                                 file.name + file.extension)
        if os.path.exists(full_path):
            os.remove(full_path)

        self._repository.delete_file(file_id)
        return True
