from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    gemini_api_key: str
    database_url: str = "sqlite:///./inventory.db"

    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
