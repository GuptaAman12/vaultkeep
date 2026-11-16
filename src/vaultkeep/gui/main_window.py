"""Main application window: login screen and vault list."""

import os
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ..constants import (
    APP_NAME, CLIPBOARD_CLEAR_MS, EXPORT_FILE_EXTENSION, EXPORT_FILE_TYPES,
    SEARCH_DEBOUNCE_MS, WINDOW_HEIGHT, WINDOW_WIDTH,
)
from ..core.vault import PasswordManager
from ..logging_config import logger
from .dialogs import (
    AddPasswordDialog, ChangePasswordDialog, EditPasswordDialog,
    PasswordGeneratorDialog, ViewPasswordDialog,
)
from .theme import (
    BG, MUTED, SURFACE, SURFACE_ALT, TEXT, apply_theme, card, menu, FONT_BODY,
)

SEARCH_PLACEHOLDER = "Search services..."
LOGO_PATH = Path(__file__).resolve().parents[1] / "assets" / "vaultkeep.png"


class PasswordManagerGUI:
    """Main GUI application for the password manager."""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(680, 520)
        self.manager = PasswordManager()
        self.authenticated = False
        self._search_job = None
        self._clipboard_job = None
        self._clipboard_text = None
        apply_theme(root)
        self.logo = tk.PhotoImage(file=str(LOGO_PATH))
        self.logo_small = self.logo.subsample(12)
        self.root.iconphoto(True, self.logo)
        self.show_login()

    def show_login(self):
        """Show the master password prompt."""
        self.root.config(menu="")
        for widget in self.root.winfo_children():
            widget.destroy()

        first_time = not os.path.exists(self.manager.data_file)
        panel = card(self.root)
        panel.place(relx=0.5, rely=0.5, anchor="center")
        inner = tk.Frame(panel, bg=SURFACE)
        inner.grid(row=0, column=0, padx=36, pady=32)

        ttk.Label(inner, image=self.logo_small, style="Card.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 14))

        title = "Create your vault" if first_time else f"Welcome back to {APP_NAME}"
        ttk.Label(inner, text=title, style="Title.TLabel").grid(
            row=1, column=0, columnspan=2, pady=(0, 4))
        subtitle = ("Choose a master password to get started."
                    if first_time else "Enter your master password to unlock your vault.")
        ttk.Label(inner, text=subtitle, style="CardMuted.TLabel").grid(
            row=2, column=0, columnspan=2, pady=(0, 22))

        ttk.Label(inner, text="Master password", style="Field.TLabel").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.master_password_entry = ttk.Entry(
            inner, show="\u2022", width=28, font=FONT_BODY)
        self.master_password_entry.grid(row=4, column=0, sticky="ew", ipady=3)
        self._master_visible = False
        self.master_toggle = ttk.Button(
            inner, text="Show", width=8, command=self._toggle_master_visibility)
        self.master_toggle.grid(row=4, column=1, padx=(8, 0))

        self.login_error = ttk.Label(inner, text="", style="Error.TLabel")
        self.login_error.grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))

        action = "Create vault" if first_time else "Unlock vault"
        self.login_button = ttk.Button(
            inner, text=action, style="Accent.TButton", command=self.login)
        self.login_button.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        self.master_password_entry.bind("<Return>", lambda event: self.login())

        note = ("Keep this password safe. It cannot be recovered."
                if first_time else "Your vault is encrypted on this device.")
        ttk.Label(inner, text=note, style="CardMuted.TLabel").grid(
            row=7, column=0, columnspan=2, pady=(18, 0))
        self.master_password_entry.focus()

    def _toggle_master_visibility(self):
        self._master_visible = not self._master_visible
        self.master_password_entry.config(show="" if self._master_visible else "\u2022")
        self.master_toggle.config(text="Hide" if self._master_visible else "Show")

    def login(self):
        """Unlock the vault with the entered master password."""
        master_password = self.master_password_entry.get()
        if not master_password:
            self.login_error.config(text="Enter your master password.")
            return

        if self.manager.initialize(master_password):
            self.authenticated = True
            self.show_main_window()
            self._maybe_remind_password_change()
        else:
            self.login_error.config(text="That password did not unlock the vault.")
            self.master_password_entry.delete(0, tk.END)
            self.master_password_entry.focus()

    def lock(self):
        """Drop the decrypted entries and return to the login screen."""
        if self._search_job is not None:
            self.root.after_cancel(self._search_job)
            self._search_job = None
        if self._clipboard_job is not None:
            self.root.after_cancel(self._clipboard_job)
            self._clipboard_job = None
        self._clear_clipboard(self._clipboard_text)
        self.manager.passwords.clear()
        self.manager.crypto.cipher = None
        self.authenticated = False
        self.show_login()

    def show_main_window(self):
        """Show the vault list and menu bar."""
        for widget in self.root.winfo_children():
            widget.destroy()

        menubar = menu(self.root)
        self.root.config(menu=menubar)
        file_menu = menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Passwords...", command=self.export_passwords)
        file_menu.add_command(label="Import Passwords...", command=self.import_passwords)
        file_menu.add_separator()
        file_menu.add_command(label="Change Master Password...",
                              command=self.change_password_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Lock Vault", command=self.lock)
        file_menu.add_command(label="Exit", command=self.root.quit)
        help_menu = menu(menubar)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(self.root)
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)
        ttk.Label(header, text=APP_NAME, style="Brand.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Encrypted on this device", style="Muted.TLabel").grid(
            row=1, column=0, sticky="w")
        ttk.Button(header, text="Lock", command=self.lock).grid(row=0, column=1, rowspan=2, padx=8)

        toolbar = card(self.root)
        toolbar.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        tools = tk.Frame(toolbar, bg=SURFACE)
        tools.pack(fill="x", padx=14, pady=12)

        # Pack actions first so they stay visible when the window shrinks.
        actions = tk.Frame(tools, bg=SURFACE)
        actions.pack(side="right")
        ttk.Button(actions, text="+ Add password", style="Accent.TButton",
                   command=self.add_password_dialog).pack(side="right")
        ttk.Button(actions, text="Generate",
                   command=self.generate_password_dialog).pack(side="right", padx=(0, 8))
        self.count_label = ttk.Label(actions, text="", style="CardMuted.TLabel")
        self.count_label.pack(side="right", padx=(0, 14))

        search_area = tk.Frame(tools, bg=SURFACE)
        search_area.pack(side="left", fill="x", expand=True)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        self.search_entry = ttk.Entry(
            search_area, textvariable=self.search_var, width=18, font=FONT_BODY)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.insert(0, SEARCH_PLACEHOLDER)
        self.search_entry.config(foreground=MUTED)
        self.search_entry.bind("<FocusIn>", self._search_focus_in)
        self.search_entry.bind("<FocusOut>", self._search_focus_out)
        ttk.Button(search_area, text="Clear", command=self.clear_search).pack(
            side="left", padx=(8, 0))

        list_card = card(self.root)
        list_card.grid(row=2, column=0, sticky="nsew", padx=18)
        list_card.grid_rowconfigure(0, weight=1)
        list_card.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            list_card, columns=("Service", "Username"), show="headings",
            height=14, selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(1, 0), pady=1)
        self.tree.heading("Service", text="SERVICE / WEBSITE", anchor="w")
        self.tree.heading("Username", text="USERNAME / EMAIL", anchor="w")
        self.tree.column("Service", width=240, minwidth=100, anchor="w")
        self.tree.column("Username", width=240, minwidth=100, anchor="w")
        self.tree.tag_configure("odd", background=SURFACE_ALT)
        self.tree.bind("<Double-Button-1>", self.view_password)
        self.tree.bind("<Button-3>", self.show_context_menu)

        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.empty_label = tk.Label(
            list_card,
            text="No passwords here yet.\nUse Add password to create your first entry.",
            bg=SURFACE, fg=MUTED, font=FONT_BODY, justify="center")
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(self.root,
                  text="Double-click an entry to view it. Right-click for more actions.",
                  style="Muted.TLabel").grid(row=3, column=0, sticky="w", padx=20, pady=(8, 12))

        self.context_menu = menu(self.root)
        self.context_menu.add_command(label="View", command=self.view_password)
        self.context_menu.add_command(label="Copy password", command=self.copy_password)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Edit", command=self.edit_password)
        self.context_menu.add_command(label="Delete", command=self.delete_password)

        self.refresh_list()

    def _search_value(self):
        value = self.search_var.get().strip()
        return "" if value == SEARCH_PLACEHOLDER else value

    def _search_focus_in(self, event=None):
        if self.search_var.get() == SEARCH_PLACEHOLDER:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground=TEXT)

    def _search_focus_out(self, event=None):
        if not self.search_var.get().strip():
            self.search_entry.insert(0, SEARCH_PLACEHOLDER)
            self.search_entry.config(foreground=MUTED)

    def clear_search(self):
        self.search_var.set(SEARCH_PLACEHOLDER)
        self.search_entry.config(foreground=MUTED)
        self.refresh_list("")

    def refresh_list(self, filter_text=None):
        """Rebuild the list, optionally limited to services matching the filter."""
        if filter_text is None:
            filter_text = self._search_value()
        services = self.manager.search(filter_text) if filter_text else self.manager.get_all_services()

        self.tree.delete(*self.tree.get_children())
        for index, service in enumerate(services):
            data = self.manager.get_password(service)
            tags = ("odd",) if index % 2 else ()
            self.tree.insert("", "end", values=(service, data["username"]), tags=tags)
        self.count_label.config(text=f"{len(services)} {'entry' if len(services) == 1 else 'entries'}")

        if services:
            self.empty_label.place_forget()
        else:
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
            self.empty_label.lift()

    def on_search(self, *args):
        """Debounce search so typing does not rebuild the list on every keystroke."""
        if self.search_var.get() == SEARCH_PLACEHOLDER:
            return
        if self._search_job is not None:
            self.root.after_cancel(self._search_job)
        self._search_job = self.root.after(SEARCH_DEBOUNCE_MS, self._apply_search)

    def _apply_search(self):
        self._search_job = None
        self.refresh_list(self._search_value())

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def selected_service(self):
        """Return the service name for the selected row, or None."""
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0])["values"][0]

    def add_password_dialog(self):
        AddPasswordDialog(self.root, self.manager, self.refresh_list)

    def view_password(self, event=None):
        service = self.selected_service()
        if service is None:
            return
        ViewPasswordDialog(self.root, service, self.manager.get_password(service),
                           self.copy_to_clipboard)

    def copy_password(self):
        service = self.selected_service()
        if service is None:
            return
        self.copy_to_clipboard(self.manager.get_password(service)["password"])
        messagebox.showinfo("Success", "Password copied to clipboard")

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  # Required for the clipboard to work on Windows
        self._clipboard_text = text
        if self._clipboard_job is not None:
            self.root.after_cancel(self._clipboard_job)
        self._clipboard_job = self.root.after(
            CLIPBOARD_CLEAR_MS, self._clear_clipboard, text)

    def _clear_clipboard(self, text):
        self._clipboard_job = None
        if text is None:
            return
        try:
            if self.root.clipboard_get() == text:
                self.root.clipboard_clear()
                self.root.update()
        except tk.TclError:
            pass

    def edit_password(self):
        service = self.selected_service()
        if service is None:
            return
        EditPasswordDialog(self.root, service, self.manager.get_password(service),
                           self.manager, self.refresh_list)

    def delete_password(self):
        service = self.selected_service()
        if service is None:
            return
        if messagebox.askyesno("Confirm Delete",
                              f"Delete the saved password for '{service}'?"):
            if self.manager.delete_password(service):
                messagebox.showinfo("Success", "Password deleted")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to delete password")

    def generate_password_dialog(self):
        PasswordGeneratorDialog(self.root, self.copy_to_clipboard)

    def change_password_dialog(self):
        ChangePasswordDialog(self.root, self.manager, self.refresh_list)

    def _maybe_remind_password_change(self):
        if not self.manager.password_change_due():
            return
        answer = messagebox.askyesnocancel(
            "Master password reminder",
            "It has been over two months since you changed your master password.\n\n"
            "Change it now?",
        )
        if answer is True:
            self.change_password_dialog()
        else:
            self.manager.snooze_password_reminder()

    def export_passwords(self):
        default_filename = f"passwords_backup_{datetime.now():%Y%m%d_%H%M%S}.json"
        filepath = filedialog.asksaveasfilename(
            title="Export Passwords",
            defaultextension=EXPORT_FILE_EXTENSION,
            filetypes=EXPORT_FILE_TYPES,
            initialfile=default_filename,
        )
        if filepath:
            if self.manager.export_to_file(filepath):
                count = len(self.manager.get_all_services())
                messagebox.showinfo("Success", f"Exported {count} passwords to:\n{filepath}")
                logger.info(f"User exported {count} passwords")
            else:
                messagebox.showerror("Error", "Failed to export passwords")

    def import_passwords(self):
        filepath = filedialog.askopenfilename(title="Import Passwords", filetypes=EXPORT_FILE_TYPES)
        if not filepath:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Import Passwords")
        dialog.geometry("460x320")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=BG)
        panel = card(dialog)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=420, height=270)
        inner = tk.Frame(panel, bg=SURFACE)
        inner.grid(row=0, column=0, padx=24, pady=22, sticky="ew")
        inner.grid_columnconfigure(0, weight=1)

        ttk.Label(inner, text="Resolve duplicate services", style="Field.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Label(inner, text="These services already exist in your vault.",
                  style="CardMuted.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 16))

        strategy_var = tk.StringVar(value="skip")
        ttk.Radiobutton(inner, text="Skip existing entries",
                        variable=strategy_var, value="skip").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Radiobutton(inner, text="Overwrite with imported entries",
                        variable=strategy_var, value="overwrite").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Radiobutton(inner, text="Keep both, renaming imports",
                        variable=strategy_var, value="rename").grid(row=4, column=0, sticky="w", pady=3)

        def do_import():
            strategy = strategy_var.get()
            dialog.destroy()
            count = self.manager.import_from_file(filepath, strategy)
            if count >= 0:
                messagebox.showinfo("Success", f"Imported {count} passwords")
                self.refresh_list()
                logger.info(f"User imported {count} passwords with strategy: {strategy}")
            else:
                messagebox.showerror("Error", "Failed to import passwords")

        buttons = tk.Frame(inner, bg=SURFACE)
        buttons.grid(row=5, column=0, sticky="e", pady=(20, 0))
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Import", style="Accent.TButton",
                   command=do_import).pack(side="left")

    def show_about(self):
        messagebox.showinfo(
            f"About {APP_NAME}",
            f"{APP_NAME}\n\n"
            "A local password vault with AES encryption, a strength meter, a secure "
            "generator and JSON backups.\n\n"
            "Your master password is never stored. Keep it safe.",
        )
