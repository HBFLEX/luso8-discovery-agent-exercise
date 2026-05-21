"""
App configs loaded from env variables
Author: Happy Banda
"""

from functools import lru_cache
from pydantic import Field
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Annotated[str, Field(..., description="SQLAlchemy connection")]
    groq_api_key: str = Annotated[str, Field(..., description="GROK API for LLM calls")]
    llm_model: str = Field(default="qwen/qwen3-32b")
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

