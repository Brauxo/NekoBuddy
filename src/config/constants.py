import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    APP_ROOT = Path(sys.executable).parent
else:
    APP_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = APP_ROOT / "data"
MEMORY_PATH = DATA_DIR / "memory.json"
LOG_PATH = DATA_DIR / "nekobuddy.log"

DEFAULT_PET_NAME = "Pixel"
DEFAULT_MASTER_NAME = "Master"
DEFAULT_PET_COLOR = "#ff9999"
DEFAULT_MASTER_COLOR = "#99ccff"
DEFAULT_SPRITE_PATH = "assets/cat 1.png"
