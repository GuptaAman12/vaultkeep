"""
Password strength checker.
Evaluates password strength based on length, character variety, and common patterns.
"""

import re
from constants import (
    STRENGTH_WEAK, STRENGTH_FAIR, STRENGTH_GOOD, 
    STRENGTH_STRONG, STRENGTH_VERY_STRONG,
    MIN_LENGTH_WEAK, MIN_LENGTH_FAIR, MIN_LENGTH_GOOD,
    MIN_LENGTH_STRONG, MIN_LENGTH_VERY_STRONG
)


class PasswordStrengthChecker:
    """Evaluates password strength."""
    
    # Common weak passwords
    COMMON_PASSWORDS = {
        'password', '123456', '12345678', 'qwerty', 'abc123',
        'monkey', '1234567', 'letmein', 'trustno1', 'dragon',
        'baseball', 'iloveyou', 'master', 'sunshine', 'ashley',
        'bailey', 'passw0rd', 'shadow', '123123', '654321'
    }
    
    @staticmethod
    def check_strength(password):
        """
        Check password strength.
        
        Args:
            password: Password string to evaluate
            
        Returns:
            Tuple of (strength_level, strength_text, feedback_list)
            strength_level: 0-4 (WEAK to VERY_STRONG)
            strength_text: Human-readable strength description
            feedback_list: List of improvement suggestions
        """
        if not password:
            return STRENGTH_WEAK, "Very Weak", ["Password is empty"]
        
        length = len(password)
        feedback = []
        score = 0
        
        # Check length
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
        
        # Check for common passwords
        if password.lower() in PasswordStrengthChecker.COMMON_PASSWORDS:
            feedback.append("This is a commonly used password")
            score -= 2
        
        # Check character variety
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_digits = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>_\-=+\[\]\\;/]', password))
        
        variety_count = sum([has_lowercase, has_uppercase, has_digits, has_special])
        
        if variety_count == 4:
            score += 2
        elif variety_count == 3:
            score += 1.5
        elif variety_count == 2:
            score += 1
        elif variety_count == 1:
            score += 0.5
            feedback.append("Use a mix of character types")
        
        # Provide specific feedback
        if not has_lowercase:
            feedback.append("Add lowercase letters")
        if not has_uppercase:
            feedback.append("Add uppercase letters")
        if not has_digits:
            feedback.append("Add numbers")
        if not has_special:
            feedback.append("Add special characters")
        
        # Check for patterns
        if re.search(r'(.)\1{2,}', password):
            feedback.append("Avoid repeating characters")
            score -= 0.5
        
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            feedback.append("Avoid sequential numbers")
            score -= 0.5
        
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            feedback.append("Avoid sequential letters")
            score -= 0.5
        
        # Determine strength level
        if score >= 4:
            strength_level = STRENGTH_VERY_STRONG
            strength_text = "Very Strong"
        elif score >= 3:
            strength_level = STRENGTH_STRONG
            strength_text = "Strong"
        elif score >= 2:
            strength_level = STRENGTH_GOOD
            strength_text = "Good"
        elif score >= 1:
            strength_level = STRENGTH_FAIR
            strength_text = "Fair"
        else:
            strength_level = STRENGTH_WEAK
            strength_text = "Weak"
        
        # If no feedback, password is good
        if not feedback:
            feedback.append("Excellent password!")
        
        return strength_level, strength_text, feedback
    
    @staticmethod
    def get_strength_color(strength_level):
        """
        Get color for strength level.
        
        Args:
            strength_level: Strength level (0-4)
            
        Returns:
            Color string for GUI display
        """
        colors = {
            STRENGTH_WEAK: "#d32f2f",          # Red
            STRENGTH_FAIR: "#f57c00",          # Orange
            STRENGTH_GOOD: "#fbc02d",          # Yellow
            STRENGTH_STRONG: "#7cb342",        # Light Green
            STRENGTH_VERY_STRONG: "#388e3c"    # Dark Green
        }
        return colors.get(strength_level, "#757575")
