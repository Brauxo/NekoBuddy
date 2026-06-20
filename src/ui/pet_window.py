import logging
from PySide6.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QAction, QCursor

from src.core.state_machine import PetState
from src.ui.sprite_manager import SpriteManager
from src.config.animations import ANIMATIONS, BASE_ANIM_SPEED
from src.config.settings import SettingsManager
from src.presenter.pet_presenter import PetPresenter

logger = logging.getLogger("nekobuddy.view")

class DesktopPet(QWidget):
    """Frameless, transparent UI widget that renders the desktop pet and handles visual animations."""
    def __init__(self):
        super().__init__()
        
        self.current_frame_idx = 0
        self.current_anim_key = "idle"
        self.loaded_animations = {}
        
        self.init_ui()
        self.reload_sprite()
        
        # UI animation ticks
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(BASE_ANIM_SPEED)
        
        # Drag coordinates
        self.dragging = False
        self.offset = QPoint()

        # Connect Presenter
        self.presenter = PetPresenter(self)
        self.presenter.start()

    def init_ui(self):
        """Builds the layouts, transparency settings, and text widgets."""
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
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
        
        self.image_label = QLabel()
        self.image_label.setScaledContents(True)
        
        self.layout.addWidget(self.chat_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def reload_sprite(self):
        """Reloads the sprite sheet and rebuilds animation frame lists."""
        sprite_path = SettingsManager.get_pet_sprite()
        self.sprite_manager = SpriteManager(sprite_path, frame_width=32, frame_height=32, scale_factor=4)
        self.loaded_animations = {}
        for key, config in ANIMATIONS.items():
            self.loaded_animations[key] = self.sprite_manager.get_animation_sequence(config)
            
        if "idle" in self.loaded_animations and self.loaded_animations["idle"]:
            self.image_label.setPixmap(self.loaded_animations["idle"][0])

    def update_animation(self):
        """Ticks animation frames and adjusts timer interval based on animation speed multipliers."""
        state = self.presenter.state_machine.current_state
        anim_key = "idle"

        if state == PetState.WALKING:
            dx, dy = self.presenter.state_machine.walk_dir
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
                PetState.THINKING: "idle",
                PetState.SPEAKING: "sit_talk",
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
        
        if anim_key != self.current_anim_key:
            self.current_frame_idx = 0
            self.current_anim_key = anim_key
            
        self.current_frame_idx = (self.current_frame_idx + 1) % len(current_anim)
        pixmap = current_anim[self.current_frame_idx]
        self.image_label.setPixmap(pixmap)

    def move_pet(self, x: int, y: int):
        """Moves the desktop pet window to the designated coordinates."""
        self.move(x, y)

    def get_pet_position(self) -> QPoint:
        """Returns the current window coordinates of the pet."""
        return self.pos()

    def get_screen_geometry(self):
        """Returns the boundary limits of the primary active screen area."""
        return QApplication.primaryScreen().availableGeometry()

    def show_chat_bubble(self, html_text: str):
        """Displays the transparent speech bubble on top of the pet."""
        self.chat_label.setText(html_text)
        self.chat_label.show()

    def hide_chat_bubble(self):
        """Hides the speech bubble from view."""
        self.chat_label.hide()

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
        """Creates right-click actions and forwards selections to the presenter."""
        menu = QMenu(self)
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
        talk_action.triggered.connect(self.presenter.handle_talk_request)
        menu.addAction(talk_action)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.presenter.handle_settings_request)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        
        menu.exec_(QCursor.pos())
