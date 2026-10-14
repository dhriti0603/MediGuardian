import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_db
from utils import validate_time

class MedicineWindow:
    def __init__(self, root, user_id, user_name):
        self.root = root
        self.user_id = user_id
        self.user_name = user_name
        self.selected_id = None
        self.root.title("Medicine Management")
        self.root.geometry("1120x700")
        self.root.config(bg="#f8f9fa")
        self.create_ui()
        self.load()

    def clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

    def create_ui(self):
        self.clear_root()
        tk.Label(self.root, text="Medicine Management", font=("Arial", 24, "bold"), bg="#f8f9fa", fg="#006d77").pack(pady=12)

        form = tk.Frame(self.root, bg="#f8f9fa")
        form.pack(pady=5)

        fields = [
            ("Medicine Name", "name_entry"),
            ("Dose", "dose_entry"),
            ("Time HH:MM", "time_entry"),
            ("Instruction", "instruction_entry"),
            ("Start Date DD-MM-YYYY", "start_entry"),
            ("End Date DD-MM-YYYY", "end_entry"),
            ("Stock", "stock_entry"),
            ("Notes", "notes_entry"),
        ]

        for i, (label, attr) in enumerate(fields):
            r, c = divmod(i, 2)
            tk.Label(form, text=label, bg="#f8f9fa").grid(row=r, column=c*2, padx=8, pady=5)
            entry = tk.Entry(form, width=30)
            entry.grid(row=r, column=c*2+1, padx=8, pady=5)
            setattr(self, attr, entry)

        tk.Label(form, text="Frequency", bg="#f8f9fa").grid(row=4, column=0, padx=8, pady=5)
        self.frequency_var = tk.StringVar(value="Daily")
        self.frequency_box = ttk.Combobox(form, textvariable=self.frequency_var, values=["Daily", "Weekly", "Monthly"], width=27, state="readonly")
        self.frequency_box.grid(row=4, column=1, padx=8, pady=5)

        btn = tk.Frame(self.root, bg="#f8f9fa")
        btn.pack(pady=8)

        tk.Button(btn, text="Add", width=12, bg="#006d77", fg="white", command=self.add).grid(row=0, column=0, padx=5)
        tk.Button(btn, text="Update", width=12, bg="#2a9d8f", fg="white", command=self.update).grid(row=0, column=1, padx=5)
        tk.Button(btn, text="Delete", width=12, bg="#d62828", fg="white", command=self.delete).grid(row=0, column=2, padx=5)
        tk.Button(btn, text="Clear", width=12, bg="#83c5be", command=self.clear_fields).grid(row=0, column=3, padx=5)
        tk.Button(btn, text="Back", width=12, bg="#555", fg="white", command=self.back).grid(row=0, column=4, padx=5)

        search = tk.Frame(self.root, bg="#f8f9fa")
        search.pack(pady=5)

        tk.Label(search, text="Search", bg="#f8f9fa").grid(row=0, column=0, padx=5)
        self.search_entry = tk.Entry(search, width=38)
        self.search_entry.grid(row=0, column=1, padx=5)
        tk.Button(search, text="Search", bg="#006d77", fg="white", command=self.search).grid(row=0, column=2, padx=5)
        tk.Button(search, text="Show All", bg="#83c5be", command=self.load).grid(row=0, column=3, padx=5)

        columns = ("ID", "Medicine", "Dose", "Time", "Instruction", "Start", "End", "Frequency", "Stock", "Notes")
        self.table = ttk.Treeview(self.root, columns=columns, show="headings", height=13)
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=105)
        self.table.pack(pady=10)
        self.table.bind("<ButtonRelease-1>", self.select)

    def values(self):
        name = self.name_entry.get().strip()
        dose = self.dose_entry.get().strip()
        time_value = self.time_entry.get().strip()
        instruction = self.instruction_entry.get().strip()
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        frequency = self.frequency_var.get()
        stock = self.stock_entry.get().strip() or "0"
        notes = self.notes_entry.get().strip()

        if not name or not dose or not time_value:
            messagebox.showerror("Error", "Medicine name, dose and time are required.")
            return None

        if not validate_time(time_value):
            messagebox.showerror("Error", "Time must be in HH:MM format, for example 08:30.")
            return None

        try:
            stock = int(stock)
        except ValueError:
            messagebox.showerror("Error", "Stock must be a number.")
            return None

        return (name, dose, time_value, instruction, start, end, frequency, stock, notes)

    def add(self):
        vals = self.values()
        if not vals:
            return

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO medicines 
        (user_id, medicine_name, dose, time, instruction, start_date, end_date, frequency, stock, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.user_id, *vals))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Medicine added successfully.")
        self.clear_fields()
        self.load()

    def load(self):
        for item in self.table.get_children():
            self.table.delete(item)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
        SELECT id, medicine_name, dose, time, instruction, start_date, end_date, frequency, stock, notes
        FROM medicines WHERE user_id=? AND active=1
        """, (self.user_id,))
        for row in cur.fetchall():
            self.table.insert("", "end", values=row)
        conn.close()

    def select(self, event=None):
        selected = self.table.focus()
        if not selected:
            return

        values = self.table.item(selected, "values")
        if not values:
            return

        self.clear_fields()
        self.selected_id = values[0]

        entries = [
            self.name_entry, self.dose_entry, self.time_entry, self.instruction_entry,
            self.start_entry, self.end_entry
        ]

        for entry, value in zip(entries, values[1:7]):
            entry.insert(0, value or "")

        self.frequency_var.set(values[7] or "Daily")
        self.stock_entry.insert(0, values[8])
        self.notes_entry.insert(0, values[9] or "")

    def update(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a medicine first.")
            return

        vals = self.values()
        if not vals:
            return

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
        UPDATE medicines
        SET medicine_name=?, dose=?, time=?, instruction=?, start_date=?, end_date=?, frequency=?, stock=?, notes=?
        WHERE id=? AND user_id=?
        """, (*vals, self.selected_id, self.user_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Medicine updated successfully.")
        self.clear_fields()
        self.load()

    def delete(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select a medicine first.")
            return

        if not messagebox.askyesno("Confirm", "Delete selected medicine?"):
            return

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("UPDATE medicines SET active=0 WHERE id=? AND user_id=?", (self.selected_id, self.user_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Medicine deleted.")
        self.clear_fields()
        self.load()

    def search(self):
        keyword = self.search_entry.get().strip()
        for item in self.table.get_children():
            self.table.delete(item)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
        SELECT id, medicine_name, dose, time, instruction, start_date, end_date, frequency, stock, notes
        FROM medicines
        WHERE user_id=? AND active=1 AND medicine_name LIKE ?
        """, (self.user_id, f"%{keyword}%"))

        for row in cur.fetchall():
            self.table.insert("", "end", values=row)

        conn.close()

    def clear_fields(self):
        self.selected_id = None
        for e in [
            self.name_entry, self.dose_entry, self.time_entry, self.instruction_entry,
            self.start_entry, self.end_entry, self.stock_entry, self.notes_entry
        ]:
            e.delete(0, tk.END)
        self.frequency_var.set("Daily")

    def back(self):
        from dashboard import DashboardWindow
        DashboardWindow(self.root, self.user_id, self.user_name)
