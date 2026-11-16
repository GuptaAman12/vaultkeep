"""
Reusable GUI dialog components for the password manager.
Contains dialogs for adding, viewing, editing passwords and generating passwords.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from password_generator import PasswordGenerator
from password_strength import PasswordStrengthChecker


class AddPasswordDialog:
    """Dialog for adding a new password entry."""
    
    def __init__(self, parent, manager, refresh_callback):
        """
        Initialize add password dialog.
        
        Args:
            parent: Parent window
            manager: PasswordManager instance
            refresh_callback: Function to call after successful save
        """
        self.manager = manager
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Password")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        # Service
        ttk.Label(frame, text="Service / Website:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='w', pady=5)
        self.service_entry = ttk.Entry(frame, width=40, font=('Arial', 10))
        self.service_entry.grid(row=0, column=1, pady=5, padx=5)
        self.service_entry.focus()
        
        # Username
        ttk.Label(frame, text="Username / Email:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(frame, width=40, font=('Arial', 10))
        self.username_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Password
        ttk.Label(frame, text="Password:", font=('Arial', 10)).grid(
            row=2, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(frame, width=40, show="*", font=('Arial', 10))
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)
        self.password_entry.bind('<KeyRelease>', self._check_strength)
        
        # Show password checkbox
        self.show_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Show password", variable=self.show_var,
                       command=self._toggle_password).grid(row=3, column=1, sticky='w', padx=5)
        
        # Password strength indicator
        ttk.Label(frame, text="Strength:", font=('Arial', 10)).grid(
            row=4, column=0, sticky='w', pady=5)
        self.strength_label = ttk.Label(frame, text="-", font=('Arial', 10))
        self.strength_label.grid(row=4, column=1, sticky='w', pady=5, padx=5)
        
        # Notes
        ttk.Label(frame, text="Notes:", font=('Arial', 10)).grid(
            row=5, column=0, sticky='nw', pady=5)
        self.notes_text = tk.Text(frame, width=40, height=5, font=('Arial', 10))
        self.notes_text.grid(row=5, column=1, pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def _toggle_password(self):
        """Toggle password visibility."""
        self.password_entry.config(show="" if self.show_var.get() else "*")
    
    def _check_strength(self, event=None):
        """Check and display password strength."""
        password = self.password_entry.get()
        if password:
            strength_level, strength_text, feedback = PasswordStrengthChecker.check_strength(password)
            color = PasswordStrengthChecker.get_strength_color(strength_level)
            self.strength_label.config(text=strength_text, foreground=color)
        else:
            self.strength_label.config(text="-", foreground="black")
    
    def _save(self):
        """Save the password entry."""
        service = self.service_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        notes = self.notes_text.get('1.0', 'end-1c').strip()
        
        if not service or not username or not password:
            messagebox.showerror("Error", "Service, username, and password are required")
            return
        
        if self.manager.add_password(service, username, password, notes):
            messagebox.showinfo("Success", "Password added successfully")
            self.refresh_callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save password")


class ViewPasswordDialog:
    """Dialog for viewing a password entry."""
    
    def __init__(self, parent, service, data, copy_callback):
        """
        Initialize view password dialog.
        
        Args:
            parent: Parent window
            service: Service name
            data: Password data dictionary
            copy_callback: Function to copy text to clipboard
        """
        self.data = data
        self.copy_callback = copy_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Password - {service}")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        
        self._create_widgets(service)
    
    def _create_widgets(self, service):
        """Create dialog widgets."""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        # Service
        ttk.Label(frame, text="Service:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5)
        ttk.Label(frame, text=service, font=('Arial', 10)).grid(
            row=0, column=1, sticky='w', pady=5)
        
        # Username
        ttk.Label(frame, text="Username:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=5)
        
        username_frame = ttk.Frame(frame)
        username_frame.grid(row=1, column=1, sticky='w', pady=5)
        ttk.Label(username_frame, text=self.data['username'], font=('Arial', 10)).pack(side='left')
        ttk.Button(username_frame, text="Copy", width=8,
                  command=lambda: self.copy_callback(self.data['username'])).pack(side='left', padx=5)
        
        # Password
        ttk.Label(frame, text="Password:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=5)
        
        password_frame = ttk.Frame(frame)
        password_frame.grid(row=2, column=1, sticky='w', pady=5)
        
        self.password_label = ttk.Label(password_frame, text="•" * 12, font=('Arial', 10))
        self.password_label.pack(side='left')
        
        self.show_var = tk.BooleanVar()
        ttk.Checkbutton(password_frame, text="Show", variable=self.show_var,
                       command=self._toggle_password).pack(side='left', padx=5)
        ttk.Button(password_frame, text="Copy", width=8,
                  command=lambda: self.copy_callback(self.data['password'])).pack(side='left', padx=5)
        
        # Notes
        if self.data.get('notes'):
            ttk.Label(frame, text="Notes:", font=('Arial', 10, 'bold')).grid(
                row=3, column=0, sticky='nw', pady=5)
            notes_text = tk.Text(frame, width=40, height=8, font=('Arial', 10))
            notes_text.grid(row=3, column=1, pady=5)
            notes_text.insert('1.0', self.data['notes'])
            notes_text.config(state='disabled')
        
        ttk.Button(frame, text="Close", command=self.dialog.destroy).grid(
            row=4, column=0, columnspan=2, pady=20)
    
    def _toggle_password(self):
        """Toggle password visibility."""
        if self.show_var.get():
            self.password_label.config(text=self.data['password'])
        else:
            self.password_label.config(text="•" * 12)


class EditPasswordDialog:
    """Dialog for editing a password entry."""
    
    def __init__(self, parent, service, data, manager, refresh_callback):
        """
        Initialize edit password dialog.
        
        Args:
            parent: Parent window
            service: Service name
            data: Password data dictionary
            manager: PasswordManager instance
            refresh_callback: Function to call after successful save
        """
        self.service = service
        self.data = data
        self.manager = manager
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Edit - {service}")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        # Service (read-only)
        ttk.Label(frame, text="Service / Website:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='w', pady=5)
        ttk.Label(frame, text=self.service, font=('Arial', 10, 'bold')).grid(
            row=0, column=1, sticky='w', pady=5, padx=5)
        
        # Username
        ttk.Label(frame, text="Username / Email:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(frame, width=40, font=('Arial', 10))
        self.username_entry.grid(row=1, column=1, pady=5, padx=5)
        self.username_entry.insert(0, self.data['username'])
        
        # Password
        ttk.Label(frame, text="Password:", font=('Arial', 10)).grid(
            row=2, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(frame, width=40, show="*", font=('Arial', 10))
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)
        self.password_entry.insert(0, self.data['password'])
        self.password_entry.bind('<KeyRelease>', self._check_strength)
        
        # Show password checkbox
        self.show_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Show password", variable=self.show_var,
                       command=self._toggle_password).grid(row=3, column=1, sticky='w', padx=5)
        
        # Password strength indicator
        ttk.Label(frame, text="Strength:", font=('Arial', 10)).grid(
            row=4, column=0, sticky='w', pady=5)
        self.strength_label = ttk.Label(frame, text="-", font=('Arial', 10))
        self.strength_label.grid(row=4, column=1, sticky='w', pady=5, padx=5)
        self._check_strength()  # Check initial password strength
        
        # Notes
        ttk.Label(frame, text="Notes:", font=('Arial', 10)).grid(
            row=5, column=0, sticky='nw', pady=5)
        self.notes_text = tk.Text(frame, width=40, height=5, font=('Arial', 10))
        self.notes_text.grid(row=5, column=1, pady=5, padx=5)
        self.notes_text.insert('1.0', self.data.get('notes', ''))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def _toggle_password(self):
        """Toggle password visibility."""
        self.password_entry.config(show="" if self.show_var.get() else "*")
    
    def _check_strength(self, event=None):
        """Check and display password strength."""
        password = self.password_entry.get()
        if password:
            strength_level, strength_text, feedback = PasswordStrengthChecker.check_strength(password)
            color = PasswordStrengthChecker.get_strength_color(strength_level)
            self.strength_label.config(text=strength_text, foreground=color)
        else:
            self.strength_label.config(text="-", foreground="black")
    
    def _save(self):
        """Save the updated password entry."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        notes = self.notes_text.get('1.0', 'end-1c').strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        if self.manager.add_password(self.service, username, password, notes):
            messagebox.showinfo("Success", "Password updated successfully")
            self.refresh_callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update password")


class PasswordGeneratorDialog:
    """Dialog for generating secure passwords."""
    
    def __init__(self, parent, copy_callback):
        """
        Initialize password generator dialog.
        
        Args:
            parent: Parent window
            copy_callback: Function to copy text to clipboard
        """
        self.copy_callback = copy_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Password Generator")
        self.dialog.geometry("450x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        self._generate()  # Generate initial password
    
    def _create_widgets(self):
        """Create dialog widgets."""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Generate Strong Password",
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Length
        length_frame = ttk.Frame(frame)
        length_frame.pack(pady=10, fill='x')
        
        ttk.Label(length_frame, text="Length:", font=('Arial', 10)).pack(side='left', padx=5)
        
        self.length_var = tk.IntVar(value=16)
        length_spinbox = ttk.Spinbox(length_frame, from_=8, to=64, 
                                     textvariable=self.length_var, width=10)
        length_spinbox.pack(side='left', padx=5)
        
        # Options
        options_frame = ttk.Frame(frame)
        options_frame.pack(pady=10, fill='x')
        
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Uppercase (A-Z)",
                       variable=self.uppercase_var).pack(anchor='w', pady=2)
        ttk.Checkbutton(options_frame, text="Lowercase (a-z)",
                       variable=self.lowercase_var).pack(anchor='w', pady=2)
        ttk.Checkbutton(options_frame, text="Digits (0-9)",
                       variable=self.digits_var).pack(anchor='w', pady=2)
        ttk.Checkbutton(options_frame, text="Special Characters (!@#$%)",
                       variable=self.special_var).pack(anchor='w', pady=2)
        
        # Generated password display
        password_frame = ttk.Frame(frame)
        password_frame.pack(pady=15, fill='x')
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var,
                                   font=('Courier', 12), state='readonly')
        password_entry.pack(fill='x', pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Generate", command=self._generate).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Copy", command=self._copy).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def _generate(self):
        """Generate a new password."""
        password = PasswordGenerator.generate(
            length=self.length_var.get(),
            use_uppercase=self.uppercase_var.get(),
            use_lowercase=self.lowercase_var.get(),
            use_digits=self.digits_var.get(),
            use_special=self.special_var.get()
        )
        
        if password is None:
            messagebox.showerror("Error", "Please select at least one character type")
            return
        
        self.password_var.set(password)
    
    def _copy(self):
        """Copy generated password to clipboard."""
        password = self.password_var.get()
        if password:
            self.copy_callback(password)
            messagebox.showinfo("Success", "Password copied to clipboard")
