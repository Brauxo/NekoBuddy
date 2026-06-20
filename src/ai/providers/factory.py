from src.ai.providers.base import LLMProvider
from src.ai.providers.ollama_provider import OllamaProvider
from src.ai.providers.litellm_provider import LitellmProvider

def get_provider(model_string: str) -> tuple[LLMProvider, str]:
    """
    Returns the appropriate LLMProvider and the clean model name to pass to it.
    """
    if model_string.startswith("ollama/"):
        clean_model = model_string[7:]
        return OllamaProvider(), clean_model
    else:
        return LitellmProvider(), model_string
