from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    DUMMY_IMAGE_URL: str
    REPLICATE_PREDICTIONS_MOCK_URL: str
    REPLICATE_MODEL_VERSION: str
    REPLICATE_CALLBACK_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()
