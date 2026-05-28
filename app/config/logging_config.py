import logging
import sys
from app.config.config import settings

# ANSI terminal character code constants for color mappings
COLOR_RESET = "\033[0m"
COLOR_BLUE = "\033[94m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_ORANGE = "\033[38;5;208m"
COLOR_DEFAULT = ""

class CustomColorFormatter(logging.Formatter):
    # Enforces a clean, highly structured layout for tracking operational logs natively
    LOG_FMT = "%(levelname)s | %(asctime)s | %(name)s:%(lineno)s | %(message)s"

    def format(self, record: logging.LogRecord) -> str:
        # Assigns highly distinguishable terminal coloring values matching log severity levels
        color = {
            logging.INFO: COLOR_BLUE,
            logging.WARNING: COLOR_YELLOW,
            logging.ERROR: COLOR_RED,
            logging.CRITICAL: COLOR_ORANGE,
            logging.DEBUG: COLOR_DEFAULT,
        }.get(record.levelno, COLOR_DEFAULT)

        # Creates the bounded string record payload wrapper dynamically
        formatter = logging.Formatter(self.LOG_FMT)
        formatted_message = formatter.format(record)
        return f"{color}{formatted_message}{COLOR_RESET}"

# Overrides external noisier connection libraries to prevent system stdout cluttering
logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(class_name: str) -> logging.Logger:
    # Factory system managing the non-duplicative provision of standard log wrappers
    logger = logging.getLogger(class_name)
    
    # Resolves your logging level dynamically matching your pydantic system parameters
    logger.setLevel(settings.LOG_LEVEL)

    # Critical Safeguard: Prevents attaching duplicate stream workers to the identical logger pipeline
    if not logger.handlers:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(settings.LOG_LEVEL)
        handler.setFormatter(CustomColorFormatter())
        logger.addHandler(handler)
        
    # Disables automatic event bubblings up into the hidden system root log container
    logger.propagate = False
    return logger