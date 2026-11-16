"""Secure random password generation."""

import secrets
import string

from ..constants import DEFAULT_PASSWORD_LENGTH

SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?"


class PasswordGenerator:
    """Generates passwords from the selected character classes."""

    @staticmethod
    def generate(length=DEFAULT_PASSWORD_LENGTH, use_uppercase=True, use_lowercase=True,
                 use_digits=True, use_special=True):
        """Return a password containing every selected character type."""
        groups = []
        if use_uppercase:
            groups.append(string.ascii_uppercase)
        if use_lowercase:
            groups.append(string.ascii_lowercase)
        if use_digits:
            groups.append(string.digits)
        if use_special:
            groups.append(SPECIAL_CHARS)

        if not groups:
            return None
        if length < len(groups):
            return None

        chars = "".join(groups)
        password_chars = [secrets.choice(group) for group in groups]
        password_chars.extend(secrets.choice(chars) for _ in range(length - len(password_chars)))
        secrets.SystemRandom().shuffle(password_chars)
        return "".join(password_chars)
