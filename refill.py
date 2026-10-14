import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_db
from config import LOW_STOCK_LIMIT


class RefillWindow:
    def __init__(self, root, user_id, user_name):
        self.root = root
        self.user_id = user_id
        self.user_name = user_name
        self.selected_id = None

        self.root.title("Low Stock and Refill")
        self.root.geometry("900x600")
        self.root.config(bg="#f8f9fa")

        self.ui()
        self.load()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def ui(self):
        self.clear()

        nav_frame = tk.Frame(self.root, bg="#f8f9fa")
        nav_frame.pack(fill="x", pady=10)

        tk.Button(
            nav_frame,
            text="⬅ Go to Dashboard",
            width=22,
            bg="#006d77",
            fg="white",
            command=self.back
        ).pack(side="left", padx=20)

        tk.Label(
            self.root,
            text="Low Stock and Refill Management",
            font=("Arial", 23, "bold"),
            bg="#f8f9fa",
            fg="#d62828"
        ).pack(pady=15)

        tk.Label(
            self.root,
            text=f"Medicines with stock less than or equal to {LOW_STOCK_LIMIT}",
            font=("Arial", 12),
            bg="#f8f9fa",
            fg="#333"
        ).pack(pady=5)

        columns = ("ID", "Medicine", "Dose", "Time", "Stock")

        self.table = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            height=12
        )

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=150)

        self.table.pack(pady=15)

        self.table.bind("<ButtonRelease-1>", self.select)

        frame = tk.Frame(self.root, bg="#f8f9fa")
        frame.pack(pady=10)

        tk.Label(
            frame,
            text="Add Stock Quantity",
            bg="#f8f9fa",
            font=("Arial", 11)
        ).grid(row=0, column=0, padx=8)

        self.stock_entry = tk.Entry(frame, width=20)
        self.stock_entry.grid(row=0, column=1, padx=8)

        tk.Button(
            frame,
            text="Refill Stock",
            bg="#006d77",
            fg="white",
            width=15,
            command=self.refill
        ).grid(row=0, column=2, padx=8)

        tk.Button(
            frame,
            text="Refresh",
            bg="#2a9d8f",
            fg="white",
            width=15,
            command=self.load
        ).grid(row=0, column=3, padx=8)

    def load(self):
        for item in self.table.get_children():
            self.table.delete(item)

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
        SELECT id, medicine_name, dose, time, stock
        FROM medicines
        WHERE user_id=? AND active=1 AND stock<=?
        ORDER BY stock ASC
        """, (self.user_id, LOW_STOCK_LIMIT))

        records = cur.fetchall()
        conn.close()

        for row in records:
            self.table.insert("", "end", values=row)

    def select(self, event=None):
        item = self.table.focus()

        if not item:
            return

        values = self.table.item(item, "values")

        if values:
            self.selected_id = values[0]

    def refill(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a medicine first.")
            return

        qty = self.stock_entry.get().strip()

        try:
            qty = int(qty)

        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number.")
            return

        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than zero.")
            return

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
        UPDATE medicines
        SET stock = stock + ?
        WHERE id=? AND user_id=?
        """, (qty, self.selected_id, self.user_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Stock refilled successfully.")

        self.stock_entry.delete(0, tk.END)
        self.selected_id = None

        self.load()

    def back(self):
        from dashboard import DashboardWindow
        DashboardWindow(self.root, self.user_id, self.user_name)