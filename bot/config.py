"""Configuration module for the LMS bot.

Loads settings from environment variables using pydantic-settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the project root directory (parent of bot/)
BOT_DIR = Path(__file__).parent
ROOT_DIR = BOT_DIR.parent
ENV_FILE = ROOT_DIR / ".env.bot.secret"


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    model_config: Final[SettingsConfigDict] = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str | None = None

    # LMS API
    lms_api_base_url: str | None = None
    lms_api_key: str | None = None

    # LLM API
    llm_api_key: str | None = None
    llm_api_base_url: str | None = None
    llm_api_model: str = "coder-model"


@lru_cache
def get_settings() -> BotSettings:
    """Get cached bot settings instance."""
    return BotSettings()
