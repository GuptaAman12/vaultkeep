"""Password strength scoring based on estimated entropy and known patterns."""

import math
import re
import string

from ..constants import (
    MIN_LENGTH_FAIR, MIN_LENGTH_GOOD, MIN_LENGTH_STRONG, MIN_LENGTH_VERY_STRONG,
    MIN_LENGTH_WEAK, STRENGTH_FAIR, STRENGTH_GOOD, STRENGTH_STRONG,
    STRENGTH_VERY_STRONG, STRENGTH_WEAK,
)


class PasswordStrengthChecker:
    """Estimates how hard a password would be to guess."""

    COMMON_PASSWORDS = {
        "123456", "1234567", "12345678", "123456789", "123123", "654321",
        "password", "password1", "passw0rd", "qwerty", "qwerty123", "abc123",
        "letmein", "trustno1", "dragon", "baseball", "iloveyou", "sunshine",
        "master", "monkey", "shadow", "superman", "batman", "welcome",
        "admin", "login", "freedom", "whatever", "starwars", "princess",
        "football", "soccer", "hockey", "baseball", "ashley", "bailey",
        "charlie", "donald", "jessica", "michael", "taylor", "thomas",
        "computer", "internet", "service", "secret", "summer", "winter",
        "qazwsx", "1q2w3e", "zaq12wsx", "asdfgh", "zxcvbnm", "qwertyuiop",
    }

    REPEATED_CHARS = re.compile(r"(.)\1{2,}")
    SEQUENTIAL_DIGITS = re.compile(r"(012|123|234|345|456|567|678|789|890)")
    SEQUENTIAL_LETTERS = re.compile(
        r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)"
    )
    KEYBOARD_WALK = re.compile(r"(qwerty|asdf|zxcv|qazwsx|1q2w|zaq12|poiu|lkjh|mnbv)")
    YEAR = re.compile(r"(19\d{2}|20\d{2})")

    @staticmethod
    def check_strength(password):
        """Return (level, label, feedback) for a password."""
        if not password:
            return STRENGTH_WEAK, "Very Weak", ["Password is empty"]

        length = len(password)
        feedback = []
        has_lowercase = any(c.islower() for c in password)
        has_uppercase = any(c.isupper() for c in password)
        has_digits = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        pool = 0
        if has_lowercase:
            pool += len(string.ascii_lowercase)
        if has_uppercase:
            pool += len(string.ascii_uppercase)
        if has_digits:
            pool += len(string.digits)
        if has_special:
            pool += 32

        entropy = length * math.log2(pool) if pool else 0

        if length < MIN_LENGTH_WEAK:
            feedback.append(f"Too short (minimum {MIN_LENGTH_WEAK} characters)")
            entropy -= 20
        elif length < MIN_LENGTH_FAIR:
            feedback.append(f"Use at least {MIN_LENGTH_FAIR} characters")
        elif length < MIN_LENGTH_GOOD:
            feedback.append(f"Aim for {MIN_LENGTH_GOOD} characters or more")
        elif length < MIN_LENGTH_STRONG:
            feedback.append(f"Use {MIN_LENGTH_STRONG} characters for a strong password")
        elif length < MIN_LENGTH_VERY_STRONG:
            feedback.append(f"Use {MIN_LENGTH_VERY_STRONG} characters for a very strong password")

        lowered = password.lower()
        checker = PasswordStrengthChecker
        if lowered in checker.COMMON_PASSWORDS:
            feedback.append("This is a commonly used password")
            entropy -= 30
        elif any(word in lowered for word in checker.COMMON_PASSWORDS if len(word) >= 4):
            feedback.append("Contains a commonly used word")
            entropy -= 15

        variety = sum((has_lowercase, has_uppercase, has_digits, has_special))
        if variety == 1:
            feedback.append("Use a mix of character types")
            entropy -= 6
        if not has_lowercase:
            feedback.append("Add lowercase letters")
        if not has_uppercase:
            feedback.append("Add uppercase letters")
        if not has_digits:
            feedback.append("Add numbers")
        if not has_special:
            feedback.append("Add special characters")

        if checker.REPEATED_CHARS.search(password):
            feedback.append("Avoid repeating characters")
            entropy -= 8
        if checker.SEQUENTIAL_DIGITS.search(password):
            feedback.append("Avoid sequential numbers")
            entropy -= 8
        if checker.SEQUENTIAL_LETTERS.search(lowered):
            feedback.append("Avoid sequential letters")
            entropy -= 8
        if checker.KEYBOARD_WALK.search(lowered):
            feedback.append("Avoid keyboard patterns")
            entropy -= 12
        if checker.YEAR.search(password):
            feedback.append("Avoid years and dates")
            entropy -= 8

        entropy = max(entropy, 0)
        if entropy < 28:
            level, label = STRENGTH_WEAK, "Weak"
        elif entropy < 36:
            level, label = STRENGTH_FAIR, "Fair"
        elif entropy < 60:
            level, label = STRENGTH_GOOD, "Good"
        elif entropy < 80:
            level, label = STRENGTH_STRONG, "Strong"
        else:
            level, label = STRENGTH_VERY_STRONG, "Very Strong"

        if not feedback:
            feedback.append("Excellent password!")
        return level, label, feedback
