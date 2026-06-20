import sys
import os
import logging
from pathlib import Path

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.window=false"

if getattr(sys, 'frozen', False):
    project_root = str(Path(sys.executable).parent)
else:
    project_root = str(Path(__file__).resolve().parent.parent)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config.logging_config import setup_logging
setup_logging()

logger = logging.getLogger("nekobuddy.main")

from PySide6.QtWidgets import QApplication
from src.ui.pet_window import DesktopPet

def main():
    """Entry point for the NekoBuddy desktop pet application."""
    logger.info("Starting NekoBuddy application...")
    os.chdir(project_root)
    
    try:
        app = QApplication(sys.argv)
        pet = DesktopPet()
        pet.show()
        logger.info("NekoBuddy window shown successfully. Entering main event loop.")
        sys.exit(app.exec())
    except Exception as e:
        logger.critical("Fatal error occurred during application runtime", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
