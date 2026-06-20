import sys
from PySide6.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, QTimer, QPoint, QThread, Signal
from PySide6.QtGui import QPixmap, QAction, QCursor

from src.core.state_machine import StateMachine, PetState
from src.ui.sprite_manager import SpriteManager
from src.ai.agent import ChatAgent, MoodAgent
from src.config.animations import ANIMATIONS, BASE_ANIM_SPEED
from src.config.settings import SettingsManager
from src.ui.settings_dialog import SettingsDialog

class ChatWorker(QThread):
    """Asynchronous QThread that handles sending user input to the ChatAgent LLM."""
    finished = Signal(str)

    def __init__(self, agent: ChatAgent, user_text: str, current_state: str):
        super().__init__()
        self.agent = agent
        self.user_text = user_text
        self.current_state = current_state

    def run(self):
        reply = self.agent.generate_response(self.user_text, self.current_state)
        self.finished.emit(reply)

class MoodWorker(QThread):
    """Asynchronous QThread that evaluates the current desktop context to determine the pet's mood."""
    finished = Signal(dict)

    def __init__(self, agent: MoodAgent, current_state: str, memory_history: list):
        super().__init__()
        self.agent = agent
        self.current_state = current_state
        self.memory_history = memory_history

    def run(self):
        result = self.agent.evaluate_mood(self.current_state, self.memory_history)
        self.finished.emit(result)

class DesktopPet(QWidget):
    """Main Frameless QWidget that renders the desktop pet, chat bubble, and manages timers."""
    def __init__(self):
        super().__init__()
        
        self.state_machine = StateMachine()
        self.chat_agent = ChatAgent()
        self.mood_agent = MoodAgent()
        self.chat_worker = None
        self.mood_worker = None
        
        self.reload_sprite()
        
        self.current_frame_idx = 0
        self.current_anim_key = "idle"
        
        self.init_ui()
        
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(BASE_ANIM_SPEED)
        
        self.logic_timer = QTimer(self)
        self.logic_timer.timeout.connect(self.update_logic)
        self.logic_timer.start(16)
        
        self.proactive_timer = QTimer(self)
        self.proactive_timer.timeout.connect(self.evaluate_mood_background)
        self.proactive_timer.start(60000)

    def init_ui(self):
        """Initializes the transparent UI, layouts, and hidden chat bubble."""
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Use a fixed size so the window NEVER changes dimensions. This 100% prevents teleporting.
        # Transparent pixels automatically pass mouse clicks through on Windows.
        self.setFixedSize(300, 350)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        
        self.chat_label = QLabel("")
        self.chat_label.setTextFormat(Qt.RichText)
        self.chat_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
                color: black;
            }
        """)
        self.chat_label.setWordWrap(True)
        self.chat_label.setMaximumWidth(250)
        self.chat_label.hide()
        
        self.last_user_text = ""
        
        self.image_label = QLabel()
        self.image_label.setScaledContents(True)
        if "idle" in self.loaded_animations and self.loaded_animations["idle"]:
            self.image_label.setPixmap(self.loaded_animations["idle"][0])
        
        self.layout.addWidget(self.chat_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)
        
        self.dragging = False
        self.offset = QPoint()

    def update_animation(self):
        """Calculates the correct animation key from the state machine and sets the current frame pixmap."""
        state = self.state_machine.current_state
        anim_key = "idle"

        if state == PetState.WALKING:
            dx, dy = self.state_machine.walk_dir
            if dy > 0 and dx == 0:
                anim_key = "walk_down"
            elif dy < 0 and dx == 0:
                anim_key = "walk_up"
            elif dy > 0 and dx != 0:
                anim_key = "walk_diagonal_down_left" if dx < 0 else "walk_diagonal_down_right"
            elif dy < 0 and dx != 0:
                anim_key = "walk_diagonal_up_left" if dx < 0 else "walk_diagonal_up_right"
            elif dy == 0 and dx != 0:
                anim_key = "walk_left" if dx < 0 else "walk_right"
        else:
            state_to_key = {
                PetState.IDLE: "idle",
                PetState.SLEEPING: "sleep",
                PetState.THINKING: "sit_down_transition", # It will sit and think
                PetState.SPEAKING: "sit_talk",            # It will literally talk!
                PetState.WASHING: "wash",
                PetState.YAWNING: "yawn",
                PetState.SCRATCHING: "scratch"
            }
            anim_key = state_to_key.get(state, "idle")
            
        current_anim = self.loaded_animations.get(anim_key)
        if not current_anim:
            return
            
        speed_mult = ANIMATIONS[anim_key].speed_multiplier if anim_key in ANIMATIONS else 1.0
        self.anim_timer.setInterval(int(BASE_ANIM_SPEED * speed_mult))
        
        # Reset frame index if animation changed
        if anim_key != self.current_anim_key:
            self.current_frame_idx = 0
            self.current_anim_key = anim_key
            
        self.current_frame_idx = (self.current_frame_idx + 1) % len(current_anim)
        pixmap = current_anim[self.current_frame_idx]
            
        self.image_label.setPixmap(pixmap)

    def update_logic(self):
        """Called at 60fps. Updates the state machine and physically moves the window if in a walking state."""
        self.state_machine.update()
        
        if self.state_machine.current_state == PetState.WALKING:
            speed = 2
            dx, dy = self.state_machine.walk_dir
            current_pos = self.pos()
            
            new_x = current_pos.x() + (speed * dx)
            new_y = current_pos.y() + (speed * dy)
            
            # Boundary checks
            screen_geom = QApplication.primaryScreen().availableGeometry()
            bounce_x = False
            bounce_y = False
            
            if new_x < screen_geom.left() or new_x + self.width() > screen_geom.right():
                bounce_x = True
            if new_y < screen_geom.top() or new_y + self.height() > screen_geom.bottom():
                bounce_y = True
                
            if bounce_x or bounce_y:
                new_dx = -dx if bounce_x else dx
                new_dy = -dy if bounce_y else dy
                self.state_machine.walk_dir = (new_dx, new_dy)
                
                # Recalculate with new direction
                new_x = current_pos.x() + (speed * new_dx)
                new_y = current_pos.y() + (speed * new_dy)
                
            self.move(new_x, new_y)

    # --- Interaction & Dragging ---
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            new_pos = self.mapToGlobal(event.position().toPoint()) - self.offset
            self.move(new_pos)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def contextMenuEvent(self, event):
        """Right click menu to interact or exit."""
        menu = QMenu(self)
        
        # Style the menu
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                color: black;
            }
            QMenu::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)

        talk_action = QAction("Talk to Cat", self)
        talk_action.triggered.connect(self.prompt_talk)
        menu.addAction(talk_action)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        
        menu.exec_(QCursor.pos())

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_():
            self.reload_sprite()

    def reload_sprite(self):
        sprite_path = SettingsManager.get_pet_sprite()
        self.sprite_manager = SpriteManager(sprite_path, frame_width=32, frame_height=32, scale_factor=4)
        self.loaded_animations = {}
        for key, config in ANIMATIONS.items():
            self.loaded_animations[key] = self.sprite_manager.get_animation_sequence(config)

    def prompt_talk(self):
        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Chat", "Say something to your cat:")
        if ok and text:
            self.interact_with_ai(text)

    def evaluate_mood_background(self):
        if self.mood_worker is not None and self.mood_worker.isRunning():
            return
            
        # We only check mood if the cat is not actively speaking or thinking
        if self.state_machine.current_state not in (PetState.THINKING, PetState.SPEAKING):
            self.mood_worker = MoodWorker(self.mood_agent, self.state_machine.current_state.name, self.chat_agent.history)
            self.mood_worker.finished.connect(self.on_mood_response)
            self.mood_worker.start()
            
    def on_mood_response(self, result: dict):
        mood = result.get("mood", "OBSERVANT")
        speech = result.get("speech")
        
        # Apply the new mood to the state machine
        self.state_machine.set_mood(mood)
        
        # If the Mood Agent decided it wants to proactively talk
        if speech:
            self.state_machine.change_state(PetState.SPEAKING)
            
            pet_name = SettingsManager.get_pet_name()
            pet_color = SettingsManager.get_pet_color()
            html = f"<b><span style='color: {pet_color};'>{pet_name}:</span></b> {speech}"
            
            self.chat_label.setText(html)
            self.chat_label.show()
            
            self.chat_agent.history.append({"role": "assistant", "content": speech})
            self.chat_agent._save_memory()
            
            QTimer.singleShot(5000, self.hide_chat_bubble)

    def interact_with_ai(self, text: str):
        self.last_user_text = text
        self.state_machine.change_state(PetState.THINKING)
        
        pet_color = SettingsManager.get_pet_color()
        html = f"<span style='color: {pet_color};'><i>...thinking...</i></span>"
        
        self.chat_label.setText(html)
        self.chat_label.show()
        
        self.chat_worker = ChatWorker(self.chat_agent, text, self.state_machine.current_state.name)
        self.chat_worker.finished.connect(self.on_chat_response)
        self.chat_worker.start()

    def on_chat_response(self, reply: str):
        if self.state_machine.current_state == PetState.THINKING:
            self.state_machine.change_state(PetState.SPEAKING)
            
        pet_name = SettingsManager.get_pet_name()
        pet_color = SettingsManager.get_pet_color()
        
        html = f"<b><span style='color: {pet_color};'>{pet_name}:</span></b> {reply}"
            
        self.chat_label.setText(html)
        
        # Hide the bubble after a few seconds
        QTimer.singleShot(7000, self.hide_chat_bubble)

    def hide_chat_bubble(self):
        self.chat_label.hide()
        if self.state_machine.current_state in (PetState.THINKING, PetState.SPEAKING):
            self.state_machine.change_state(PetState.IDLE)
