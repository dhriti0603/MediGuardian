import tkinter as tk
from tkinter import messagebox
import hashlib
import sqlite3
from database import connect_db


APP_TITLE = "MediGuardian"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class AuthWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("720x680")
        self.root.config(bg="#eaf7f7")
        self.show_login()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def header(self, title, subtitle):
        tk.Label(
            self.root,
            text="💊 MediGuardian",
            font=("Segoe UI", 30, "bold"),
            bg="#eaf7f7",
            fg="#005f73"
        ).pack(pady=(30, 5))

        tk.Label(
            self.root,
            text=subtitle,
            font=("Segoe UI", 13),
            bg="#eaf7f7",
            fg="#1d3557"
        ).pack(pady=(0, 15))

    def styled_label(self, parent, text):
        tk.Label(
            parent,
            text=text,
            bg="white",
            fg="#1d3557",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=50, pady=(8, 2))

    def styled_entry(self, parent, show=None):
        entry = tk.Entry(
            parent,
            width=42,
            show=show if show else "",
            font=("Segoe UI", 11),
            bg="#f8fbfc",
            fg="#1d3557",
            relief="solid",
            bd=1
        )
        entry.pack(pady=4, ipady=6)
        return entry

    def primary_button(self, parent, text, command):
        tk.Button(
            parent,
            text=text,
            width=28,
            height=2,
            bg="#0a9396",
            fg="white",
            activebackground="#005f73",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            cursor="hand2",
            command=command
        ).pack(pady=(18, 8))

    def secondary_button(self, parent, text, command):
        tk.Button(
            parent,
            text=text,
            width=28,
            height=2,
            bg="#94d2bd",
            fg="#1d3557",
            activebackground="#0a9396",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            cursor="hand2",
            command=command
        ).pack(pady=6)

    def card(self):
        box = tk.Frame(
            self.root,
            bg="white",
            bd=0,
            relief="ridge",
            highlightbackground="#cde7e7",
            highlightthickness=2
        )
        box.pack(padx=70, pady=10, fill="both")
        return box

    def show_login(self):
        self.clear()
        self.header(
            "MediGuardian",
            "Smart Medicine Reminder and Dose Monitoring System"
        )

        box = self.card()

        tk.Label(
            box,
            text="Welcome Back",
            font=("Segoe UI", 22, "bold"),
            bg="white",
            fg="#005f73"
        ).pack(pady=(25, 5))

        tk.Label(
            box,
            text="Login to manage your medicines and reminders",
            font=("Segoe UI", 11),
            bg="white",
            fg="#457b9d"
        ).pack(pady=(0, 15))

        self.styled_label(box, "Email Address")
        self.email_entry = self.styled_entry(box)

        self.styled_label(box, "Password")
        self.password_entry = self.styled_entry(box, show="*")

        self.primary_button(box, "Login", self.login)
        self.secondary_button(box, "Create New Account", self.show_register)

        tk.Label(
            box,
            text="Stay on track. Never miss your dose.",
            font=("Segoe UI", 10, "italic"),
            bg="white",
            fg="#6c757d"
        ).pack(pady=(12, 22))

    def show_register(self):
        self.clear()
        self.header(
            "MediGuardian",
            "Create your personal medication care account"
        )

        box = self.card()

        tk.Label(
            box,
            text="Create Account",
            font=("Segoe UI", 22, "bold"),
            bg="white",
            fg="#005f73"
        ).pack(pady=(18, 5))

        fields = [
            ("Full Name", "name_entry", False),
            ("Email Address", "reg_email_entry", False),
            ("Password", "reg_password_entry", True),
            ("Phone Number", "phone_entry", False),
            ("Caregiver Email", "caregiver_entry", False),
        ]

        for label, attr, secret in fields:
            self.styled_label(box, label)
            entry = self.styled_entry(box, show="*" if secret else None)
            setattr(self, attr, entry)

        self.primary_button(box, "Register", self.register)
        self.secondary_button(box, "Back to Login", self.show_login)

    def register(self):
        name = self.name_entry.get().strip()
        email = self.reg_email_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        phone = self.phone_entry.get().strip()
        caregiver = self.caregiver_entry.get().strip()

        if not name or not email or not password:
            messagebox.showerror("Error", "Name, email and password are required.")
            return

        if "@" not in email:
            messagebox.showerror("Error", "Enter a valid email address.")
            return

        conn = connect_db()
        cur = conn.cursor()

        try:
            cur.execute("""
            INSERT INTO users (name, email, password, phone, caregiver_email)
            VALUES (?, ?, ?, ?, ?)
            """, (name, email, hash_password(password), phone, caregiver))

            conn.commit()
            messagebox.showinfo("Success", "Registration successful. Please login.")
            self.show_login()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists.")

        finally:
            conn.close()

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "Email and password are required.")
            return

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, name FROM users WHERE email=? AND password=?",
            (email, hash_password(password))
        )

        user = cur.fetchone()
        conn.close()

        if user:
            from dashboard import DashboardWindow
            DashboardWindow(self.root, user[0], user[1])
        else:
            messagebox.showerror("Error", "Invalid email or password.")