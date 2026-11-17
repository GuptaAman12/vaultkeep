"""Application constants and configuration values."""

import sys
from pathlib import Path

# A frozen app keeps its vault beside the exe; source runs use the project folder.
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = str(PROJECT_ROOT / "passwords.enc")
SALT_FILE = str(PROJECT_ROOT / "salt.key")
LOG_FILE = str(PROJECT_ROOT / "password_manager.log")

# Encryption settings
PBKDF2_ITERATIONS = 100000
KEY_LENGTH = 32
SALT_LENGTH = 16

# Password generator defaults
DEFAULT_PASSWORD_LENGTH = 16
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 64

# Password strength thresholds
STRENGTH_WEAK = 0
STRENGTH_FAIR = 1
STRENGTH_GOOD = 2
STRENGTH_STRONG = 3
STRENGTH_VERY_STRONG = 4

MIN_LENGTH_WEAK = 6
MIN_LENGTH_FAIR = 8
MIN_LENGTH_GOOD = 12
MIN_LENGTH_STRONG = 16
MIN_LENGTH_VERY_STRONG = 20

# GUI settings
APP_NAME = "Vaultkeep"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
DIALOG_WIDTH = 500
DIALOG_HEIGHT = 400
GENERATOR_DIALOG_WIDTH = 450
GENERATOR_DIALOG_HEIGHT = 400
SEARCH_DEBOUNCE_MS = 150
CLIPBOARD_CLEAR_MS = 30000
AUTO_LOCK_MS = 300000
PASSWORD_CHANGE_INTERVAL_DAYS = 60
PASSWORD_REMINDER_SNOOZE_DAYS = 7
THEME = "clam"

# Export/Import settings
EXPORT_FILE_EXTENSION = ".json"
EXPORT_FILE_TYPES = [("JSON files", "*.json"), ("All files", "*.*")]

# Logging settings
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
