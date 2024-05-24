from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


@lru_cache()
def get_settings():
    return Settings()


class Settings(BaseSettings):
    app_name: str = "TETYS Service"
    path_projects: str = "./resources/projects"
    model_config = SettingsConfigDict(env_file=".env")
