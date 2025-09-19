from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


# Import all settings
class Settings(BaseSettings):
    SEARCH_URL: str

    model_config = SettingsConfigDict(env_file=".env")


# Store all the settings to the cache
@lru_cache
def get_settings():
    return Settings()
