import logging
import random
from PySide6.QtCore import QObject, QTimer, QThread, Signal, Qt
from PySide6.QtWidgets import QApplication, QInputDialog

from src.core.state_machine import StateMachine, PetState
from src.ai.agent import ChatAgent, MoodAgent
from src.config.settings import SettingsManager

logger = logging.getLogger("nekobuddy.presenter")

class ChatWorker(QThread):
    """Handles sending user input to the LLM agent on a background thread."""
    finished = Signal(str)

    def __init__(self, agent: ChatAgent, user_text: str, current_state: str):
        super().__init__()
        self.agent = agent
        self.user_text = user_text
        self.current_state = current_state

    def run(self):
        try:
            reply = self.agent.generate_response(self.user_text, self.current_state)
            self.finished.emit(reply)
        except Exception as e:
            logger.exception("Error in ChatWorker thread execution")
            self.finished.emit(f"*hiss* Unhandled crash: {e}")

class MoodWorker(QThread):
    """Evaluates the user's active window environment context on a background thread."""
    finished = Signal(dict)

    def __init__(self, agent: MoodAgent, current_state: str, memory_history: list):
        super().__init__()
        self.agent = agent
        self.current_state = current_state
        self.memory_history = memory_history

    def run(self):
        try:
            result = self.agent.evaluate_mood(self.current_state, self.memory_history)
            self.finished.emit(result)
        except Exception as e:
            logger.exception("Error in MoodWorker thread execution")

class PetPresenter(QObject):
    """
    Coordinates the core application state, timers, worker threads,
    and business logic, telling the view what to display.
    """
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.state_machine = StateMachine()
        self.chat_agent = ChatAgent()
        self.mood_agent = MoodAgent()
        
        self.chat_worker = None
        self.mood_worker = None
        
        self.logic_timer = QTimer(self)
        self.logic_timer.timeout.connect(self.update_logic)
        
        self.proactive_timer = QTimer(self)
        self.proactive_timer.timeout.connect(self.evaluate_mood_background)

    def start(self):
        """Starts all background logic timers."""
        self.logic_timer.start(16)  # ~60 fps logic tick
        self._schedule_next_mood()

    def _schedule_next_mood(self):
        """Schedules the next mood evaluation after a random delay between 40-80 seconds."""
        delay = random.randint(40000, 80000)
        self.proactive_timer.singleShot(delay, self.evaluate_mood_background)

    def update_logic(self):
        """Updates the state machine and coordinates boundaries collision and pet positioning."""
        self.state_machine.update()
        
        if self.state_machine.current_state == PetState.WALKING:
            speed = 2
            dx, dy = self.state_machine.walk_dir
            current_pos = self.view.get_pet_position()
            
            new_x = current_pos.x() + (speed * dx)
            new_y = current_pos.y() + (speed * dy)
            
            screen_geom = self.view.get_screen_geometry()
            bounce_x = False
            bounce_y = False
            
            if new_x < screen_geom.left() or new_x + self.view.width() > screen_geom.right():
                bounce_x = True
            if new_y < screen_geom.top() or new_y + self.view.height() > screen_geom.bottom():
                bounce_y = True
                
            if bounce_x or bounce_y:
                new_dx = -dx if bounce_x else dx
                new_dy = -dy if bounce_y else dy
                self.state_machine.walk_dir = (new_dx, new_dy)
                
                new_x = current_pos.x() + (speed * new_dx)
                new_y = current_pos.y() + (speed * new_dy)
                
            self.view.move_pet(new_x, new_y)

    def handle_drag_start(self):
        """Transitions the pet into the DRAGGING state and hides any active chat bubble."""
        self.state_machine.change_state(PetState.DRAGGING)
        self.view.hide_chat_bubble()

    def handle_drag_stop(self):
        """Returns the pet to the IDLE state, hides the bubble, records the grab event, and triggers mood check."""
        if self.state_machine.current_state == PetState.DRAGGING:
            self.state_machine.change_state(PetState.IDLE)
            self.view.hide_chat_bubble()
            
            pet_name = SettingsManager.get_pet_name()
            self.chat_agent.add_event(f"The user grabbed and dragged {pet_name} across the screen. React to this action.")
            self.evaluate_mood_background()



    def handle_talk_request(self):
        """Prompts the user for dialogue and triggers the chat lifecycle."""
        text, ok = QInputDialog.getText(self.view, "Chat", "Say something to your cat:")
        if ok and text:
            self.interact_with_ai(text)

    def interact_with_ai(self, text: str):
        """Puts the pet into thinking mode and initializes the LLM completion thread."""
        self.state_machine.change_state(PetState.THINKING)
        
        pet_color = SettingsManager.get_pet_color()
        html = f"<span style='color: {pet_color};'><i>...thinking...</i></span>"
        self.view.show_chat_bubble(html)
        
        self.chat_worker = ChatWorker(self.chat_agent, text, self.state_machine.current_state.name)
        self.chat_worker.finished.connect(self.on_chat_response)
        self.chat_worker.start()

    def on_chat_response(self, reply: str):
        """Processes the LLM response, displaying it in the bubble and scheduling hides."""
        if self.state_machine.current_state == PetState.THINKING:
            self.state_machine.change_state(PetState.SPEAKING)
            
        pet_name = SettingsManager.get_pet_name()
        pet_color = SettingsManager.get_pet_color()
        html = f"<b><span style='color: {pet_color};'>{pet_name}:</span></b> {reply}"
        self.view.show_chat_bubble(html)
        
        QTimer.singleShot(7000, self.hide_chat_bubble)

    def evaluate_mood_background(self):
        """Triggers the mood evaluation worker if the pet is in a stable state."""
        if self.mood_worker is not None and self.mood_worker.isRunning():
            return
            
        if self.state_machine.current_state not in (PetState.THINKING, PetState.SPEAKING):
            self.mood_worker = MoodWorker(self.mood_agent, self.state_machine.current_state.name, self.chat_agent.history)
            self.mood_worker.finished.connect(self.on_mood_response)
            self.mood_worker.start()

    def on_mood_response(self, result: dict):
        """Applies evaluated mood shift and displays proactive speech."""
        mood = result.get("mood", "OBSERVANT")
        speech = result.get("speech")
        
        self.state_machine.set_mood(mood)
        
        if speech:
            self.state_machine.change_state(PetState.SPEAKING)
            
            pet_name = SettingsManager.get_pet_name()
            pet_color = SettingsManager.get_pet_color()
            html = f"<b><span style='color: {pet_color};'>{pet_name}:</span></b> {speech}"
            
            self.view.show_chat_bubble(html)
            
            self.chat_agent.history.append({"role": "assistant", "content": speech})
            self.chat_agent._save_memory()
            
            QTimer.singleShot(5000, self.hide_chat_bubble)
        
        self._schedule_next_mood()

    def hide_chat_bubble(self):
        """Closes the UI bubble and returns the pet state machine to IDLE."""
        self.view.hide_chat_bubble()
        if self.state_machine.current_state in (PetState.THINKING, PetState.SPEAKING):
            self.state_machine.change_state(PetState.IDLE)
            
    def handle_settings_request(self):
        """Displays settings configuration dialog and reloads visuals if updated."""
        from src.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.view)
        if dialog.exec_():
            self.view.reload_sprite()
