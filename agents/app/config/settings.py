from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


# Import all settings
class Settings(BaseSettings):
    DEEPGRAM_API_KEY: str
    APP_NAME: str
    MCP_SERVER_URL: str
    MODEL_NAME: str
    GOOGLE_API_KEY: str
    ELEVEN_LABS_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


# Store all the settings to the cache
@lru_cache
def get_settings():
    return Settings()
