"""Heuristic password strength scoring."""

import re

from ..constants import (
    MIN_LENGTH_FAIR, MIN_LENGTH_GOOD, MIN_LENGTH_STRONG, MIN_LENGTH_VERY_STRONG,
    MIN_LENGTH_WEAK, STRENGTH_FAIR, STRENGTH_GOOD, STRENGTH_STRONG,
    STRENGTH_VERY_STRONG, STRENGTH_WEAK,
)


class PasswordStrengthChecker:
    """Scores length, character variety and common patterns."""

    COMMON_PASSWORDS = {
        "password", "123456", "12345678", "qwerty", "abc123",
        "monkey", "1234567", "letmein", "trustno1", "dragon",
        "baseball", "iloveyou", "master", "sunshine", "ashley",
        "bailey", "passw0rd", "shadow", "123123", "654321",
    }

    REPEATED_CHARS = re.compile(r"(.)\1{2,}")
    SEQUENTIAL_DIGITS = re.compile(r"(012|123|234|345|456|567|678|789|890)")
    SEQUENTIAL_LETTERS = re.compile(
        r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)"
    )

    @staticmethod
    def check_strength(password):
        """Return (level, label, feedback) for a password."""
        if not password:
            return STRENGTH_WEAK, "Very Weak", ["Password is empty"]

        length = len(password)
        feedback = []
        score = 0

        if length < MIN_LENGTH_WEAK:
            feedback.append(f"Too short (minimum {MIN_LENGTH_WEAK} characters)")
        elif length >= MIN_LENGTH_VERY_STRONG:
            score += 2
        elif length >= MIN_LENGTH_STRONG:
            score += 1.5
        elif length >= MIN_LENGTH_GOOD:
            score += 1
        elif length >= MIN_LENGTH_FAIR:
            score += 0.5

        if password.lower() in PasswordStrengthChecker.COMMON_PASSWORDS:
            feedback.append("This is a commonly used password")
            score -= 2

        has_lowercase = any(c.islower() for c in password)
        has_uppercase = any(c.isupper() for c in password)
        has_digits = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        variety_count = sum((has_lowercase, has_uppercase, has_digits, has_special))

        if variety_count == 4:
            score += 2
        elif variety_count == 3:
            score += 1.5
        elif variety_count == 2:
            score += 1
        elif variety_count == 1:
            score += 0.5
            feedback.append("Use a mix of character types")

        if not has_lowercase:
            feedback.append("Add lowercase letters")
        if not has_uppercase:
            feedback.append("Add uppercase letters")
        if not has_digits:
            feedback.append("Add numbers")
        if not has_special:
            feedback.append("Add special characters")

        checker = PasswordStrengthChecker
        if checker.REPEATED_CHARS.search(password):
            feedback.append("Avoid repeating characters")
            score -= 0.5
        if checker.SEQUENTIAL_DIGITS.search(password):
            feedback.append("Avoid sequential numbers")
            score -= 0.5
        if checker.SEQUENTIAL_LETTERS.search(password.lower()):
            feedback.append("Avoid sequential letters")
            score -= 0.5

        if score >= 4:
            level, label = STRENGTH_VERY_STRONG, "Very Strong"
        elif score >= 3:
            level, label = STRENGTH_STRONG, "Strong"
        elif score >= 2:
            level, label = STRENGTH_GOOD, "Good"
        elif score >= 1:
            level, label = STRENGTH_FAIR, "Fair"
        else:
            level, label = STRENGTH_WEAK, "Weak"

        if not feedback:
            feedback.append("Excellent password!")
        return level, label, feedback
