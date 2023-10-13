from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]

    APP_HOST: str
    APP_PORT: int

    REDIS_HOST: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        db = f"postgresql+asyncpg://"\
             f"{self.DB_USER}:{self.DB_PASS}"\
             f"@{self.DB_HOST}:{self.DB_PORT}"\
             f"/{self.DB_NAME}"
        return db

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    @property
    def TEST_DATABASE_URL(self):
        db = f"postgresql+asyncpg://"\
             f"{self.TEST_DB_USER}:{self.TEST_DB_PASS}"\
             f"@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}"\
             f"/{self.TEST_DB_NAME}"
        return db

    SECRET_KEY: str
    ALGORYTM:   str

    CELERY_BROKER: str

    SITE_NAME:  str
    TG_BOT:     str
    TG_CHANNEL: str

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()
