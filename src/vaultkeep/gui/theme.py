"""Shared light theme and small UI helpers for the Tkinter interface."""

import tkinter as tk
from tkinter import ttk

from ..constants import THEME

BG = "#f5f7fb"
SURFACE = "#ffffff"
SURFACE_ALT = "#eef2f9"
TEXT = "#17233c"
MUTED = "#64748b"
BORDER = "#dbe3ef"
ACCENT = "#3b6ef6"
ACCENT_HOVER = "#2f5ad6"
ACCENT_SOFT = "#e8efff"
DANGER = "#dc2626"
SUCCESS = "#16a34a"
SELECTION = "#dbe7ff"

FONT_BODY = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_SMALL_BOLD = ("Segoe UI", 9, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_BRAND = ("Segoe UI", 16, "bold")
FONT_TITLE = ("Segoe UI", 21, "bold")
FONT_MONO = ("Consolas", 11)


def apply_theme(root, configure_style=True):
    """Configure ttk styles and the background of a window."""
    root.configure(bg=BG)
    if not configure_style:
        return
    style = ttk.Style()
    style.theme_use(THEME)

    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT, font=FONT_BODY)
    style.configure("Card.TLabel", background=SURFACE, foreground=TEXT, font=FONT_BODY)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=FONT_SMALL)
    style.configure("CardMuted.TLabel", background=SURFACE, foreground=MUTED, font=FONT_SMALL)
    style.configure("Field.TLabel", background=SURFACE, foreground=TEXT, font=FONT_LABEL)
    style.configure("Value.TLabel", background=SURFACE, foreground=TEXT, font=FONT_BODY)
    style.configure("Mono.TLabel", background=SURFACE, foreground=TEXT, font=FONT_MONO)
    style.configure("Brand.TLabel", background=BG, foreground=TEXT, font=FONT_BRAND)
    style.configure("Title.TLabel", background=SURFACE, foreground=TEXT, font=FONT_TITLE)
    style.configure("Error.TLabel", background=SURFACE, foreground=DANGER, font=FONT_SMALL)

    style.configure("TButton", background=SURFACE, foreground=TEXT, font=FONT_BODY,
                    padding=(12, 7), borderwidth=1, relief="flat")
    style.map("TButton", background=[("active", SURFACE_ALT), ("pressed", BORDER)])
    style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff",
                    font=FONT_LABEL, padding=(14, 9), borderwidth=0, relief="flat")
    style.map("Accent.TButton", background=[("active", ACCENT_HOVER), ("pressed", ACCENT_HOVER)])
    style.configure("Danger.TButton", background=DANGER, foreground="#ffffff",
                    font=FONT_BODY, padding=(10, 6), borderwidth=0, relief="flat")
    style.map("Danger.TButton", background=[("active", "#b91c1c")])

    style.configure("TEntry", fieldbackground=SURFACE, foreground=TEXT,
                    insertcolor=TEXT, bordercolor=BORDER, lightcolor=BORDER,
                    darkcolor=BORDER, padding=7)
    style.map("TEntry", bordercolor=[("focus", ACCENT)])

    style.configure("TCheckbutton", background=BG, foreground=TEXT, font=FONT_BODY)
    style.configure("Card.TCheckbutton", background=SURFACE, foreground=TEXT, font=FONT_BODY)
    style.configure("TRadiobutton", background=SURFACE, foreground=TEXT, font=FONT_BODY)

    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE,
                    foreground=TEXT, font=FONT_BODY, rowheight=32, borderwidth=0)
    style.map("Treeview", background=[("selected", SELECTION)],
              foreground=[("selected", TEXT)])
    style.configure("Treeview.Heading", background=SURFACE_ALT, foreground=MUTED,
                    font=FONT_SMALL_BOLD, relief="flat", padding=(10, 9))
    style.configure("Vertical.TScrollbar", background=SURFACE_ALT,
                    troughcolor=SURFACE, bordercolor=SURFACE,
                    arrowcolor=MUTED, darkcolor=BORDER, lightcolor=BORDER)


def card(parent, **kwargs):
    """Return a white panel with a thin border."""
    return tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER,
                    highlightthickness=1, bd=0, **kwargs)


def menu(widget):
    """Return a menu styled to match the app."""
    return tk.Menu(widget, tearoff=0, bg=SURFACE, fg=TEXT,
                   activebackground=ACCENT_SOFT, activeforeground=TEXT,
                   bd=0, relief="flat")
