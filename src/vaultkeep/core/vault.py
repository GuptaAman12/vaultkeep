"""Encrypted vault storage and entry management."""

import json
import os

from .backup import BackupManager
from .crypto import CryptoManager
from ..constants import DATA_FILE, SALT_FILE
from ..logging_config import logger


class PasswordManager:
    """Stores password entries in a single encrypted file."""

    def __init__(self, data_file=DATA_FILE, salt_file=SALT_FILE):
        self.data_file = data_file
        self.crypto = CryptoManager(salt_file)
        self.backup_manager = BackupManager()
        self.passwords = {}
        logger.info("PasswordManager initialized")

    def initialize(self, master_password):
        """Unlock the vault, returning False if the password is wrong."""
        self.crypto.initialize(master_password)

        if not os.path.exists(self.data_file):
            self.passwords = {}
            return self.save()

        try:
            with open(self.data_file, "rb") as f:
                decrypted = self.crypto.decrypt(f.read())
            if decrypted is None:
                logger.error("Failed to decrypt password file - incorrect master password")
                return False
            self.passwords = json.loads(decrypted.decode())
            logger.info(f"Loaded {len(self.passwords)} passwords from encrypted file")
            return True
        except Exception as e:
            logger.error(f"Error loading passwords: {e}")
            return False

    def save(self):
        """Encrypt and write the vault, replacing the old file atomically."""
        temp_file = self.data_file + ".tmp"
        try:
            encrypted = self.crypto.encrypt(json.dumps(self.passwords).encode())
            if encrypted is None:
                return False

            with open(temp_file, "wb") as f:
                f.write(encrypted)
            os.replace(temp_file, self.data_file)
            logger.debug("Passwords saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving: {e}")
            return False
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def add_password(self, service, username, password, notes=""):
        """Add or update an entry."""
        self.passwords[service] = {
            "username": username,
            "password": password,
            "notes": notes,
        }
        logger.info(f"Added/updated password for service: {service}")
        return self.save()

    def get_password(self, service):
        """Return an entry, or None if the service is not in the vault."""
        return self.passwords.get(service)

    def delete_password(self, service):
        """Delete an entry."""
        if service in self.passwords:
            del self.passwords[service]
            logger.info(f"Deleted password for service: {service}")
            return self.save()
        return False

    def search(self, query):
        """Return service names containing the query, case-insensitively."""
        query = query.lower()
        return [s for s in self.passwords if query in s.lower()]

    def get_all_services(self):
        """Return all service names, sorted."""
        return sorted(self.passwords)

    def export_to_file(self, filepath):
        """Write a JSON backup."""
        return self.backup_manager.export_passwords(self.passwords, filepath)

    def import_from_file(self, filepath, merge_strategy="skip"):
        """Import a JSON backup, returning the number of entries or -1 on failure."""
        imported = self.backup_manager.import_passwords(filepath)
        if imported is None:
            return -1

        original_count = len(self.passwords)
        self.passwords = self.backup_manager.merge_passwords(
            self.passwords, imported, merge_strategy
        )
        if not self.save():
            return -1

        added = len(self.passwords) - original_count
        logger.info(f"Imported {len(imported)} passwords, added {added} new entries")
        return len(imported)
