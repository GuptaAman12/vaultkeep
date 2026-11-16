"""Encryption and key derivation for the vault."""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..constants import KEY_LENGTH, PBKDF2_ITERATIONS, SALT_LENGTH
from ..logging_config import logger


class CryptoManager:
    """Derives a key from the master password and encrypts vault data."""

    def __init__(self, salt_file):
        self.salt_file = salt_file
        self.cipher = None

    def derive_key(self, password, salt):
        """Derive a base64 Fernet key from a master password and salt."""
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
        """Load or create the salt and set up the cipher."""
        if os.path.exists(self.salt_file):
            with open(self.salt_file, "rb") as f:
                salt = f.read()
            logger.info("Loaded existing salt file")
        else:
            salt = os.urandom(SALT_LENGTH)
            with open(self.salt_file, "wb") as f:
                f.write(salt)
            logger.info("Created new salt file")

        self.cipher = Fernet(self.derive_key(master_password, salt))
        return True

    def encrypt(self, data):
        """Encrypt bytes, returning None on error."""
        if self.cipher is None:
            return None
        try:
            return self.cipher.encrypt(data)
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None

    def decrypt(self, encrypted_data):
        """Decrypt bytes, returning None on a bad key or corrupt data."""
        if self.cipher is None:
            return None
        try:
            return self.cipher.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
