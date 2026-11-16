"""Centralized logging setup and audit logger."""

import logging

from .constants import LOG_FILE, LOG_FORMAT, LOG_LEVEL


def setup_logger(name="PasswordManager"):
    """Return a logger configured with file and console handlers."""
    log = logging.getLogger(name)

    if not log.handlers:
        log.setLevel(getattr(logging, LOG_LEVEL))

        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        log.addHandler(file_handler)
        log.addHandler(console_handler)

    return log


logger = setup_logger()
