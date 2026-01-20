from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATA_DIR: Path
    model_name: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
