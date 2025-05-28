from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index, UniqueConstraint
from src.core.database import Base


class Files(Base):
    id = Column(Integer, primary_key=True, index=True)

    # Имя файла
    name = Column(String(255), nullable=False)

    # Расширение файла
    extension = Column(String(10), nullable=True)

    # Размер файла в байтах
    size = Column(Integer, nullable=False)

    # Путь до файла
    path = Column(String(1024), nullable=False)

    # Дата создания
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Дата изменения
    updated_at = Column(DateTime, nullable=True)

    # Комментарий
    comment = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('name', name='uq_files_name'),
        Index('ix_files_path', 'path'),
    )

    def __repr__(self):
        return f"<File(name={self.name!r}, extension={self.extension!r}, size={self.size}, path={self.path!r})>"
