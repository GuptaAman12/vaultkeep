"""Vaultkeep - a local, encrypted password vault."""

import tkinter as tk

from .gui.main_window import PasswordManagerGUI


def main():
    """Start the desktop application."""
    root = tk.Tk()
    PasswordManagerGUI(root)
    root.mainloop()
