from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PG_NAME: str
    PG_USER: str
    PG_PASS: str
    PG_HOST: str
    PG_PORT: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

conf_settings = Settings()