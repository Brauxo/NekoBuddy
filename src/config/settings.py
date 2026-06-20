import os
import logging
import threading
from dotenv import load_dotenv, set_key
from src.config.constants import (
    APP_ROOT, DEFAULT_PET_NAME, DEFAULT_MASTER_NAME,
    DEFAULT_PET_COLOR, DEFAULT_MASTER_COLOR, DEFAULT_SPRITE_PATH
)

logger = logging.getLogger("nekobuddy.config")

ENV_PATH = APP_ROOT / ".env"
if not ENV_PATH.exists():
    try:
        ENV_PATH.write_text("", encoding="utf-8")
    except Exception as e:
        logger.error(f"Could not create .env file: {e}")

load_dotenv(str(ENV_PATH))

class SettingsManager:
    """Manages the application configuration by reading/writing to the .env file."""
    
    @staticmethod
    def reload():
        """Reloads the environment variables from the .env file."""
        load_dotenv(str(ENV_PATH), override=True)

    @staticmethod
    def get(key: str, default: str = "") -> str:
        """Fetches a configuration value by key, returning a default if not found."""
        return os.getenv(key, default)

    @staticmethod
    def set(key: str, value: str):
        """Saves a configuration value to in-memory environment, and writes to disk on a background thread."""
        os.environ[key] = value
        
        def save_task():
            try:
                set_key(str(ENV_PATH), key, value)
            except Exception as e:
                logger.error(f"Failed to write setting '{key}' to disk: {e}")

        threading.Thread(target=save_task, daemon=True).start()

    @staticmethod
    def get_pet_name() -> str:
        return SettingsManager.get("PET_NAME", DEFAULT_PET_NAME)

    @staticmethod
    def get_master_name() -> str:
        return SettingsManager.get("MASTER_NAME", DEFAULT_MASTER_NAME)
        
    @staticmethod
    def get_pet_color() -> str:
        return SettingsManager.get("PET_COLOR", DEFAULT_PET_COLOR)
        
    @staticmethod
    def get_master_color() -> str:
        return SettingsManager.get("MASTER_COLOR", DEFAULT_MASTER_COLOR)
        
    @staticmethod
    def get_model() -> str:
        return SettingsManager.get("LITELLM_MODEL", "")
        
    @staticmethod
    def get_pet_sprite() -> str:
        return SettingsManager.get("PET_SPRITE", DEFAULT_SPRITE_PATH)

    @staticmethod
    def get_openai_key() -> str:
        return SettingsManager.get("OPENAI_API_KEY", "")

    @staticmethod
    def get_anthropic_key() -> str:
        return SettingsManager.get("ANTHROPIC_API_KEY", "")

    @staticmethod
    def get_gemini_key() -> str:
        return SettingsManager.get("GEMINI_API_KEY", "")
