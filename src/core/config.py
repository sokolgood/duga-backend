import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("ENV", "local")
env_path: str = f"env/.env.{ENV}"
load_dotenv(env_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DUGA_")

    api_version: str = "/api/v1"
    env: str = ENV

    DB_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_PORT: str = os.getenv("DB_PORT")
    database_uri: str = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@/{DB_NAME}"
        + "?host="
        + ",".join(DB_HOST.split(","))
        + "&port="
        + ",".join(DB_PORT.split(","))
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
