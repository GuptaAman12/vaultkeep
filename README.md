# Vaultkeep

A local, encrypted password vault with a desktop GUI. Entries are stored in one encrypted file on your machine. The master password is never stored.

[![Download Vaultkeep.exe](https://img.shields.io/badge/Download-Vaultkeep.exe-2ea44f?style=for-the-badge)](https://github.com/GuptaAman12/vaultkeep/releases/latest/download/Vaultkeep.exe)

## Features

- Master password protection with PBKDF2 key derivation
- Change the master password at any time, with a reminder every two months
- Fernet (AES-128) encryption for the whole vault
- Login errors that distinguish a wrong password from a missing salt or damaged vault
- Add, view, edit, delete and search entries
- Real-time password strength meter
- Secure password generator with adjustable length and character types
- JSON export and import with conflict strategies
- Audit logging for vault operations
- Auto-locks after 5 minutes of inactivity and clears the search box
- Clipboard clears itself 30 seconds after a copy, or immediately on lock
- Atomic file writes to avoid a half-written vault after a crash

## Quick start

On Windows, download the exe above and run it. No Python or install step is needed.

To run from source, use Python 3.8 or newer and install the package:

```bash
python -m pip install --user .
vaultkeep
```

`python -m vaultkeep` also works after installing. On Windows, add `%APPDATA%\Python\Python<version>\Scripts` to your PATH if the `vaultkeep` command is not found.

Without installing, run `python main.py` from this folder, or install the single dependency with `pip install -r requirements.txt`.

Vault files are resolved from the project folder, so a shortcut with a different working directory still opens the same vault.

On first launch, enter a new master password to create the vault. On later launches, enter the same password to unlock it. There is no reset or recovery path, so keep it memorable.

## Using the app

| Action | How |
| --- | --- |
| Add an entry | Click "+ Add Password" |
| View an entry | Double-click it, or right-click and choose View |
| Edit or delete | Right-click an entry |
| Copy credentials | Use the Copy buttons in the view dialog or the context menu |
| Search | Type in the Search box, filtering happens as you type |
| Generate a password | Click "Generate Password" |
| Back up | File > Export Passwords |
| Restore | File > Import Passwords |
| Lock the vault | Click Lock in the header or File > Lock Vault |
| Change the master password | File > Change Master Password |

After 60 days, login asks whether to change the master password. Choosing no or cancel snoozes the reminder for 7 days.

Import conflicts can be handled in three ways:

- **Skip**: keep the existing entry
- **Overwrite**: replace it with the imported one
- **Rename**: add the imported entry under a name like `Gmail (1)`

## Files

Vaultkeep creates these beside `Vaultkeep.exe`, or in the project folder when run from source:

| File | Purpose |
| --- | --- |
| `passwords.enc` | Encrypted vault |
| `salt.key` | Random salt used for key derivation |
| `password_manager.log` | Audit and debug log |

Back up `passwords.enc` and `salt.key` together. Without either the salt or the master password, the vault cannot be opened. Exported JSON backups are plain text, so store them somewhere secure.

## Security details

- Key derivation: PBKDF2-HMAC-SHA256, 100,000 iterations, 16-byte random salt, 32-byte key
- Encryption: Fernet with AES-128 and HMAC authentication
- Password generation: Python `secrets` module
- Nothing is decrypted or written to disk until you unlock the vault and make a change

These settings live in `src/vaultkeep/constants.py`.

## Project structure

```
main.py                       entry point
src/vaultkeep/
  assets/vaultkeep.png        app icon
  __init__.py                 application startup
  constants.py                configuration
  logging_config.py           logger setup
  core/
    vault.py                  entry storage and logic
    crypto.py                 encryption and key derivation
    backup.py                 JSON export and import
  security/
    generator.py              password generation
    strength.py               strength scoring
  gui/
    main_window.py            login screen and vault list
    dialogs.py                add, view, edit and generator dialogs
tests/test_vaultkeep.py       self-checks
```

The app icon is from Paomedia's small-n-flat set and is released under CC0.

## Tests

```bash
python -m unittest discover -s tests
```

The tests use temporary files and do not open the GUI. They check vault round trips, wrong-password handling, search, backup merging, generation and strength scoring.

## Windows executable

`Vaultkeep.exe` is a one-file PyInstaller build in the project root. It keeps `passwords.enc`, `salt.key` and the log beside itself.

To rebuild it from source:

```bash
pip install pyinstaller cryptography
python -m PyInstaller --onefile --windowed --name Vaultkeep --paths src --add-data "src\vaultkeep\assets\vaultkeep.png;vaultkeep\assets" main.py
```

## License

MIT. See `LICENSE` for details.
