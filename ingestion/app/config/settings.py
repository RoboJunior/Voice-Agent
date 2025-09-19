from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


# Import all settings
class Settings(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str
    COLLECTION_NAME: str
    TEXT_EMBEDDING_MODEL_NAME: str

    model_config = SettingsConfigDict(env_file=".env")


# Store all the settings to the cache
@lru_cache
def get_settings():
    return Settings()
