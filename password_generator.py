"""
Password generation utility.
Provides secure random password generation with customizable options.
"""

import secrets
import string


class PasswordGenerator:
    """Generates secure random passwords."""
    
    @staticmethod
    def generate(length=16, use_uppercase=True, use_lowercase=True, 
                 use_digits=True, use_special=True):
        """
        Generate a secure random password.
        
        Args:
            length: Password length (default: 16)
            use_uppercase: Include uppercase letters A-Z
            use_lowercase: Include lowercase letters a-z
            use_digits: Include digits 0-9
            use_special: Include special characters
            
        Returns:
            Generated password string or None if no character types selected
        """
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
        
        password = ''.join(secrets.choice(chars) for _ in range(length))
        return password
