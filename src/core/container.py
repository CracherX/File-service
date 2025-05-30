from dependency_injector import containers, providers
from src.core.database import Database
from src.repositories.file_repositry import FileRepository
from src.services.files_service import FilesService
from src.core.config import setup_config
from src.core.logger import setup_logging


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.api.v1.endpoints.files_endpoint",
        ]
    )

    config = providers.Singleton(setup_config)

    logger = providers.Singleton(setup_logging, level=config.provided.LOG_LEVEL)

    db = providers.Singleton(Database, db_url=config.provided.DATABASE_URI)

    file_repository = providers.Factory(
        FileRepository,
        session=db.provided.get_session.call(),
    )

    file_service = providers.Factory(
        FilesService,
        repository=file_repository,
        config=config,
        logger=logger
    )
