import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

if getattr(sys, 'frozen', False):
    ENV_PATH = Path(sys.executable).parent / ".env"
else:
    ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
if not ENV_PATH.exists():
    ENV_PATH.write_text("", encoding="utf-8")

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
        """Saves a configuration value both to memory and the persistent .env file."""
        set_key(str(ENV_PATH), key, value)
        os.environ[key] = value

    @staticmethod
    def get_pet_name() -> str:
        return SettingsManager.get("PET_NAME", "Pixel")

    @staticmethod
    def get_master_name() -> str:
        return SettingsManager.get("MASTER_NAME", "Master")
        
    @staticmethod
    def get_pet_color() -> str:
        return SettingsManager.get("PET_COLOR", "#ff9999")
        
    @staticmethod
    def get_master_color() -> str:
        return SettingsManager.get("MASTER_COLOR", "#99ccff")
        
    @staticmethod
    def get_model() -> str:
        return SettingsManager.get("LITELLM_MODEL", "")
        
    @staticmethod
    def get_pet_sprite() -> str:
        return SettingsManager.get("PET_SPRITE", "assets/cat 1.png")

    @staticmethod
    def get_openai_key() -> str:
        return SettingsManager.get("OPENAI_API_KEY", "")

    @staticmethod
    def get_anthropic_key() -> str:
        return SettingsManager.get("ANTHROPIC_API_KEY", "")

    @staticmethod
    def get_gemini_key() -> str:
        return SettingsManager.get("GEMINI_API_KEY", "")
