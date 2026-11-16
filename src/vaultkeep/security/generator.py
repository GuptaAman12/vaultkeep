"""Secure random password generation."""

import secrets
import string

from ..constants import DEFAULT_PASSWORD_LENGTH


class PasswordGenerator:
    """Generates passwords from the selected character classes."""

    @staticmethod
    def generate(length=DEFAULT_PASSWORD_LENGTH, use_uppercase=True, use_lowercase=True,
                 use_digits=True, use_special=True):
        """Return a password, or None if no character type is selected."""
        chars = ""
        if use_uppercase:
            chars += string.ascii_uppercase
        if use_lowercase:
            chars += string.ascii_lowercase
        if use_digits:
            chars += string.digits
        if use_special:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"

        if not chars:
            return None
        return "".join(secrets.choice(chars) for _ in range(length))
