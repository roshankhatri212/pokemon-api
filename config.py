# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_version: str = "v1"

    class Config:
        env_file = ".env"

settings = Settings()
