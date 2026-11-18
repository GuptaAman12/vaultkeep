"""Modal dialogs for adding, viewing, editing and generating passwords."""

import tkinter as tk
from tkinter import messagebox, ttk

from ..constants import (
    DEFAULT_PASSWORD_LENGTH, DIALOG_HEIGHT, DIALOG_WIDTH, GENERATOR_DIALOG_HEIGHT,
    GENERATOR_DIALOG_WIDTH, MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH,
)
from ..security.generator import PasswordGenerator
from ..security.strength import PasswordStrengthChecker
from .strength_meter import StrengthMeter
from .theme import BG, BORDER, SURFACE, TEXT, card, FONT_BODY, FONT_MONO


def _dialog(parent, title, width, height):
    """Create a themed modal dialog, sized to its content and centered."""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry(f"{width}x{height}")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.configure(bg=BG)
    dialog.after_idle(_fit_dialog, dialog, width, height)
    return dialog


def _fit_dialog(dialog, width, height):
    """Keep the whole dialog visible even with larger fonts or scaling."""
    dialog.update_idletasks()
    width = max(width, dialog.winfo_reqwidth())
    height = max(height, dialog.winfo_reqheight())
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    width = min(width, screen_width - 40)
    height = min(height, screen_height - 60)
    dialog.geometry(f"{width}x{height}+{(screen_width - width) // 2}+"
                    f"{(screen_height - height) // 2}")


def _panel(dialog):
    """Create a bordered content card with a padded inner frame."""
    panel = card(dialog)
    panel.pack(fill="both", expand=True, padx=16, pady=16)
    panel.grid_rowconfigure(0, weight=1)
    panel.grid_columnconfigure(0, weight=1)
    inner = tk.Frame(panel, bg=SURFACE)
    inner.grid(row=0, column=0, sticky="nsew", padx=24, pady=22)
    inner.grid_columnconfigure(0, weight=1)
    return inner


def _notes_widget(parent, text=""):
    notes = tk.Text(parent, width=40, height=4, font=FONT_BODY, wrap="word",
                    bg=SURFACE, fg=TEXT, highlightbackground=BORDER,
                    highlightthickness=1, relief="flat", padx=8, pady=6)
    if text:
        notes.insert("1.0", text)
    return notes


class _PasswordFormMixin:
    """Shared password visibility, strength and generation behavior."""

    def _toggle_password(self):
        self._password_visible = not self._password_visible
        self.password_entry.config(show="" if self._password_visible else "\u2022")
        self.show_button.config(text="Hide" if self._password_visible else "Show")

    def _add_password_field(self, inner, row, initial=""):
        ttk.Label(inner, text="Password", style="Field.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(14, 5))
        self.password_entry = ttk.Entry(
            inner, show="\u2022", width=36, font=FONT_BODY)
        self.password_entry.insert(0, initial)
        self.password_entry.grid(row=row + 1, column=0, sticky="ew", ipady=3)
        self._password_visible = False
        self.show_button = ttk.Button(
            inner, text="Show", width=8, command=self._toggle_password)
        self.show_button.grid(row=row + 1, column=1, padx=(8, 0))
        self.password_entry.bind("<KeyRelease>", self._check_strength)

    def _add_strength_ui(self, inner, row):
        ttk.Label(inner, text="Strength", style="Field.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(14, 5))
        self.strength_meter = StrengthMeter(inner)
        self.strength_meter.grid(row=row + 1, column=0, columnspan=2, sticky="ew")
        self.strength_feedback = ttk.Label(inner, text="", style="CardMuted.TLabel")
        self.strength_feedback.grid(row=row + 2, column=0, columnspan=2, sticky="w", pady=(4, 0))
        self._check_strength()

    def _check_strength(self, event=None):
        password = self.password_entry.get()
        if not password:
            self.strength_meter.set(0)
            self.strength_feedback.config(text="")
            return
        level, label, feedback = PasswordStrengthChecker.check_strength(password)
        self.strength_meter.set(level, label)
        self.strength_feedback.config(text=", ".join(feedback[:2]))

    def _generate_password(self):
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, PasswordGenerator.generate(DEFAULT_PASSWORD_LENGTH))
        self._check_strength()


class AddPasswordDialog(_PasswordFormMixin):
    """Dialog for adding a new entry."""

    def __init__(self, parent, manager, refresh_callback):
        self.manager = manager
        self.refresh_callback = refresh_callback
        self.dialog = _dialog(parent, "Add password", DIALOG_WIDTH + 40, DIALOG_HEIGHT + 280)
        inner = _panel(self.dialog)

        ttk.Label(inner, text="New password", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(inner, text="Save a credential to your encrypted vault.",
                  style="CardMuted.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 16))

        ttk.Label(inner, text="Service / website", style="Field.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.service_entry = ttk.Entry(inner, width=36, font=FONT_BODY)
        self.service_entry.grid(row=3, column=0, columnspan=2, sticky="ew", ipady=3)
        self.service_entry.focus()

        ttk.Label(inner, text="Username / email", style="Field.TLabel").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(14, 5))
        self.username_entry = ttk.Entry(inner, width=36, font=FONT_BODY)
        self.username_entry.grid(row=5, column=0, columnspan=2, sticky="ew", ipady=3)

        self._add_password_field(inner, 6)
        self._add_strength_ui(inner, 8)
        ttk.Button(inner, text="Suggest a strong password",
                   command=self._generate_password).grid(
            row=10, column=0, columnspan=2, sticky="w", pady=(8, 0))

        ttk.Label(inner, text="Notes", style="Field.TLabel").grid(
            row=11, column=0, columnspan=2, sticky="w", pady=(14, 5))
        self.notes_text = _notes_widget(inner)
        self.notes_text.grid(row=12, column=0, columnspan=2, sticky="ew")

        buttons = tk.Frame(inner, bg=SURFACE)
        buttons.grid(row=13, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(buttons, text="Cancel", command=self.dialog.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Save password", style="Accent.TButton",
                   command=self._save).pack(side="left")

    def _save(self):
        service = self.service_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        notes = self.notes_text.get("1.0", "end-1c").strip()

        if not service or not username or not password:
            messagebox.showerror("Missing details", "Service, username and password are required.",
                                 parent=self.dialog)
            return

        if self.manager.add_password(service, username, password, notes):
            messagebox.showinfo("Saved", "Password added to your vault.", parent=self.dialog)
            self.refresh_callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save password.", parent=self.dialog)


class ViewPasswordDialog:
    """Dialog for viewing a single entry."""

    def __init__(self, parent, service, data, copy_callback):
        self.data = data
        self.copy_callback = copy_callback
        self.dialog = _dialog(parent, service, DIALOG_WIDTH + 40, DIALOG_HEIGHT + 110)
        inner = _panel(self.dialog)

        ttk.Label(inner, text=service, style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(inner, text="Stored in your encrypted vault.",
                  style="CardMuted.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 20))

        ttk.Label(inner, text="Username / email", style="Field.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 8))
        ttk.Label(inner, text=self.data["username"], style="Value.TLabel",
                  wraplength=180).grid(row=2, column=1, sticky="ew")
        ttk.Button(inner, text="Copy", width=8,
                   command=lambda: self.copy_callback(self.data["username"])).grid(
            row=2, column=2, padx=(10, 0))

        ttk.Label(inner, text="Password", style="Field.TLabel").grid(
            row=3, column=0, sticky="w", pady=(18, 8))
        self.password_label = ttk.Label(inner, text="\u2022" * 12, style="Mono.TLabel")
        self.password_label.grid(row=3, column=1, sticky="w")
        self._visible = False
        self.show_button = ttk.Button(
            inner, text="Show", width=8, command=self._toggle_password)
        self.show_button.grid(row=3, column=2, padx=(4, 0))
        ttk.Button(inner, text="Copy", width=8,
                   command=lambda: self.copy_callback(self.data["password"])).grid(
            row=3, column=3, padx=(4, 0))

        row = 4
        if self.data.get("notes"):
            ttk.Label(inner, text="Notes", style="Field.TLabel").grid(
                row=4, column=0, columnspan=4, sticky="w", pady=(20, 6))
            notes = _notes_widget(inner, self.data["notes"])
            notes.config(state="disabled")
            notes.grid(row=5, column=0, columnspan=4, sticky="ew")
            row = 6

        buttons = tk.Frame(inner, bg=SURFACE)
        buttons.grid(row=row, column=0, columnspan=4, sticky="e", pady=(22, 0))
        ttk.Button(buttons, text="Close", style="Accent.TButton",
                   command=self.dialog.destroy).pack(side="left")

    def _toggle_password(self):
        self._visible = not self._visible
        self.password_label.config(
            text=self.data["password"] if self._visible else "\u2022" * 12)
        self.show_button.config(text="Hide" if self._visible else "Show")


class EditPasswordDialog(_PasswordFormMixin):
    """Dialog for editing an existing entry."""

    def __init__(self, parent, service, data, manager, refresh_callback):
        self.service = service
        self.data = data
        self.manager = manager
        self.refresh_callback = refresh_callback
        self.dialog = _dialog(parent, f"Edit {service}", DIALOG_WIDTH + 40, DIALOG_HEIGHT + 280)
        inner = _panel(self.dialog)

        ttk.Label(inner, text=service, style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(inner, text="Update the details below.",
                  style="CardMuted.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 16))

        ttk.Label(inner, text="Username / email", style="Field.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.username_entry = ttk.Entry(inner, width=36, font=FONT_BODY)
        self.username_entry.insert(0, self.data["username"])
        self.username_entry.grid(row=3, column=0, columnspan=2, sticky="ew", ipady=3)

        self._add_password_field(inner, 4, self.data["password"])
        self._add_strength_ui(inner, 6)
        ttk.Button(inner, text="Suggest a strong password",
                   command=self._generate_password).grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(8, 0))

        ttk.Label(inner, text="Notes", style="Field.TLabel").grid(
            row=9, column=0, columnspan=2, sticky="w", pady=(14, 5))
        self.notes_text = _notes_widget(inner, self.data.get("notes", ""))
        self.notes_text.grid(row=10, column=0, columnspan=2, sticky="ew")

        buttons = tk.Frame(inner, bg=SURFACE)
        buttons.grid(row=11, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(buttons, text="Cancel", command=self.dialog.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Save changes", style="Accent.TButton",
                   command=self._save).pack(side="left")

    def _save(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        notes = self.notes_text.get("1.0", "end-1c").strip()

        if not username or not password:
            messagebox.showerror("Missing details", "Username and password are required.",
                                 parent=self.dialog)
            return

        if self.manager.add_password(self.service, username, password, notes):
            messagebox.showinfo("Saved", "Password updated.", parent=self.dialog)
            self.refresh_callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update password.", parent=self.dialog)


class PasswordGeneratorDialog:
    """Dialog for generating and copying a random password."""

    def __init__(self, parent, copy_callback):
        self.copy_callback = copy_callback
        self.dialog = _dialog(
            parent, "Password generator", GENERATOR_DIALOG_WIDTH, GENERATOR_DIALOG_HEIGHT + 230)
        inner = _panel(self.dialog)

        ttk.Label(inner, text="Password generator", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(inner, text="Create a strong password with secure randomness.",
                  style="CardMuted.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 18))

        ttk.Label(inner, text="Length", style="Field.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 6))
        self.length_var = tk.IntVar(value=DEFAULT_PASSWORD_LENGTH)
        ttk.Spinbox(inner, from_=MIN_PASSWORD_LENGTH, to=MAX_PASSWORD_LENGTH,
                    textvariable=self.length_var, width=8, font=FONT_BODY).grid(
            row=2, column=1, sticky="w")

        ttk.Label(inner, text="Include", style="Field.TLabel").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(18, 6))
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)
        options = [
            ("Uppercase letters (A-Z)", self.uppercase_var),
            ("Lowercase letters (a-z)", self.lowercase_var),
            ("Digits (0-9)", self.digits_var),
            ("Special characters", self.special_var),
        ]
        for index, (text, variable) in enumerate(options, start=4):
            ttk.Checkbutton(inner, text=text, variable=variable,
                            style="Card.TCheckbutton").grid(
                row=index, column=0, columnspan=2, sticky="w", pady=2)

        ttk.Label(inner, text="Result", style="Field.TLabel").grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(18, 6))
        self.password_var = tk.StringVar()
        ttk.Entry(inner, textvariable=self.password_var, font=FONT_MONO,
                  state="readonly").grid(row=9, column=0, columnspan=2, sticky="ew", ipady=4)
        self.strength_meter = StrengthMeter(inner)
        self.strength_meter.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        buttons = tk.Frame(inner, bg=SURFACE)
        buttons.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        ttk.Button(buttons, text="Close", command=self.dialog.destroy).pack(side="left")
        ttk.Button(buttons, text="Copy", command=self._copy).pack(side="right", padx=(0, 8))
        ttk.Button(buttons, text="Generate", style="Accent.TButton",
                   command=self._generate).pack(side="right")
        self._generate()

    def _generate(self):
        password = PasswordGenerator.generate(
            length=self.length_var.get(),
            use_uppercase=self.uppercase_var.get(),
            use_lowercase=self.lowercase_var.get(),
            use_digits=self.digits_var.get(),
            use_special=self.special_var.get(),
        )
        if password is None:
            messagebox.showerror("No character types", "Select at least one character type.",
                                 parent=self.dialog)
            return
        self.password_var.set(password)
        level, label, _ = PasswordStrengthChecker.check_strength(password)
        self.strength_meter.set(level, label)

    def _copy(self):
        password = self.password_var.get()
        if password:
            self.copy_callback(password)
            messagebox.showinfo("Copied", "Password copied to clipboard.", parent=self.dialog)


class ChangePasswordDialog:
    """Dialog for replacing the master password."""

    def __init__(self, parent, manager, on_success):
        self.manager = manager
        self.on_success = on_success
        self.dialog = _dialog(parent, "Change master password",
                              DIALOG_WIDTH + 40, DIALOG_HEIGHT + 170)
        inner = _panel(self.dialog)

        ttk.Label(inner, text="Change master password", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(inner, text="Your vault will be re-encrypted with the new password.",
                  style="CardMuted.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 18))

        ttk.Label(inner, text="Current master password", style="Field.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.current_entry = ttk.Entry(inner, show="\u2022", width=36, font=FONT_BODY)
        self.current_entry.grid(row=3, column=0, columnspan=2, sticky="ew", ipady=3)
        self.current_entry.focus()

        ttk.Label(inner, text="New master password", style="Field.TLabel").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(14, 5))
        self.new_entry = ttk.Entry(inner, show="\u2022", width=36, font=FONT_BODY)
        self.new_entry.grid(row=5, column=0, columnspan=2, sticky="ew", ipady=3)
        self.new_entry.bind("<KeyRelease>", self._check_strength)

        self.strength_meter = StrengthMeter(inner)
        self.strength_meter.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        ttk.Label(inner, text="Confirm new password", style="Field.TLabel").grid(
            row=7, column=0, columnspan=2, sticky="w", pady=(10, 5))
        self.confirm_entry = ttk.Entry(inner, show="\u2022", width=36, font=FONT_BODY)
        self.confirm_entry.grid(row=8, column=0, columnspan=2, sticky="ew", ipady=3)

        self.show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(inner, text="Show passwords", variable=self.show_var,
                        command=self._toggle, style="Card.TCheckbutton").grid(
            row=9, column=0, columnspan=2, sticky="w", pady=(12, 0))

        buttons = tk.Frame(inner, bg=SURFACE)
        buttons.grid(row=10, column=0, columnspan=2, sticky="e", pady=(16, 0))
        ttk.Button(buttons, text="Cancel", command=self.dialog.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Change password", style="Accent.TButton",
                   command=self._save).pack(side="left")

    def _toggle(self):
        show = "" if self.show_var.get() else "\u2022"
        for entry in (self.current_entry, self.new_entry, self.confirm_entry):
            entry.config(show=show)

    def _check_strength(self, event=None):
        password = self.new_entry.get()
        if not password:
            self.strength_meter.set(0)
            return
        level, label, _ = PasswordStrengthChecker.check_strength(password)
        self.strength_meter.set(level, label)

    def _save(self):
        current = self.current_entry.get()
        new = self.new_entry.get()
        confirm = self.confirm_entry.get()

        if not current or not new:
            messagebox.showerror("Missing details", "Enter your current and new master password.",
                                 parent=self.dialog)
            return
        if new != confirm:
            messagebox.showerror("Mismatch", "The new passwords do not match.", parent=self.dialog)
            return
        if not self.manager.verify_master_password(current):
            messagebox.showerror("Incorrect", "Your current master password is incorrect.",
                                 parent=self.dialog)
            return
        if self.manager.change_master_password(current, new):
            messagebox.showinfo(
                "Password changed",
                "Your master password was changed. Remember the new one, it cannot be recovered.",
                parent=self.dialog,
            )
            self.dialog.destroy()
            self.on_success()
        else:
            messagebox.showerror("Error", "Failed to re-encrypt the vault.", parent=self.dialog)
