from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
HOTELS_PATH = DATA_DIR / "hotels.json"
TOURS_PATH = DATA_DIR / "tours.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    webapp_url: str = "http://localhost:5173"
    api_public_url: str = "http://127.0.0.1:8000"
    cors_origins: str = "http://localhost:5173"
    validate_init_data: bool = True
    enable_web_search: bool = True
    web_search_max_results: int = 5

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
