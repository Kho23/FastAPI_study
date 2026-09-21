from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    database_url:str = f"sqlite:///{(BASE_DIR / 'data' / 'ledger.db').as_posix()}"
    debug:bool = False

settings = Settings()