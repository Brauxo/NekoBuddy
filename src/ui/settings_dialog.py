import os
import subprocess
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QComboBox, QColorDialog,
                               QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from src.config.settings import SettingsManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NekoBuddy Settings")
        self.setMinimumWidth(400)
        
        self.pet_color = SettingsManager.get_pet_color()
        self.master_color = SettingsManager.get_master_color()
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
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
        current_friendly_name = "Black Cat" # Default
        
        for friendly_name, filename in self.sprite_map.items():
            self.sprite_combo.addItem(friendly_name)
            if filename == current_sprite_file:
                current_friendly_name = friendly_name
                
        self.sprite_combo.setCurrentText(current_friendly_name)
        form_layout.addRow("Pet Color:", self.sprite_combo)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        current_model = SettingsManager.get_model()
        
        if current_model:
            self.model_combo.addItem(current_model)
        else:
            self.model_combo.addItem("Enter or select a model...")
            
        form_layout.addRow("LLM Model:", self.model_combo)
        
        layout.addLayout(form_layout)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save & Apply")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.fetch_ollama_models()

    def fetch_ollama_models(self):
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')[1:]
            models = [line.split()[0] for line in lines if line.strip()]
            ollama_models = [f"ollama/{m}" for m in models]

            for m in ollama_models:
                if m != self.model_combo.currentText() and m != "Enter or select a model...":
                    self.model_combo.addItem(m)
        except Exception as e:
            print("Could not fetch ollama models:", e)

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
        SettingsManager.set("PET_NAME", self.pet_name_input.text().strip())
        SettingsManager.set("MASTER_NAME", self.master_name_input.text().strip())
        SettingsManager.set("PET_COLOR", self.pet_color)
        SettingsManager.set("MASTER_COLOR", self.master_color)
        
        friendly_name = self.sprite_combo.currentText()
        filename = self.sprite_map.get(friendly_name, "cat 1.png")
        SettingsManager.set("PET_SPRITE", f"assets/{filename}")
        
        selected_model = self.model_combo.currentText().strip()
        if selected_model != "Enter or select a model...":
            SettingsManager.set("LITELLM_MODEL", selected_model)
        
        SettingsManager.reload()
        
        QMessageBox.information(self, "Settings Saved", "Settings updated! The brain has been reloaded.")
        self.accept()
