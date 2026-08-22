from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DATABASE_URL: str = (
        "postgresql+psycopg://globetrotter:globetrotter@localhost:5432/globetrotter"
    )
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENVIRONMENT: str = "development"

    UPLOAD_DIR: str = "uploads/photos"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_CONTENT_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]
    PUBLIC_BASE_URL: str = "http://localhost:8000"


settings = Settings()
