"""Encrypted vault storage and entry management."""

import json
import os
from datetime import datetime, timedelta

from .backup import BackupManager
from .crypto import CryptoManager
from ..constants import (
    DATA_FILE, PASSWORD_CHANGE_INTERVAL_DAYS, PASSWORD_REMINDER_SNOOZE_DAYS, SALT_FILE,
)
from ..logging_config import logger

META_KEY = "__meta__"


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
        else:
            try:
                with open(self.data_file, "rb") as f:
                    decrypted = self.crypto.decrypt(f.read())
                if decrypted is None:
                    logger.error("Failed to decrypt password file - incorrect master password")
                    return False
                self.passwords = json.loads(decrypted.decode())
            except Exception as e:
                logger.error(f"Error loading passwords: {e}")
                return False

        meta = self.get_meta()
        if not meta.get("password_changed_at"):
            meta["password_changed_at"] = datetime.now().isoformat()
            self.passwords[META_KEY] = meta
            if not self.save():
                return False
        logger.info(f"Loaded {len(self.get_all_services())} passwords from encrypted file")
        return True

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

    def get_meta(self):
        """Return the encrypted vault metadata."""
        meta = self.passwords.get(META_KEY)
        return meta if isinstance(meta, dict) else {}

    def _entry_keys(self):
        return [key for key, value in self.passwords.items()
                if key != META_KEY and isinstance(value, dict)]

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
        return [s for s in self._entry_keys() if query in s.lower()]

    def get_all_services(self):
        """Return all service names, sorted."""
        return sorted(self._entry_keys())

    def verify_master_password(self, password):
        """Check a master password without changing the active cipher."""
        if not os.path.exists(self.crypto.salt_file) or not os.path.exists(self.data_file):
            return False
        try:
            with open(self.data_file, "rb") as f:
                encrypted = f.read()
            checker = CryptoManager(self.crypto.salt_file)
            checker.initialize(password)
            return checker.decrypt(encrypted) is not None
        except Exception as e:
            logger.error(f"Master password check failed: {e}")
            return False

    def change_master_password(self, current_password, new_password):
        """Re-encrypt the vault with a new master password."""
        if not self.verify_master_password(current_password):
            return False

        previous_meta = dict(self.get_meta())
        meta = dict(previous_meta)
        meta["password_changed_at"] = datetime.now().isoformat()
        meta.pop("reminder_snoozed_until", None)
        self.passwords[META_KEY] = meta

        self.crypto.initialize(new_password)
        if self.save():
            logger.info("Master password changed")
            return True

        self.passwords[META_KEY] = previous_meta
        self.crypto.initialize(current_password)
        return False

    def password_change_due(self):
        """Return True when the password is older than the reminder interval."""
        meta = self.get_meta()
        snoozed = meta.get("reminder_snoozed_until")
        if snoozed:
            try:
                if datetime.fromisoformat(snoozed) > datetime.now():
                    return False
            except ValueError:
                pass
        changed = meta.get("password_changed_at")
        if not changed:
            return False
        try:
            age = datetime.now() - datetime.fromisoformat(changed)
        except ValueError:
            return False
        return age >= timedelta(days=PASSWORD_CHANGE_INTERVAL_DAYS)

    def snooze_password_reminder(self):
        """Hide the password reminder for a short period."""
        meta = self.get_meta()
        meta["reminder_snoozed_until"] = (
            datetime.now() + timedelta(days=PASSWORD_REMINDER_SNOOZE_DAYS)
        ).isoformat()
        self.passwords[META_KEY] = meta
        return self.save()

    def export_to_file(self, filepath):
        """Write a JSON backup without vault metadata."""
        entries = {key: self.passwords[key] for key in self._entry_keys()}
        return self.backup_manager.export_passwords(entries, filepath)

    def import_from_file(self, filepath, merge_strategy="skip"):
        """Import a JSON backup, returning the number of entries or -1 on failure."""
        imported = self.backup_manager.import_passwords(filepath)
        if imported is None:
            return -1
        imported = {key: value for key, value in imported.items()
                    if key != META_KEY and isinstance(value, dict)}

        original_count = len(self._entry_keys())
        self.passwords = self.backup_manager.merge_passwords(
            self.passwords, imported, merge_strategy
        )
        if not self.save():
            return -1

        added = len(self._entry_keys()) - original_count
        logger.info(f"Imported {len(imported)} passwords, added {added} new entries")
        return len(imported)
