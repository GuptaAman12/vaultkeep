"""Vaultkeep - a local, encrypted password vault."""

import ctypes
import tkinter as tk

from .gui.main_window import PasswordManagerGUI


def _enable_dpi_awareness():
    """Use real pixels so dialogs fit on scaled Windows displays."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass


def main():
    """Start the desktop application."""
    _enable_dpi_awareness()
    root = tk.Tk()
    PasswordManagerGUI(root)
    root.mainloop()
