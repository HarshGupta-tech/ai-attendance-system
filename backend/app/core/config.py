from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./attendance.db"
    SECRET_KEY: str = "change-me-in-production"
    JWT_SECRET: str = "jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    FACE_RECOGNITION_THRESHOLD: float = 0.6
    UPLOAD_DIRECTORY: str = "uploads"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    LOW_ATTENDANCE_THRESHOLD: float = 75.0
    LATE_THRESHOLD_MINUTES: int = 15
    DEMO_MODE: bool = False
    APP_NAME: str = "AI Attendance System"
    APP_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
