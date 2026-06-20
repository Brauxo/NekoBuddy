import os
import logging
import subprocess
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QComboBox, QColorDialog,
                               QFormLayout, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor

from src.config.settings import SettingsManager

logger = logging.getLogger("nekobuddy.settings")

class OllamaWorker(QThread):
    """Background worker that queries the local system for available Ollama models."""
    finished = Signal(list)

    def run(self):
        models = []
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                startupinfo=startupinfo,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                models = [f"ollama/{line.split()[0]}" for line in lines if line.strip()]
        except Exception as e:
            logger.warning(f"Could not retrieve local Ollama models list: {e}")
            
        self.finished.emit(models)


class SettingsDialog(QDialog):
    """Configuration interface for setting names, colors, sprite types, and LLM backends."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NekoBuddy Settings")
        self.setMinimumWidth(450)
        
        self.pet_color = SettingsManager.get_pet_color()
        self.master_color = SettingsManager.get_master_color()
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- General settings ---
        general_group = QGroupBox("General")
        form_layout = QFormLayout()

        self.pet_name_input = QLineEdit(SettingsManager.get_pet_name())
        self.master_name_input = QLineEdit(SettingsManager.get_master_name())
        
        form_layout.addRow("Pet Name:", self.pet_name_input)
        form_layout.addRow("Master Name:", self.master_name_input)

        self.pet_color_btn = QPushButton("Pick Color")
        self.pet_color_btn.setStyleSheet(f"background-color: {self.pet_color}; color: black;")
        self.pet_color_btn.clicked.connect(self.pick_pet_color)
        
        self.master_color_btn = QPushButton("Pick Color")
        self.master_color_btn.setStyleSheet(f"background-color: {self.master_color}; color: black;")
        self.master_color_btn.clicked.connect(self.pick_master_color)
        
        form_layout.addRow("Pet Name Color:", self.pet_color_btn)
        form_layout.addRow("Master Name Color:", self.master_color_btn)

        self.sprite_combo = QComboBox()
        self.sprite_map = {
            "Black Cat": "cat 1.png",
            "Orange Cat": "cat 1.6.png",
            "White Cat": "cat 1.9.png"
        }

        current_sprite_file = os.path.basename(SettingsManager.get_pet_sprite())
        current_friendly_name = "Black Cat"
        
        for friendly_name, filename in self.sprite_map.items():
            self.sprite_combo.addItem(friendly_name)
            if filename == current_sprite_file:
                current_friendly_name = friendly_name
                
        self.sprite_combo.setCurrentText(current_friendly_name)
        form_layout.addRow("Pet Color:", self.sprite_combo)
        
        self.language_combo = QComboBox()
        languages = [
            "Arabic", "Chinese (Simplified)", "Chinese (Traditional)",
            "Czech", "Danish", "Dutch", "English", "Finnish", "French",
            "German", "Greek", "Hebrew", "Hindi", "Hungarian", "Indonesian",
            "Italian", "Japanese", "Korean", "Norwegian", "Polish",
            "Portuguese", "Romanian", "Russian", "Spanish", "Swedish",
            "Thai", "Turkish", "Ukrainian", "Vietnamese",
        ]
        for lang in languages:
            self.language_combo.addItem(lang)
        self.language_combo.setCurrentText(SettingsManager.get_language())
        form_layout.addRow("Language:", self.language_combo)
        
        general_group.setLayout(form_layout)

        main_layout.addWidget(general_group)

        # --- AI API Settings ---
        api_group = QGroupBox("AI Configuration")
        api_layout = QFormLayout()

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        current_model = SettingsManager.get_model()
        
        if current_model:
            self.model_combo.addItem(current_model)
        else:
            self.model_combo.addItem("Loading models...")
            
        api_layout.addRow("LLM Model:", self.model_combo)

        self.openai_input = QLineEdit(SettingsManager.get_openai_key())
        self.openai_input.setEchoMode(QLineEdit.Password)
        api_layout.addRow("OpenAI API Key:", self.openai_input)

        self.anthropic_input = QLineEdit(SettingsManager.get_anthropic_key())
        self.anthropic_input.setEchoMode(QLineEdit.Password)
        api_layout.addRow("Anthropic API Key:", self.anthropic_input)

        self.gemini_input = QLineEdit(SettingsManager.get_gemini_key())
        self.gemini_input.setEchoMode(QLineEdit.Password)
        api_layout.addRow("Gemini API Key:", self.gemini_input)

        api_group.setLayout(api_layout)
        main_layout.addWidget(api_group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save & Apply")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        # Load Ollama models in background
        self.ollama_worker = OllamaWorker()
        self.ollama_worker.finished.connect(self.on_ollama_models_loaded)
        self.ollama_worker.start()

    def on_ollama_models_loaded(self, models: list):
        """Callback when local Ollama models list has loaded."""
        current_text = self.model_combo.currentText()
        if current_text == "Loading models...":
            self.model_combo.clear()
            self.model_combo.addItem("Enter or select a model...")
            current_text = "Enter or select a model..."

        for m in models:
            if m != current_text:
                self.model_combo.addItem(m)

    def pick_pet_color(self):
        color = QColorDialog.getColor(QColor(self.pet_color), self, "Pick Pet Name Color")
        if color.isValid():
            self.pet_color = color.name()
            self.pet_color_btn.setStyleSheet(f"background-color: {self.pet_color}; color: black;")

    def pick_master_color(self):
        color = QColorDialog.getColor(QColor(self.master_color), self, "Pick Master Name Color")
        if color.isValid():
            self.master_color = color.name()
            self.master_color_btn.setStyleSheet(f"background-color: {self.master_color}; color: black;")

    def save_settings(self):
        """Validates, applies, and persists the configuration settings."""
        SettingsManager.set("PET_NAME", self.pet_name_input.text().strip())
        SettingsManager.set("MASTER_NAME", self.master_name_input.text().strip())
        SettingsManager.set("PET_COLOR", self.pet_color)
        SettingsManager.set("MASTER_COLOR", self.master_color)
        
        friendly_name = self.sprite_combo.currentText()
        filename = self.sprite_map.get(friendly_name, "cat 1.png")
        SettingsManager.set("PET_SPRITE", f"assets/{filename}")
        
        selected_lang = self.language_combo.currentText()
        SettingsManager.set("PET_LANGUAGE", selected_lang)
        
        selected_model = self.model_combo.currentText().strip()
        if selected_model not in ("Enter or select a model...", "Loading models..."):
            SettingsManager.set("LITELLM_MODEL", selected_model)

        # Save API keys
        SettingsManager.set("OPENAI_API_KEY", self.openai_input.text().strip())
        SettingsManager.set("ANTHROPIC_API_KEY", self.anthropic_input.text().strip())
        SettingsManager.set("GEMINI_API_KEY", self.gemini_input.text().strip())
        
        logger.info("Settings saved.")
        QMessageBox.information(self, "Settings Saved", "Settings updated! The brain has been reloaded.")
        self.accept()
