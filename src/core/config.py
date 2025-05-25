import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("ENV", "local")
env_path: str = f"env/.env.{ENV}"
load_dotenv(env_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DUGA_")

    project_name: str = "duga backend"
    api_version: str = "/api/v1"
    env: str = ENV

    DB_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_PORT: str = os.getenv("DB_PORT")
    database_uri: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # jwt
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_days: int = os.getenv("ACCESS_TOKEN_EXPIRE_DAYS")

    # s3
    s3_params: dict = {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "region_name": os.getenv("AWS_REGION"),
    }
    s3_bucket: str = os.getenv("AWS_BUCKET_NAME")

    # file storage
    file_storage_path: str = os.getenv("FILE_STORAGE_PATH")

    # redis
    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: str = os.getenv("REDIS_PORT")
    redis_pass: str = os.getenv("REDIS_PASS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
