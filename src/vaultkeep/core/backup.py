"""JSON backup and restore for password entries."""

import json
import os
from datetime import datetime

from ..logging_config import logger


class BackupManager:
    """Exports, imports and merges password backups."""

    @staticmethod
    def export_passwords(passwords, filepath):
        """Write a timestamped backup to a JSON file."""
        try:
            export_data = {
                "export_date": datetime.now().isoformat(),
                "version": "1.0",
                "passwords": passwords,
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Exported {len(passwords)} passwords to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

    @staticmethod
    def import_passwords(filepath):
        """Read a JSON backup, returning its entries or None on failure."""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Import file not found: {filepath}")
                return None

            with open(filepath, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            passwords = import_data.get("passwords")
            if not isinstance(passwords, dict):
                logger.error("Invalid backup file format")
                return None

            logger.info(f"Imported {len(passwords)} passwords from {filepath}")
            return passwords
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in import file: {e}")
            return None
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return None

    @staticmethod
    def merge_passwords(existing, imported, strategy="skip"):
        """Merge imports using skip, overwrite or rename for name conflicts."""
        merged = existing.copy()
        conflicts = []

        for service, data in imported.items():
            if service in merged:
                conflicts.append(service)
                if strategy == "overwrite":
                    merged[service] = data
                elif strategy == "rename":
                    suffix = 1
                    new_service = f"{service} ({suffix})"
                    while new_service in merged:
                        suffix += 1
                        new_service = f"{service} ({suffix})"
                    merged[new_service] = data
            else:
                merged[service] = data

        if conflicts:
            logger.info(f"Found {len(conflicts)} conflicts during merge")

        return merged
