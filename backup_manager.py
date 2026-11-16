"""
Backup and restore functionality for password data.
Handles export/import of password data in JSON format.
"""

import json
import os
from datetime import datetime
from logger import logger


class BackupManager:
    """Manages backup and restore operations."""
    
    @staticmethod
    def export_passwords(passwords, filepath):
        """
        Export passwords to JSON file.
        
        Args:
            passwords: Dictionary of password entries
            filepath: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'version': '1.0',
                'passwords': passwords
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(passwords)} passwords to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    @staticmethod
    def import_passwords(filepath):
        """
        Import passwords from JSON file.
        
        Args:
            filepath: Path to import file
            
        Returns:
            Dictionary of password entries, or None if failed
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"Import file not found: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Validate structure
            if 'passwords' not in import_data:
                logger.error("Invalid backup file format")
                return None
            
            passwords = import_data['passwords']
            logger.info(f"Imported {len(passwords)} passwords from {filepath}")
            
            return passwords
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in import file: {e}")
            return None
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return None
    
    @staticmethod
    def merge_passwords(existing, imported, strategy='skip'):
        """
        Merge imported passwords with existing ones.
        
        Args:
            existing: Existing password dictionary
            imported: Imported password dictionary
            strategy: 'skip' (keep existing), 'overwrite' (replace), or 'rename' (add suffix)
            
        Returns:
            Merged password dictionary
        """
        merged = existing.copy()
        conflicts = []
        
        for service, data in imported.items():
            if service in merged:
                conflicts.append(service)
                
                if strategy == 'overwrite':
                    merged[service] = data
                elif strategy == 'rename':
                    # Add timestamp suffix to avoid conflicts
                    suffix = 1
                    new_service = f"{service} ({suffix})"
                    while new_service in merged:
                        suffix += 1
                        new_service = f"{service} ({suffix})"
                    merged[new_service] = data
                # 'skip' strategy: do nothing, keep existing
            else:
                merged[service] = data
        
        if conflicts:
            logger.info(f"Found {len(conflicts)} conflicts during merge")
        
        return merged
