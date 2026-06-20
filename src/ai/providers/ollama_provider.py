import ollama
import logging
from src.config.settings import SettingsManager
from src.ai.providers.base import LLMProvider

logger = logging.getLogger("nekobuddy.ai.ollama")

class OllamaProvider(LLMProvider):
    def generate(self, model: str, messages: list, json_mode: bool = False) -> str:
        host = SettingsManager.get("OLLAMA_HOST", "http://localhost:11434")
        
        options = {"stream": False}
        if json_mode:
            options["format"] = "json"
            
        try:
            logger.info(f"Ollama completion() model={model}; host={host}")
            client = ollama.Client(host=host)
            response = client.chat(
                model=model,
                messages=messages,
                **options
            )
            return response.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise e
