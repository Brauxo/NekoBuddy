import json
import litellm
import pywinctl
from pathlib import Path
from datetime import datetime
from src.config.settings import SettingsManager
from src.config.personality import get_chat_prompt, get_mood_prompt

def get_context(current_state: str) -> str:
    """Generates a system context string describing the current active window and pet state."""
    try:
        active_window = pywinctl.getActiveWindowTitle()
        if not active_window:
            active_window = "Desktop"
    except:
        active_window = "Unknown"
        
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"[[SYSTEM CONTEXT: It is {time_str}. User's active window: '{active_window}'. Your avatar is currently: {current_state}]]\n"


class ChatAgent:
    """Handles explicit user conversation with memory."""
    def __init__(self):
        self.memory_path = Path("data/memory.json")
        self.history = self._load_memory()
        
    def _load_memory(self):
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
            except:
                pass
        return [{"role": "system", "content": get_chat_prompt()}]
        
    def _save_memory(self):
        """Saves the conversation history to the persistent JSON file."""
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print("Failed to save memory:", e)

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
            return f"*hiss* Error connecting to my brain: {str(e)}"

class MoodAgent:
    """Runs asynchronously to determine the cat's mood and trigger proactive speech."""
    def __init__(self):
        pass
        
    def evaluate_mood(self, current_state: str, memory_history: list) -> dict:
        """Asks the LLM to evaluate the desktop context and decide the pet's next mood."""
        messages = [{"role": "system", "content": get_mood_prompt()}]
        
        # Give it a summary of recent conversation so it knows what was just talked about
        recent_history = [msg for msg in memory_history[-5:] if msg.get("role") != "system"]
        history_text = "Recent conversation:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in recent_history])
        
        prompt = get_context(current_state) + history_text + "\nEvaluate mood and output JSON:"
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = litellm.completion(model=SettingsManager.get_model(), messages=messages, response_format={"type": "json_object"})
            reply = response.choices[0].message.content
            # litellm will return JSON if possible, otherwise we try parsing it
            import re
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
            print("Mood Agent Error:", e)
            return {"mood": "OBSERVANT", "speech": None}
