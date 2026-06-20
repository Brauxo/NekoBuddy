import litellm
import logging
from src.ai.providers.base import LLMProvider

logger = logging.getLogger("nekobuddy.ai.litellm")

class LitellmProvider(LLMProvider):
    def generate(self, model: str, messages: list, json_mode: bool = False) -> str:
        kwargs = {
            "model": model,
            "messages": messages
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        try:
            response = litellm.completion(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LiteLLM error: {e}")
            raise e
