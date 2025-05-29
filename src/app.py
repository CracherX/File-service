from fastapi import FastAPI
from src.core.container import Container
from src.api.v1.endpoints import files_endpoint  # импортируем router с endpoint


class App:
    def __init__(self) -> None:
        self.container = Container()
        self.config = self.container.config()
        self.logger = self.container.logger()
        self.db = self.container.db()
        self.app = FastAPI(title=self.config.APP_NAME)
        self._include_routers()

        self.db.create_database()

    def _include_routers(self) -> None:
        self.app.include_router(files_endpoint.router, prefix="/api/v1", tags=["Файлы"])

    def get_app(self) -> FastAPI:
        return self.app


app_instance = App()
app = app_instance.get_app()
app_instance.logger.info(f"Приложение {app_instance.config.APP_NAME} запущено")
