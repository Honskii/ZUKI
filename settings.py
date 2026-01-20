from pydantic_settings import BaseSettings
from pydantic import ConfigDict, ConfigDict

class Settings(BaseSettings):
    bot_token: str

    model_config = ConfigDict(env_file=".env")

settings = Settings()