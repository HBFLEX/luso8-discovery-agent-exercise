"""
App configs loaded from env variables
Author: Happy Banda
"""

from functools import lru_cache
from pydantic import Field
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Annotated[str, Field(..., alias="DATABASE_URL")]
    anthropic_api_key: str = Annotated[str, Field(..., alias="ANTHROPIC_API_KEY")]
    llm_model: str = Field(default="claude-3-5-sonnet-20241022", alias="LLM_MODEL")
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

