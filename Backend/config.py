import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Fenny Financial Assistant"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # File upload settings
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
    ]
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".xls", ".xlsx", ".txt"]
    MAX_FILES_PER_CONVERSATION: int = 3

    # Session settings
    SESSION_EXPIRY_HOURS: int = 24

    class Config:
        env_file = ".env"


settings = Settings()
