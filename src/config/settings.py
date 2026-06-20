import os
import logging
import threading
from dotenv import load_dotenv, set_key
from src.config.constants import (
    APP_ROOT, DEFAULT_PET_NAME, DEFAULT_MASTER_NAME,
    DEFAULT_PET_COLOR, DEFAULT_MASTER_COLOR, DEFAULT_SPRITE_PATH,
    DEFAULT_PET_LANGUAGE

)

logger = logging.getLogger("nekobuddy.config")

ENV_PATH = APP_ROOT / ".env"
if not ENV_PATH.exists():
    try:
        ENV_PATH.write_text("", encoding="utf-8")
    except Exception as e:
        logger.error(f"Could not create .env file: {e}")

load_dotenv(str(ENV_PATH))

_pending_writes = {}
_pending_lock = threading.Lock()
_flush_scheduled = False


def _flush_to_disk():
    """Waits briefly for rapid writes to accumulate, then saves them all to disk in one pass."""
    import time
    global _flush_scheduled

    time.sleep(0.3)

    with _pending_lock:
        writes = dict(_pending_writes)
        _pending_writes.clear()
        _flush_scheduled = False

    for key, value in writes.items():
        try:
            set_key(str(ENV_PATH), key, value)
        except Exception as e:
            logger.error(f"Failed to write setting '{key}' to disk: {e}")


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
        """
        Updates a setting instantly in-memory and schedules a debounced disk write.
        
        Rapid successive calls (e.g. saving 10 settings at once) are coalesced
        into a single background flush, avoiding file contention on Windows.
        """
        global _flush_scheduled
        os.environ[key] = value

        with _pending_lock:
            _pending_writes[key] = value
            if not _flush_scheduled:
                _flush_scheduled = True
                threading.Thread(target=_flush_to_disk, daemon=True).start()

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
    def get_ollama_host() -> str:
        return SettingsManager.get("OLLAMA_HOST", "http://localhost:11434")
        
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

    @staticmethod
    def get_language() -> str:
        return SettingsManager.get("PET_LANGUAGE", DEFAULT_PET_LANGUAGE)

