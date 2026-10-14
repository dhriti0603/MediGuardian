import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from utils import parse_date, date_range_filter


class HistoryWindow:
    def __init__(self, root, user_id, user_name):
        self.root = root
        self.user_id = user_id
        self.user_name = user_name

        self.root.title("Medicine History")
        self.root.geometry("1000x700")
        self.root.config(bg="#f8f9fa")

        self.create_ui()
        self.load()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def create_ui(self):
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
            text="Medicine History",
            font=("Arial", 24, "bold"),
            bg="#f8f9fa",
            fg="#006d77"
        ).pack(pady=10)

        top = tk.Frame(self.root, bg="#f8f9fa")
        top.pack(pady=5)

        tk.Label(top, text="Filter", bg="#f8f9fa").grid(row=0, column=0, padx=6)

        self.filter_var = tk.StringVar(value="All")
        self.filter_box = ttk.Combobox(
            top,
            textvariable=self.filter_var,
            values=["All", "Daily", "Weekly", "Monthly"],
            state="readonly",
            width=15
        )
        self.filter_box.grid(row=0, column=1, padx=6)

        tk.Button(
            top,
            text="Apply Filter",
            bg="#006d77",
            fg="white",
            command=self.load
        ).grid(row=0, column=2, padx=6)

        tk.Label(
            top,
            text="Search Date",
            bg="#f8f9fa"
        ).grid(row=1, column=0, padx=6, pady=10)

        self.date_entry = tk.Entry(top, width=18)
        self.date_entry.grid(row=1, column=1, padx=6, pady=10)
        self.date_entry.insert(0, "DD-MM-YYYY")

        tk.Button(
            top,
            text="Search by Date",
            bg="#2a9d8f",
            fg="white",
            command=self.search_by_date
        ).grid(row=1, column=2, padx=6, pady=10)

        tk.Button(
            top,
            text="Show All",
            bg="#83c5be",
            command=self.show_all
        ).grid(row=1, column=3, padx=6, pady=10)

        columns = ("Medicine", "Dose", "Time", "Status", "Date", "Action Time")

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

    def clear_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

    def insert_records(self, records):
        self.clear_table()

        for row in records:
            self.table.insert("", "end", values=row)

    def load(self):
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
        SELECT medicine_name, dose, time, status, date, action_time
        FROM history
        WHERE user_id=?
        ORDER BY id DESC
        """, (self.user_id,))

        records = cur.fetchall()
        conn.close()

        mode = self.filter_var.get()

        if mode != "All":
            start, end = date_range_filter(mode)
            start_dt = parse_date(start)
            end_dt = parse_date(end)

            filtered = []

            for record in records:
                try:
                    record_dt = parse_date(record[4])

                    if start_dt <= record_dt <= end_dt:
                        filtered.append(record)

                except Exception:
                    pass

            records = filtered

        self.insert_records(records)

    def search_by_date(self):
        search_date = self.date_entry.get().strip()

        if search_date == "" or search_date == "DD-MM-YYYY":
            messagebox.showerror(
                "Error",
                "Please enter date in DD-MM-YYYY format"
            )
            return

        try:
            parse_date(search_date)
        except Exception:
            messagebox.showerror(
                "Invalid Date",
                "Date format must be DD-MM-YYYY"
            )
            return

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
        SELECT medicine_name, dose, time, status, date, action_time
        FROM history
        WHERE user_id=? AND date=?
        ORDER BY id DESC
        """, (self.user_id, search_date))

        records = cur.fetchall()
        conn.close()

        if not records:
            messagebox.showinfo(
                "No Records",
                f"No history found for {search_date}"
            )

        self.insert_records(records)

    def show_all(self):
        self.filter_var.set("All")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, "DD-MM-YYYY")
        self.load()

    def back(self):
        from dashboard import DashboardWindow
        DashboardWindow(self.root, self.user_id, self.user_name)