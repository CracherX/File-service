from datetime import datetime
from sqlalchemy.orm import Session
from src.models.files import Files
from typing import List, Optional
from src.schemas.request_dto import UploadFile


class FileRepository:
    def __init__(self, session: Session):
        self._db = session

    def get_files(
            self,
            offset: int = 0,
            limit: int = 100,
            path_contains: Optional[str] = None
    ) -> List[Files]:
        query = self._db.query(Files)

        if path_contains:
            query = query.filter(Files.path.contains(path_contains))

        return query.offset(offset).limit(limit).all()

    def get_file(self, file_id: int) -> Files:
        return self._db.query(Files).get(file_id)

    def add_file(self, dto: UploadFile) -> Files:
        file = Files(
            name=dto.name,
            extension=dto.extension,
            size=dto.size,
            path=dto.path,
            comment=dto.comment,
        )
        self._db.add(file)
        self._db.commit()
        self._db.refresh(file)
        return file

    def delete_file(self, file_id: int) -> None:
        file = self._db.query(Files).filter(Files.id == file_id).first()
        if file:
            self._db.delete(file)
            self._db.commit()

    def update_file(self, file_id: int, **kwargs) -> Optional[Files]:
        file = self._db.query(Files).filter(Files.id == file_id).first()
        if not file:
            return None

        for key, value in kwargs.items():
            setattr(file, key, value)

        file.updated_at = datetime.utcnow()
        self._db.commit()
        self._db.refresh(file)
        return file
