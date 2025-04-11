from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PYRO_API_ID: int
    PYRO_API_HASH: str

    LOGGER_LOG_LEVEL: str = "INFO"
    LOGGER_ROTATION: str = "1 MB"
    LOGGER_RETENTION_DAYS: str = "10 Days"
    LOGGER_ENCODING: str = "utf-8"

    BROKER_URL: str
    BROKER_IN_TOPIC: str
    BROKER_OUT_TOPIC: str

    COLLECTOR_HISTORY_LIMIT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()