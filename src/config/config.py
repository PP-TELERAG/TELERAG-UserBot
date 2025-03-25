from pydantic import model_validator
from pydantic_settings import BaseSettings

from functools import lru_cache


class Settings(BaseSettings):
    # PYROGRAM SETTINGS
    PYRO_API_ID: int
    PYRO_API_HASH: str

    # POSTGRESQL SETTINGS
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_URL: str = None

    # LOGGER
    LOGGER: str
    LOGGER_LEVEL: str

    @model_validator(mode="before")
    @classmethod
    def get_database_url(cls, v):
        v["DB_URL"] = "postgresql://" + \
            f"{v["DB_USER"]}:{v["DB_PASS"]}@" + \
            f"{v["DB_HOST"]}:{v["DB_PORT"]}/{v["DB_NAME"]}"
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
