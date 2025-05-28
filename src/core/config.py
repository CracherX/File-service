from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum


class LogLevel(str, Enum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"


class Config(BaseSettings):
    # App
    APP_NAME: str = Field("App", env="APP_NAME")
    LOG_LEVEL: LogLevel = Field(..., env="LOG_LEVEL")
    UPLOAD_DIR: str = Field("/uploads", env="UPLOAD_DIR")

    # Database
    DB: str = Field("", env="DB")
    DB_USER: str = Field("", env="DB_USER")
    DB_PASSWORD: str = Field("", env="DB_PASSWORD")
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: str = Field("3306", env="DB_PORT")
    DB_ENGINE: str = Field("postgresql", env="DB_ENGINE")

    @property
    def DATABASE_URI(self) -> str:
        return (
            f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB}"
        )

    @field_validator("DB_PORT")
    def validate_digital(cls, v: str):
        if not v.isdigit():
            raise ValueError("DB_PORT должен содержать только цифры!")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def setup_config():
    return Config()
