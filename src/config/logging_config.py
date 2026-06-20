import sys
import logging
from src.config.constants import DATA_DIR, LOG_PATH

def setup_logging():
    """
    Initializes the logging system. Sets up file-based logging
    in addition to stdout streams, and overrides sys.excepthook
    to log unhandled application exceptions.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    def exception_hook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger("nekobuddy").critical(
            "Unhandled exception occurred",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = exception_hook
