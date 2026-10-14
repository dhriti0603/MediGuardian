import tkinter as tk
from tkinter import messagebox
from database import connect_db

class ProfileWindow:
    def __init__(self, root, user_id, user_name):
        self.root = root
        self.user_id = user_id
        self.user_name = user_name
        self.root.title("Profile Settings")
        self.root.geometry("700x520")
        self.root.config(bg="#f8f9fa")
        self.ui()
        self.load()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def ui(self):
        self.clear()

        tk.Label(self.root, text="Profile Settings", font=("Arial", 24, "bold"), bg="#f8f9fa", fg="#006d77").pack(pady=25)

        frame = tk.Frame(self.root, bg="#f8f9fa")
        frame.pack(pady=10)

        fields = [
            ("Name", "name_entry"),
            ("Email", "email_entry"),
            ("Phone", "phone_entry"),
            ("Caregiver Email", "caregiver_entry"),
        ]

        for i, (label, attr) in enumerate(fields):
            tk.Label(frame, text=label, bg="#f8f9fa").grid(row=i, column=0, padx=10, pady=9)
            entry = tk.Entry(frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=9)
            setattr(self, attr, entry)

        tk.Button(self.root, text="Update Profile", width=25, bg="#006d77", fg="white", command=self.update).pack(pady=16)
        tk.Button(self.root, text="Back to Dashboard", width=25, bg="#555", fg="white", command=self.back).pack(pady=5)

    def load(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT name, email, phone, caregiver_email FROM users WHERE id=?", (self.user_id,))
        user = cur.fetchone()
        conn.close()

        if user:
            for entry, value in zip([self.name_entry, self.email_entry, self.phone_entry, self.caregiver_entry], user):
                entry.insert(0, value or "")

    def update(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        caregiver = self.caregiver_entry.get().strip()

        if not name or not email:
            messagebox.showerror("Error", "Name and email are required.")
            return

        conn = connect_db()
        cur = conn.cursor()

        try:
            cur.execute("""
            UPDATE users
            SET name=?, email=?, phone=?, caregiver_email=?
            WHERE id=?
            """, (name, email, phone, caregiver, self.user_id))
            conn.commit()
            self.user_name = name
            messagebox.showinfo("Success", "Profile updated successfully.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            conn.close()

    def back(self):
        from dashboard import DashboardWindow
        DashboardWindow(self.root, self.user_id, self.user_name)
