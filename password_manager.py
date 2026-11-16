"""
Core password management functionality.
Handles storage, retrieval, and management of password entries.
"""

import json
import os
from crypto_manager import CryptoManager
from backup_manager import BackupManager
from constants import DATA_FILE, SALT_FILE
from logger import logger


class PasswordManager:
    """Manages password storage and retrieval with encryption."""
    
    def __init__(self, data_file=DATA_FILE, salt_file=SALT_FILE):
        """
        Initialize password manager.
        
        Args:
            data_file: Path to encrypted password storage file
            salt_file: Path to salt file for encryption
        """
        self.data_file = data_file
        self.crypto = CryptoManager(salt_file)
        self.backup_manager = BackupManager()
        self.master_password = None
        self.passwords = {}
        logger.info("PasswordManager initialized")
        
    def initialize(self, master_password):
        """
        Initialize with master password and load existing passwords.
        
        Args:
            master_password: Master password string
            
        Returns:
            True if successful, False if master password is incorrect
        """
        self.master_password = master_password
        
        # Initialize encryption
        self.crypto.initialize(master_password)
        
        # Load existing passwords
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.crypto.decrypt(encrypted_data)
                if decrypted_data is None:
                    logger.error("Failed to decrypt password file - incorrect master password")
                    return False
                self.passwords = json.loads(decrypted_data.decode())
                logger.info(f"Loaded {len(self.passwords)} passwords from encrypted file")
                return True
            except Exception as e:
                logger.error(f"Error loading passwords: {e}")
                return False
        else:
            # First time - create empty password store
            self.passwords = {}
            self.save()
            logger.info("Created new password vault")
            return True
    
    def save(self):
        """
        Save passwords to encrypted file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = json.dumps(self.passwords).encode()
            encrypted_data = self.crypto.encrypt(data)
            if encrypted_data is None:
                return False
            
            with open(self.data_file, 'wb') as f:
                f.write(encrypted_data)
            logger.debug("Passwords saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving: {e}")
            return False
    
    def add_password(self, service, username, password, notes=""):
        """
        Add or update a password entry.
        
        Args:
            service: Service/website name
            username: Username or email
            password: Password
            notes: Optional notes
            
        Returns:
            True if successful, False otherwise
        """
        self.passwords[service] = {
            'username': username,
            'password': password,
            'notes': notes
        }
        logger.info(f"Added/updated password for service: {service}")
        return self.save()
    
    def get_password(self, service):
        """
        Retrieve a password entry.
        
        Args:
            service: Service/website name
            
        Returns:
            Dictionary with username, password, and notes, or None if not found
        """
        return self.passwords.get(service)
    
    def delete_password(self, service):
        """
        Delete a password entry.
        
        Args:
            service: Service/website name
            
        Returns:
            True if successful, False if service not found
        """
        if service in self.passwords:
            del self.passwords[service]
            logger.info(f"Deleted password for service: {service}")
            return self.save()
        return False
    
    def search(self, query):
        """
        Search for services containing query.
        
        Args:
            query: Search string
            
        Returns:
            List of matching service names
        """
        query = query.lower()
        return [s for s in self.passwords.keys() if query in s.lower()]
    
    def get_all_services(self):
        """
        Get list of all services.
        
        Returns:
            Sorted list of service names
        """
        return sorted(self.passwords.keys())
    
    def export_to_file(self, filepath):
        """
        Export passwords to backup file.
        
        Args:
            filepath: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        return self.backup_manager.export_passwords(self.passwords, filepath)
    
    def import_from_file(self, filepath, merge_strategy='skip'):
        """
        Import passwords from backup file.
        
        Args:
            filepath: Path to import file
            merge_strategy: How to handle conflicts ('skip', 'overwrite', 'rename')
            
        Returns:
            Number of passwords imported, or -1 if failed
        """
        imported = self.backup_manager.import_passwords(filepath)
        if imported is None:
            return -1
        
        original_count = len(self.passwords)
        self.passwords = self.backup_manager.merge_passwords(
            self.passwords, imported, merge_strategy
        )
        new_count = len(self.passwords)
        
        if self.save():
            imported_count = new_count - original_count
            logger.info(f"Imported {len(imported)} passwords, added {imported_count} new entries")
            return len(imported)
        return -1
