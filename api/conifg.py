from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_NAME: str
    PG_USER: str
    PG_PASS: str
    PG_HOST: str
    PG_PORT: str

    ALLOWED_ORIGINS: List[str]
    ALLOW_CREDENTIALS: bool
    ALLOW_METHODS: List[str]
    ALLOW_HEADERS: List[str]

    OFFICES_URL: str
    PREREG_URL: str
    APP_PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


conf_settings = Settings()
