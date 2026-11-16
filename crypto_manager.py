"""
Cryptographic utilities for password encryption and key derivation.
Handles all encryption/decryption operations using Fernet (AES).
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from constants import PBKDF2_ITERATIONS, KEY_LENGTH, SALT_LENGTH
from logger import logger


class CryptoManager:
    """Manages encryption keys and cryptographic operations."""
    
    def __init__(self, salt_file):
        """
        Initialize crypto manager.
        
        Args:
            salt_file: Path to file storing the salt for key derivation
        """
        self.salt_file = salt_file
        self.cipher = None
        
    def derive_key(self, password, salt):
        """
        Derive encryption key from master password using PBKDF2.
        
        Args:
            password: Master password string
            salt: Salt bytes for key derivation
            
        Returns:
            Base64-encoded encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_LENGTH,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        logger.debug("Derived encryption key from master password")
        return key
    
    def initialize(self, master_password):
        """
        Initialize cipher with master password.
        
        Args:
            master_password: Master password string
            
        Returns:
            True if initialization successful
        """
        # Load or create salt
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
            logger.info("Loaded existing salt file")
        else:
            salt = os.urandom(SALT_LENGTH)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            logger.info("Created new salt file")
        # Derive encryption key and create cipher
        key = self.derive_key(master_password, salt)
        self.cipher = Fernet(key)
        return True
    
    def encrypt(self, data):
        """
        Encrypt data.
        
        Args:
            data: Bytes to encrypt
            
        Returns:
            Encrypted bytes or None on error
        """
        if self.cipher is None:
            return None
        
        try:
            return self.cipher.encrypt(data)
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None
    
    def decrypt(self, encrypted_data):
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            Decrypted bytes or None on error
        """
        if self.cipher is None:
            return None
        
        try:
            return self.cipher.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
