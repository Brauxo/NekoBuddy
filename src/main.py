import sys
import os
from pathlib import Path

# Suppress harmless Qt warnings about geometry/DPI in the terminal
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.window=false"

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from src.ui.pet_window import DesktopPet

def main():
    """
    Entry point for the application.
    Initializes the PySide6 application and starts the DesktopPet widget.
    """
    os.chdir(project_root)
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
