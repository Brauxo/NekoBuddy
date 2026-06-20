import json
import logging
import threading
import litellm
import pywinctl
from datetime import datetime
from src.config.settings import SettingsManager
from src.config.personality import get_chat_prompt, get_mood_prompt
from src.config.constants import MEMORY_PATH

logger = logging.getLogger("nekobuddy.ai")

def get_context(current_state: str) -> str:
    """Generates a system context string describing the current active window and pet state."""
    try:
        active_window = pywinctl.getActiveWindowTitle()
        if not active_window:
            active_window = "Desktop"
    except Exception as e:
        logger.warning(f"Failed to query active window title: {e}")
        active_window = "Unknown"
        
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"[[SYSTEM CONTEXT: It is {time_str}. User's active window: '{active_window}'. Your avatar is currently: {current_state}]]\n"


class ChatAgent:
    """Handles explicit user conversation with memory."""
    def __init__(self):
        self.memory_path = MEMORY_PATH
        self.history = self._load_memory()
        
    def _load_memory(self) -> list:
        """Loads the conversation history from the persistent JSON file, injecting the system prompt."""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if len(data) > 0 and data[0].get("role") == "system":
                        data[0]["content"] = get_chat_prompt()
                    else:
                        data.insert(0, {"role": "system", "content": get_chat_prompt()})
                    return data
            except Exception as e:
                logger.error(f"Failed to load conversation history: {e}")
        return [{"role": "system", "content": get_chat_prompt()}]
        
    def _save_memory(self):
        """Saves the conversation history to the persistent JSON file on a background thread."""
        history_snapshot = list(self.history)
        
        def save_task():
            try:
                self.memory_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.memory_path, 'w', encoding='utf-8') as f:
                    json.dump(history_snapshot, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Failed to save conversation memory: {e}")

        threading.Thread(target=save_task, daemon=True).start()

    def generate_response(self, user_text: str, current_state: str) -> str:
        """Appends the user's message to history and requests an LLM completion."""
        full_msg = get_context(current_state) + (user_text if user_text else "(The user is looking at you)")
        self.history.append({"role": "user", "content": full_msg})
        
        try:
            response = litellm.completion(model=SettingsManager.get_model(), messages=self.history)
            reply = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": reply})
            
            if len(self.history) > 21:
                self.history = [self.history[0]] + self.history[-20:]
            self._save_memory()
            return reply
        except Exception as e:
            logger.exception("Error during LLM chat generation")
            return f"*hiss* Error connecting to my brain: {str(e)}"


class MoodAgent:
    """Runs asynchronously to determine the cat's mood and trigger proactive speech."""
    def __init__(self):
        pass
        
    def evaluate_mood(self, current_state: str, memory_history: list) -> dict:
        """Asks the LLM to evaluate the desktop context and decide the pet's next mood."""
        messages = [{"role": "system", "content": get_mood_prompt()}]
        
        recent_history = [msg for msg in memory_history[-5:] if msg.get("role") != "system"]
        history_text = "Recent conversation:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in recent_history])
        
        prompt = get_context(current_state) + history_text + "\nEvaluate mood and output JSON:"
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = litellm.completion(
                model=SettingsManager.get_model(),
                messages=messages,
                response_format={"type": "json_object"}
            )
            reply = response.choices[0].message.content
            # litellm will return JSON if possible, otherwise we try parsing it
            json_str = reply
            # Strip markdown if present
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
                
            data = json.loads(json_str.strip())
            return {
                "mood": data.get("mood", "OBSERVANT"),
                "speech": data.get("speech")
            }
        except Exception as e:
            logger.error(f"Mood Agent evaluation failed: {e}")
            return {"mood": "OBSERVANT", "speech": None}
