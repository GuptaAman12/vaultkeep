"""
Secure Password Manager with GUI
Entry point for the application.

Features:
- Master password protection
- AES encryption for stored passwords
- Add, view, edit, and delete passwords
- Search functionality
- Password generator
- Copy to clipboard
"""

import tkinter as tk
from main_window import PasswordManagerGUI


def main():
    """Main entry point for the password manager application."""
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
