from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, model: str, messages: list, json_mode: bool = False) -> str:
        """
        Generate a response from the LLM.
        :param model: The specific model name to use.
        :param messages: A list of dicts with 'role' and 'content'.
        :param json_mode: If True, the provider should enforce JSON output.
        :return: The generated response string.
        """
        pass
