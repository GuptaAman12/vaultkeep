"""
Main application window for the password manager.
Handles the login screen and main password list interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from password_manager import PasswordManager
from constants import EXPORT_FILE_TYPES
from logger import logger
from gui_components import (
    AddPasswordDialog, 
    ViewPasswordDialog, 
    EditPasswordDialog, 
    PasswordGeneratorDialog
)


class PasswordManagerGUI:
    """Main GUI application for the password manager."""
    
    def __init__(self, root):
        """
        Initialize the password manager GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Secure Password Manager")
        self.root.geometry("800x600")
        self.manager = PasswordManager()
        self.authenticated = False
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Show login screen
        self.show_login()
    
    def show_login(self):
        """Show master password login screen."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create login frame
        login_frame = ttk.Frame(self.root, padding="50")
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(login_frame, text="Password Manager",
                 font=('Arial', 24, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(login_frame, text="Master Password:",
                 font=('Arial', 12)).grid(row=1, column=0, sticky='e', padx=5, pady=10)
        
        self.master_password_entry = ttk.Entry(login_frame, show="*", width=30, font=('Arial', 12))
        self.master_password_entry.grid(row=1, column=1, padx=5, pady=10)
        self.master_password_entry.focus()
        self.master_password_entry.bind('<Return>', lambda e: self.login())
        
        ttk.Button(login_frame, text="Login",
                  command=self.login).grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Label(login_frame, text="First time? Enter a new master password to create your vault.",
                 font=('Arial', 9), foreground='gray').grid(row=3, column=0, columnspan=2)
    
    def login(self):
        """Authenticate with master password."""
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
        """Show main password manager interface."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Passwords...", command=self.export_passwords)
        file_menu.add_command(label="Import Passwords...", command=self.import_passwords)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Create main layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Top frame (search and buttons)
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(top_frame, text="Search:", font=('Arial', 10)).pack(side='left', padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        
        ttk.Button(top_frame, text="+ Add Password",
                  command=self.add_password_dialog).pack(side='right', padx=5)
        
        ttk.Button(top_frame, text="Generate Password",
                  command=self.generate_password_dialog).pack(side='right', padx=5)
        
        # Password list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky='nsew')
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview
        columns = ('Service', 'Username')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=20)
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        # Configure columns
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('Service', width=300)
        self.tree.column('Username', width=300)
        
        self.tree.heading('Service', text='Service / Website')
        self.tree.heading('Username', text='Username / Email')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to view password
        self.tree.bind('<Double-Button-1>', self.view_password)
        
        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="View", command=self.view_password)
        self.context_menu.add_command(label="Copy Password", command=self.copy_password)
        self.context_menu.add_command(label="Edit", command=self.edit_password)
        self.context_menu.add_command(label="Delete", command=self.delete_password)
        
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Load passwords
        self.refresh_list()
    
    def refresh_list(self, filter_text=""):
        """
        Refresh password list.
        
        Args:
            filter_text: Optional filter string for search
        """
        self.tree.delete(*self.tree.get_children())
        
        services = self.manager.get_all_services()
        if filter_text:
            services = [s for s in services if filter_text.lower() in s.lower()]
        
        for service in services:
            data = self.manager.get_password(service)
            self.tree.insert('', 'end', values=(service, data['username']))
    
    def on_search(self, *args):
        """Handle search input."""
        self.refresh_list(self.search_var.get())
    
    def show_context_menu(self, event):
        """Show right-click context menu."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def add_password_dialog(self):
        """Show dialog to add new password."""
        AddPasswordDialog(self.root, self.manager, self.refresh_list)
    
    def view_password(self, event=None):
        """View selected password."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        service = item['values'][0]
        data = self.manager.get_password(service)
        
        ViewPasswordDialog(self.root, service, data, self.copy_to_clipboard)
    
    def copy_password(self):
        """Copy password to clipboard."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        service = item['values'][0]
        data = self.manager.get_password(service)
        
        self.copy_to_clipboard(data['password'])
        messagebox.showinfo("Success", "Password copied to clipboard")
    
    def copy_to_clipboard(self, text):
        """
        Copy text to clipboard.
        
        Args:
            text: Text to copy
        """
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  # Required for clipboard to work
    
    def edit_password(self):
        """Edit selected password."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        service = item['values'][0]
        data = self.manager.get_password(service)
        
        EditPasswordDialog(self.root, service, data, self.manager, self.refresh_list)
    
    def delete_password(self):
        """Delete selected password."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        service = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete",
                              f"Are you sure you want to delete the password for '{service}'?"):
            if self.manager.delete_password(service):
                messagebox.showinfo("Success", "Password deleted successfully")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to delete password")
    
    def generate_password_dialog(self):
        """Show password generator dialog."""
        PasswordGeneratorDialog(self.root, self.copy_to_clipboard)
    
    def export_passwords(self):
        """Export passwords to backup file."""
        default_filename = f"passwords_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            title="Export Passwords",
            defaultextension=".json",
            filetypes=EXPORT_FILE_TYPES,
            initialfile=default_filename
        )
        
        if filepath:
            if self.manager.export_to_file(filepath):
                count = len(self.manager.passwords)
                messagebox.showinfo("Success", 
                    f"Exported {count} passwords to:\n{filepath}")
                logger.info(f"User exported {count} passwords")
            else:
                messagebox.showerror("Error", "Failed to export passwords")
    
    def import_passwords(self):
        """Import passwords from backup file."""
        filepath = filedialog.askopenfilename(
            title="Import Passwords",
            filetypes=EXPORT_FILE_TYPES
        )
        
        if filepath:
            # Ask user about merge strategy
            dialog = tk.Toplevel(self.root)
            dialog.title("Import Options")
            dialog.geometry("400x200")
            dialog.transient(self.root)
            dialog.grab_set()
            
            frame = ttk.Frame(dialog, padding="20")
            frame.pack(fill='both', expand=True)
            
            ttk.Label(frame, text="How should conflicts be handled?",
                     font=('Arial', 12, 'bold')).pack(pady=10)
            
            ttk.Label(frame, text="(Services that already exist in your vault)",
                     font=('Arial', 9)).pack(pady=5)
            
            strategy_var = tk.StringVar(value='skip')
            
            ttk.Radiobutton(frame, text="Skip - Keep existing passwords",
                           variable=strategy_var, value='skip').pack(anchor='w', pady=5)
            ttk.Radiobutton(frame, text="Overwrite - Replace with imported passwords",
                           variable=strategy_var, value='overwrite').pack(anchor='w', pady=5)
            ttk.Radiobutton(frame, text="Rename - Import as new entries with suffix",
                           variable=strategy_var, value='rename').pack(anchor='w', pady=5)
            
            def do_import():
                strategy = strategy_var.get()
                dialog.destroy()
                
                count = self.manager.import_from_file(filepath, strategy)
                if count >= 0:
                    messagebox.showinfo("Success",
                        f"Imported {count} passwords from:\n{filepath}")
                    self.refresh_list()
                    logger.info(f"User imported {count} passwords with strategy: {strategy}")
                else:
                    messagebox.showerror("Error", "Failed to import passwords")
            
            button_frame = ttk.Frame(frame)
            button_frame.pack(pady=20)
            ttk.Button(button_frame, text="Import", command=do_import).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About Password Manager",
            "Secure Password Manager v2.0\n\n"
            "Features:\n"
            "• AES-128 encryption (Fernet)\n"
            "• PBKDF2 key derivation (100,000 iterations)\n"
            "• Password strength checker\n"
            "• Secure password generator\n"
            "• Export/Import functionality\n"
            "• Comprehensive logging\n\n"
            "Keep your master password safe!")
