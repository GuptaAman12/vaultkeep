# Password Manager - User Guide

## Quick Start

### Running the Application

1. **Open a terminal/command prompt** in the Password Manager directory:
   ```bash
   cd "c:\Users\gupta\Desktop\Grind\Python\Password Manager"
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **First Time Setup**:
   - Enter a **master password** (this will create your vault)
   - Remember this password - you'll need it every time!
   - Your master password is NOT stored anywhere

4. **Subsequent Logins**:
   - Enter your master password to unlock your vault

## Features

### 1. Adding Passwords
- Click **"+ Add Password"** button
- Fill in:
  - Service/Website name (e.g., "Gmail", "Facebook")
  - Username or Email
  - Password (with real-time strength indicator)
  - Notes (optional)
- **NEW**: Password strength shown as you type (Weak/Fair/Good/Strong/Very Strong)
- Click **Save**

### 2. Viewing Passwords
- **Double-click** any entry in the list, OR
- **Right-click** → Select "View"
- Click **"Show"** checkbox to reveal the password
- Use **"Copy"** buttons to copy username or password to clipboard

### 3. Editing Passwords
- **Right-click** on an entry → Select "Edit"
- Update the information
- Click **Save**

### 4. Deleting Passwords
- **Right-click** on an entry → Select "Delete"
- Confirm deletion

### 5. Searching
- Type in the **Search** box at the top
- Results filter automatically as you type

### 6. Generating Secure Passwords
- Click **"Generate Password"** button
- Customize:
  - Length (8-64 characters)
  - Character types (uppercase, lowercase, digits, special)
- Click **"Generate"** to create a new password
- Click **"Copy"** to copy to clipboard

### 7. Exporting Passwords (Backup)
- Click **File → Export Passwords...** in menu bar
- Choose save location
- Backup saved as JSON file with timestamp
- Use for data backup or migration

### 8. Importing Passwords (Restore)
- Click **File → Import Passwords...** in menu bar
- Select backup JSON file
- Choose merge strategy:
  - **Skip**: Keep existing passwords (recommended)
  - **Overwrite**: Replace with imported passwords
  - **Rename**: Import as new entries with suffix
- Click Import to restore

## Security Features

✅ **AES-128 Encryption** - All passwords encrypted with Fernet  
✅ **PBKDF2 Key Derivation** - 100,000 iterations for master password  
✅ **No Plain Text Storage** - Everything is encrypted on disk  
✅ **Secure Random Generation** - Uses Python's `secrets` module  
✅ **Password Strength Checker** - Real-time feedback on password quality  
✅ **Audit Logging** - All operations logged for security review  

## Files Created

When you first run the application, it creates:
- `passwords.enc` - Your encrypted password database
- `salt.key` - Salt for key derivation
- `password_manager.log` - Application logs and audit trail

**⚠️ IMPORTANT**: 
- Keep these files safe - they contain your encrypted passwords
- Back them up regularly
- If you lose `salt.key`, you won't be able to decrypt your passwords
- If you forget your master password, there's NO way to recover it

## Keyboard Shortcuts

- **Enter** on login screen → Login
- **Double-click** entry → View password
- **Right-click** entry → Context menu

## Tips

1. **Choose a Strong Master Password**: 
   - At least 12 characters
   - Mix of letters, numbers, and symbols
   - Don't use common words

2. **Regular Backups**:
   - Copy `passwords.enc` and `salt.key` to a secure location
   - Consider cloud storage (encrypted) or external drive

3. **Use the Password Generator**:
   - Generate unique passwords for each service
   - Use maximum length when possible
   - Include all character types

## Troubleshooting

### "Invalid master password" error
- Make sure you're entering the correct master password
- Passwords are case-sensitive
- If you've forgotten it, there's no recovery option

### Application won't start
- Ensure Python 3.7+ is installed
- Install required packages:
  ```bash
  pip install cryptography
  ```

### Lost passwords
- If you have backups of `passwords.enc` and `salt.key`, restore them
- Without backups and the correct master password, data cannot be recovered

## Requirements

- **Python**: 3.7 or higher
- **Dependencies**:
  - `cryptography` library
  - `tkinter` (usually included with Python)

### Installing Dependencies
```bash
pip install cryptography
```

## Project Structure

```
Password Manager/
├── main.py                  # Entry point
├── constants.py             # Configuration constants
├── logger.py               # Logging setup
├── crypto_manager.py        # Encryption utilities
├── password_generator.py    # Password generation
├── password_manager.py      # Core business logic
├── password_strength.py     # Password strength checker
├── backup_manager.py        # Export/import functionality
├── gui_components.py        # Dialog components
├── main_window.py          # Main application window
├── README.md               # This file
├── passwords.enc           # Your encrypted passwords (created on first run)
├── salt.key               # Encryption salt (created on first run)
└── password_manager.log    # Application logs (created on first run)
```

## What's New in v2.0

### Password Strength Checker
- Real-time strength indicator in Add/Edit dialogs
- Color-coded feedback (Red/Orange/Yellow/Light Green/Dark Green)
- Evaluates length, character variety, and common patterns

### Export/Import Functionality
- Backup passwords to JSON file
- Restore from backup with merge strategies
- Timestamped backup filenames

### Menu Bar
- File menu with Export/Import options
- Help menu with About dialog

### Logging System
- All operations logged to `password_manager.log`
- Audit trail for security review
- Debug information for troubleshooting

### Constants Module
- Centralized configuration
- Easy to customize settings
- No magic numbers in code

## Support

For issues or questions, check:
1. This README
2. The walkthrough.md in the artifacts directory
3. Code comments in each module

---

**Remember**: Your master password is the key to everything. Keep it safe and memorable! 🔐
