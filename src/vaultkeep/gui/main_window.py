"""Main application window: login screen and vault list."""

import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from ..constants import (
    APP_NAME, EXPORT_FILE_EXTENSION, EXPORT_FILE_TYPES, FONT_LARGE, FONT_NORMAL,
    FONT_SMALL, FONT_TITLE, SEARCH_DEBOUNCE_MS, THEME, WINDOW_HEIGHT, WINDOW_WIDTH,
)
from ..core.vault import PasswordManager
from ..logging_config import logger
from .dialogs import (
    AddPasswordDialog, EditPasswordDialog, PasswordGeneratorDialog, ViewPasswordDialog,
)


class PasswordManagerGUI:
    """Main GUI application for the password manager."""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.manager = PasswordManager()
        self.authenticated = False
        self._search_job = None

        ttk.Style().theme_use(THEME)
        self.show_login()

    def show_login(self):
        """Show the master password prompt."""
        for widget in self.root.winfo_children():
            widget.destroy()

        login_frame = ttk.Frame(self.root, padding="50")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(login_frame, text=APP_NAME, font=FONT_TITLE).grid(
            row=0, column=0, columnspan=2, pady=20)
        ttk.Label(login_frame, text="Master Password:", font=FONT_LARGE).grid(
            row=1, column=0, sticky="e", padx=5, pady=10)

        self.master_password_entry = ttk.Entry(
            login_frame, show="*", width=30, font=FONT_LARGE)
        self.master_password_entry.grid(row=1, column=1, padx=5, pady=10)
        self.master_password_entry.focus()
        self.master_password_entry.bind("<Return>", lambda e: self.login())

        ttk.Button(login_frame, text="Login", command=self.login).grid(
            row=2, column=0, columnspan=2, pady=20)
        ttk.Label(login_frame,
                  text="First time? Enter a new master password to create your vault.",
                  font=FONT_SMALL, foreground="gray").grid(row=3, column=0, columnspan=2)

    def login(self):
        """Unlock the vault with the entered master password."""
        master_password = self.master_password_entry.get()
        if not master_password:
            messagebox.showerror("Error", "Please enter master password")
            return

        if self.manager.initialize(master_password):
            self.authenticated = True
            self.show_main_window()
        else:
            messagebox.showerror("Error", "Invalid master password")
            self.master_password_entry.delete(0, tk.END)

    def show_main_window(self):
        """Show the vault list and menu bar."""
        for widget in self.root.winfo_children():
            widget.destroy()

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Passwords...", command=self.export_passwords)
        file_menu.add_command(label="Import Passwords...", command=self.import_passwords)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(top_frame, text="Search:", font=FONT_NORMAL).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        ttk.Entry(top_frame, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        ttk.Button(top_frame, text="+ Add Password",
                   command=self.add_password_dialog).pack(side="right", padx=5)
        ttk.Button(top_frame, text="Generate Password",
                   command=self.generate_password_dialog).pack(side="right", padx=5)

        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        columns = ("Service", "Username")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=20)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("Service", width=300)
        self.tree.column("Username", width=300)
        self.tree.heading("Service", text="Service / Website")
        self.tree.heading("Username", text="Username / Email")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-Button-1>", self.view_password)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="View", command=self.view_password)
        self.context_menu.add_command(label="Copy Password", command=self.copy_password)
        self.context_menu.add_command(label="Edit", command=self.edit_password)
        self.context_menu.add_command(label="Delete", command=self.delete_password)

        self.refresh_list()

    def refresh_list(self, filter_text=""):
        """Rebuild the list, optionally limited to services matching the filter."""
        self.tree.delete(*self.tree.get_children())
        services = self.manager.search(filter_text) if filter_text else self.manager.get_all_services()
        for service in services:
            data = self.manager.get_password(service)
            self.tree.insert("", "end", values=(service, data["username"]))

    def on_search(self, *args):
        """Debounce search so typing does not rebuild the list on every keystroke."""
        if self._search_job is not None:
            self.root.after_cancel(self._search_job)
        self._search_job = self.root.after(SEARCH_DEBOUNCE_MS, self._apply_search)

    def _apply_search(self):
        self._search_job = None
        self.refresh_list(self.search_var.get().strip())

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
                              f"Are you sure you want to delete the password for '{service}'?"):
            if self.manager.delete_password(service):
                messagebox.showinfo("Success", "Password deleted successfully")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to delete password")

    def generate_password_dialog(self):
        PasswordGeneratorDialog(self.root, self.copy_to_clipboard)

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
                count = len(self.manager.passwords)
                messagebox.showinfo("Success", f"Exported {count} passwords to:\n{filepath}")
                logger.info(f"User exported {count} passwords")
            else:
                messagebox.showerror("Error", "Failed to export passwords")

    def import_passwords(self):
        filepath = filedialog.askopenfilename(title="Import Passwords", filetypes=EXPORT_FILE_TYPES)
        if not filepath:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Import Options")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="How should conflicts be handled?",
                  font=FONT_LARGE).pack(pady=10)
        ttk.Label(frame, text="(Services that already exist in your vault)",
                  font=FONT_SMALL).pack(pady=5)
        strategy_var = tk.StringVar(value="skip")
        ttk.Radiobutton(frame, text="Skip - Keep existing passwords",
                        variable=strategy_var, value="skip").pack(anchor="w", pady=5)
        ttk.Radiobutton(frame, text="Overwrite - Replace with imported passwords",
                        variable=strategy_var, value="overwrite").pack(anchor="w", pady=5)
        ttk.Radiobutton(frame, text="Rename - Import as new entries with suffix",
                        variable=strategy_var, value="rename").pack(anchor="w", pady=5)

        def do_import():
            strategy = strategy_var.get()
            dialog.destroy()
            count = self.manager.import_from_file(filepath, strategy)
            if count >= 0:
                messagebox.showinfo("Success", f"Imported {count} passwords from:\n{filepath}")
                self.refresh_list()
                logger.info(f"User imported {count} passwords with strategy: {strategy}")
            else:
                messagebox.showerror("Error", "Failed to import passwords")

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Import", command=do_import).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    def show_about(self):
        messagebox.showinfo(
            f"About {APP_NAME}",
            f"{APP_NAME} v2.1\n\n"
            "Features:\n"
            "• AES-128 encryption (Fernet)\n"
            "• PBKDF2 key derivation (100,000 iterations)\n"
            "• Password strength checker\n"
            "• Secure password generator\n"
            "• Export/Import functionality\n"
            "• Comprehensive logging\n\n"
            "Keep your master password safe!",
        )
