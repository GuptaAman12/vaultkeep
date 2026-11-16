"""Small self-checks for the restructured package (stdlib unittest)."""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaultkeep.core.backup import BackupManager
from vaultkeep.core.vault import META_KEY, PasswordManager
from vaultkeep.security.generator import PasswordGenerator
from vaultkeep.security.strength import PasswordStrengthChecker


class VaultTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data = os.path.join(self.temp.name, "passwords.enc")
        self.salt = os.path.join(self.temp.name, "salt.key")

    def test_round_trip_and_wrong_password(self):
        vault = PasswordManager(self.data, self.salt)
        self.assertTrue(vault.initialize("correct horse"))
        self.assertTrue(vault.add_password("Gmail", "me@example.com", "s3cret!"))
        self.assertFalse(os.path.exists(self.data + ".tmp"))

        reopened = PasswordManager(self.data, self.salt)
        self.assertTrue(reopened.initialize("correct horse"))
        self.assertEqual(reopened.get_password("Gmail")["username"], "me@example.com")

        locked = PasswordManager(self.data, self.salt)
        with self.assertLogs("PasswordManager", level="ERROR"):
            self.assertFalse(locked.initialize("wrong password"))

    def test_search_uses_shared_logic(self):
        vault = PasswordManager(self.data, self.salt)
        vault.initialize("master")
        vault.add_password("GitHub", "user", "pw")
        vault.add_password("GitLab", "user", "pw")
        self.assertEqual(vault.search("git"), ["GitHub", "GitLab"])
        self.assertEqual(vault.get_all_services(), ["GitHub", "GitLab"])

    def test_change_master_password(self):
        vault = PasswordManager(self.data, self.salt)
        vault.initialize("old master")
        vault.add_password("Gmail", "me@example.com", "s3cret!")

        with self.assertLogs("PasswordManager", level="ERROR"):
            self.assertFalse(vault.change_master_password("wrong", "new master"))
        self.assertTrue(vault.change_master_password("old master", "new master"))

        reopened = PasswordManager(self.data, self.salt)
        self.assertTrue(reopened.initialize("new master"))
        self.assertEqual(reopened.get_password("Gmail")["username"], "me@example.com")
        with self.assertLogs("PasswordManager", level="ERROR"):
            self.assertFalse(reopened.initialize("old master"))

    def test_password_reminder_and_snooze(self):
        vault = PasswordManager(self.data, self.salt)
        vault.initialize("master")
        self.assertFalse(vault.password_change_due())

        meta = vault.get_meta()
        meta["password_changed_at"] = (datetime.now() - timedelta(days=61)).isoformat()
        vault.passwords[META_KEY] = meta
        vault.save()
        self.assertTrue(vault.password_change_due())

        vault.snooze_password_reminder()
        self.assertFalse(vault.password_change_due())

    def test_backup_merge_strategies(self):
        existing = {"Site": {"username": "old", "password": "old"}}
        imported = {"Site": {"username": "new", "password": "new"}, "Other": {}}
        self.assertEqual(list(BackupManager.merge_passwords(existing, imported)), ["Site", "Other"])
        self.assertEqual(
            BackupManager.merge_passwords(existing, imported, "overwrite")["Site"]["username"],
            "new",
        )
        self.assertIn("Site (1)", BackupManager.merge_passwords(existing, imported, "rename"))


class SecurityTests(unittest.TestCase):
    def test_generator(self):
        self.assertEqual(len(PasswordGenerator.generate(24, False, False, True, False)), 24)
        self.assertTrue(PasswordGenerator.generate(20, False, False, True, False).isdigit())
        self.assertIsNone(PasswordGenerator.generate(16, False, False, False, False))

    def test_generator_includes_every_selected_type(self):
        for _ in range(25):
            password = PasswordGenerator.generate(12)
            self.assertEqual(len(password), 12)
            self.assertTrue(any(c.isupper() for c in password))
            self.assertTrue(any(c.islower() for c in password))
            self.assertTrue(any(c.isdigit() for c in password))
            self.assertTrue(any(not c.isalnum() for c in password))

    def test_strength(self):
        self.assertLess(
            PasswordStrengthChecker.check_strength("password")[0],
            PasswordStrengthChecker.check_strength("Xy7!qLp9#mVr2@tZ")[0],
        )


if __name__ == "__main__":
    unittest.main()
