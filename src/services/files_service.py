from pathlib import Path
from typing import List, Optional
from uuid import uuid4
from shutil import move
from logging import Logger
import aiofiles.os

from src.models.files import Files
from src.repositories.file_repositry import FileRepository
from src.schemas.requests_dto import UploadFile, UpdateFile
from src.schemas.responses_dto import FileDTO, DownloadFileDTO, ActualizeResultDTO
from src.core.config import Config


class FilesService:
    def __init__(self, repository: FileRepository, config: Config, logger: Logger):
        self._repository = repository
        self._config = config
        self._logger = logger

    def list_files(
            self, page: int = 0,
            page_size: int = 100,
            path_contains: Optional[str] = None
    ) -> List[FileDTO]:
        offset = (page - 1) * page_size
        self._logger.info(f"Запрошен список файлов: страница {page}, размер страницы {page_size}, фильтр: {path_contains}")
        files = self._repository.get_files(offset, page_size, path_contains)
        return [FileDTO.from_orm(file) for file in files]

    def get_file(self, file_id: int = 1) -> FileDTO:
        self._logger.info(f"Получение файла по ID: {file_id}")
        return FileDTO.from_orm(self._repository.get_file(file_id))

    async def upload_file(self, dto: UploadFile, content: bytes) -> FileDTO:
        self._logger.info(f"Загрузка файла: {dto.name}.{dto.extension} в путь {dto.path}")
        path = Path(__file__).resolve().parent.parent / self._config.UPLOAD_DIR / dto.path
        path.mkdir(parents=True, exist_ok=True)

        file_path = path / f"{dto.name}.{dto.extension}"

        if file_path.exists():
            self._logger.warning(f"Файл уже существует: {file_path}, создаётся уникальное имя")
            unique_suffix = uuid4().hex[:8]
            new_name = f"{dto.name}_{unique_suffix}"
            file_path = path / f"{new_name}.{dto.extension}"
            dto.name = new_name

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        self._logger.info(f"Файл успешно сохранён: {file_path}")
        return FileDTO.from_orm(self._repository.add_file(dto))

    async def delete_file(self, file_id: int) -> bool:
        self._logger.info(f"Удаление файла с ID: {file_id}")
        file = self._repository.get_file(file_id)
        if not file:
            self._logger.warning(f"Файл с ID {file_id} не найден в базе данных")
            return False

        full_path = Path(
            __file__).resolve().parent.parent / self._config.UPLOAD_DIR / file.path / f"{file.name}.{file.extension}"

        if full_path.exists():
            await aiofiles.os.remove(full_path)
            self._logger.info(f"Файл удалён с диска: {full_path}")
        else:
            self._logger.warning(f"Файл не найден на диске: {full_path}")

        self._repository.delete_file(file_id)
        self._logger.info(f"Запись о файле удалена из базы данных: ID {file_id}")
        return True

    def download_file(self, file_id: int) -> DownloadFileDTO | None:
        self._logger.info(f"Запрос на скачивание файла с ID: {file_id}")
        file = self._repository.get_file(file_id)
        if not file:
            self._logger.warning(f"Файл с ID {file_id} не найден")
            return None

        base_dir = Path(__file__).resolve().parent.parent
        full_path = base_dir / self._config.UPLOAD_DIR / file.path / f"{file.name}.{file.extension}"

        if not full_path.exists():
            self._logger.error(f"Файл отсутствует на диске: {full_path}")
            return None

        self._logger.info(f"Файл готов к скачиванию: {full_path}")
        return DownloadFileDTO(
            path=str(full_path),
            filename=f"{file.name}.{file.extension}",
        )

    async def update_file(self, dto: UpdateFile) -> Optional[FileDTO]:
        self._logger.info(f"Обновление файла с ID: {dto.id}")
        file = self._repository.get_file(dto.id)
        if not file:
            self._logger.warning(f"Файл с ID {dto.id} не найден")
            return None

        old_path = Path(
            __file__).resolve().parent.parent / self._config.UPLOAD_DIR / file.path / f"{file.name}.{file.extension}"

        new_name = dto.name or file.name
        new_path = dto.path or file.path
        new_full_path = Path(__file__).resolve().parent.parent / self._config.UPLOAD_DIR / new_path
        new_full_path.mkdir(parents=True, exist_ok=True)

        new_file_path = new_full_path / f"{new_name}.{file.extension}"

        if dto.name or dto.path:
            if old_path.exists():
                move(str(old_path), str(new_file_path))
                self._logger.info(f"Файл перемещён из {old_path} в {new_file_path}")
            else:
                self._logger.warning(f"Старый файл не найден на диске: {old_path}")

        updated_file = self._repository.update_file(
            file_id=dto.id,
            name=new_name,
            path=new_path,
            comment=dto.comment
        )

        self._logger.info(f"Файл обновлён в базе данных: ID {dto.id}")
        return FileDTO.from_orm(updated_file)

    def sync_files(self) -> ActualizeResultDTO:
        self._logger.info("Начата синхронизация файловой системы и базы данных")
        base_path = Path(__file__).resolve().parent.parent / self._config.UPLOAD_DIR

        disk_files = {}
        for path in base_path.rglob("*"):
            if path.is_file():
                rel_path = path.relative_to(base_path)
                file_name = path.stem
                extension = path.suffix.lstrip(".")
                size = path.stat().st_size
                disk_files[str(rel_path)] = {
                    "name": file_name,
                    "extension": extension,
                    "size": size,
                    "path": str(rel_path.parent),
                }

        db_files = self._repository.get_all_files()
        db_files_map = {
            f"{file.path}/{file.name}.{file.extension}": file for file in db_files
        }

        removed = []
        for key in db_files_map:
            if key not in disk_files:
                self._logger.info(f"Файл отсутствует на диске, удаление из БД: {key}")
                self._repository.delete_file(db_files_map[key].id)
                removed.append(key)

        added = []
        new_files = []
        for key, info in disk_files.items():
            if key not in db_files_map:
                self._logger.info(f"Файл найден на диске, добавление в БД: {key}")
                new_files.append(Files(
                    name=info["name"],
                    extension=info["extension"],
                    size=info["size"],
                    path=info["path"],
                ))
                added.append(key)
        if new_files:
            self._repository.add_files_bulk(new_files)

        total = len(self._repository.get_all_files())
        self._logger.info(f"Синхронизация завершена. Добавлено: {len(added)}, удалено: {len(removed)}, всего в БД: {total}")
        return ActualizeResultDTO(
            added=added,
            removed=removed,
            total_in_db=total
        )