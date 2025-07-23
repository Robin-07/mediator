from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_BACKEND_URL: str = "redis://redis:6379/1"

    class Config:
        env_file = ".env"


settings = Settings()
