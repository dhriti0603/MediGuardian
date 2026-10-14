import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from database import connect_db

class AnalyticsWindow:
    def __init__(self, root, user_id, user_name):
        self.root = root
        self.user_id = user_id
        self.user_name = user_name
        self.root.title("Analytics")
        self.root.geometry("820x530")
        self.root.config(bg="#f8f9fa")
        self.ui()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def counts(self):
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM history WHERE user_id=? AND status='Taken'", (self.user_id,))
        taken = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM history WHERE user_id=? AND status='Skipped'", (self.user_id,))
        skipped = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM medicines WHERE user_id=? AND active=1", (self.user_id,))
        medicines = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM medicines WHERE user_id=? AND active=1 AND stock<=5", (self.user_id,))
        low = cur.fetchone()[0]

        conn.close()
        return taken, skipped, medicines, low

    def ui(self):
        self.clear()

        taken, skipped, medicines, low = self.counts()
        total = taken + skipped
        adherence = (taken / total * 100) if total else 0

        tk.Label(self.root, text="Analytics Dashboard", font=("Arial", 24, "bold"), bg="#f8f9fa", fg="#006d77").pack(pady=25)

        frame = tk.Frame(self.root, bg="#f8f9fa")
        frame.pack(pady=20)

        self.card(frame, "Medicines", medicines, 0, 0)
        self.card(frame, "Taken", taken, 0, 1)
        self.card(frame, "Skipped", skipped, 0, 2)
        self.card(frame, "Adherence", f"{adherence:.2f}%", 1, 0)
        self.card(frame, "Low Stock", low, 1, 1)

        tk.Button(self.root, text="Show Adherence Pie Chart", width=28, bg="#006d77", fg="white", command=self.pie).pack(pady=6)
        tk.Button(self.root, text="Show Status Bar Chart", width=28, bg="#2a9d8f", fg="white", command=self.bar).pack(pady=6)
        tk.Button(self.root, text="Back to Dashboard", width=28, bg="#555", fg="white", command=self.back).pack(pady=6)

    def card(self, parent, title, value, row, col):
        box = tk.Frame(parent, bg="white", width=180, height=105, relief="raised", bd=2)
        box.grid(row=row, column=col, padx=12, pady=10)
        box.pack_propagate(False)
        tk.Label(box, text=title, bg="white", fg="#006d77", font=("Arial", 12, "bold")).pack(pady=12)
        tk.Label(box, text=str(value), bg="white", font=("Arial", 22, "bold")).pack()

    def pie(self):
        taken, skipped, _, _ = self.counts()
        if taken + skipped == 0:
            messagebox.showinfo("No Data", "No history available.")
            return

        plt.figure(figsize=(6, 6))
        plt.pie([taken, skipped], labels=["Taken", "Skipped"], autopct="%1.1f%%")
        plt.title("Medicine Adherence")
        plt.show()

    def bar(self):
        taken, skipped, medicines, low = self.counts()
        plt.figure(figsize=(8, 5))
        plt.bar(["Medicines", "Taken", "Skipped", "Low Stock"], [medicines, taken, skipped, low])
        plt.xlabel("Category")
        plt.ylabel("Count")
        plt.title("Medicine Reminder Statistics")
        plt.show()

    def back(self):
        from dashboard import DashboardWindow
        DashboardWindow(self.root, self.user_id, self.user_name)
