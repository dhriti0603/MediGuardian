import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import winsound

from database import connect_db, get_user_email
from notifications import send_email
from config import LOW_STOCK_LIMIT, SNOOZE_MINUTES, REMINDER_CHECK_SECONDS
from utils import today_str, now_full_str


class ReminderSystem:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.reminded = set()
        self.active_popups = set()
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.check()

    def check(self):
        current_time = datetime.now().strftime("%H:%M")
        today = today_str()

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, medicine_name, dose, time, instruction, stock
        FROM medicines
        WHERE user_id=? AND time=? AND active=1
        """, (self.user_id, current_time))

        medicines = cursor.fetchall()
        conn.close()

        for medicine in medicines:
            medicine_id = medicine[0]
            reminder_key = f"{medicine_id}-{today}-{current_time}"

            if reminder_key not in self.reminded:
                self.reminded.add(reminder_key)
                self.show_notification(medicine)

        self.root.after(REMINDER_CHECK_SECONDS * 1000, self.check)

    def play_alarm(self):
        try:
            for _ in range(3):
                winsound.Beep(1200, 700)
                winsound.Beep(900, 500)
        except Exception:
            print("\a")

    def show_notification(self, medicine):
        medicine_id, name, dose, med_time, instruction, stock = medicine

        if medicine_id in self.active_popups:
            return

        self.active_popups.add(medicine_id)

        self.play_alarm()

        popup = tk.Toplevel(self.root)
        popup.title("Dose Reminder")
        popup.geometry("470x420")
        popup.config(bg="#fff3cd")
        popup.grab_set()

        def close_popup():
            self.active_popups.discard(medicine_id)
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", close_popup)

        tk.Label(
            popup,
            text="⏰ Dose Reminder",
            font=("Arial", 22, "bold"),
            bg="#fff3cd",
            fg="#d62828"
        ).pack(pady=15)

        tk.Label(
            popup,
            text="It is time to take your medicine",
            font=("Arial", 14, "bold"),
            bg="#fff3cd",
            fg="#333"
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Medicine: {name}",
            font=("Arial", 15, "bold"),
            bg="#fff3cd"
        ).pack(pady=6)

        tk.Label(
            popup,
            text=f"Dose: {dose}",
            font=("Arial", 14),
            bg="#fff3cd"
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Scheduled Time: {med_time}",
            font=("Arial", 14),
            bg="#fff3cd"
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Instruction: {instruction}",
            font=("Arial", 13),
            bg="#fff3cd",
            wraplength=390
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Stock Left: {stock}",
            font=("Arial", 13, "bold"),
            bg="#fff3cd",
            fg="#006d77"
        ).pack(pady=5)

        button_frame = tk.Frame(popup, bg="#fff3cd")
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Taken",
            width=11,
            bg="#2a9d8f",
            fg="white",
            command=lambda: self.save_status(
                popup, medicine_id, name, dose, med_time, "Taken"
            )
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            button_frame,
            text="Skip",
            width=11,
            bg="#f4a261",
            fg="white",
            command=lambda: self.save_status(
                popup, medicine_id, name, dose, med_time, "Skipped"
            )
        ).grid(row=0, column=1, padx=6)

        tk.Button(
            button_frame,
            text="Snooze",
            width=11,
            bg="#457b9d",
            fg="white",
            command=lambda: self.snooze(popup, medicine)
        ).grid(row=0, column=2, padx=6)

    def save_status(self, popup, medicine_id, name, dose, med_time, status):
        date = today_str()

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO history 
        (user_id, medicine_id, medicine_name, dose, time, status, date, action_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.user_id,
            medicine_id,
            name,
            dose,
            med_time,
            status,
            date,
            now_full_str()
        ))

        if status == "Taken":
            cursor.execute("""
            UPDATE medicines
            SET stock = CASE 
                WHEN stock > 0 THEN stock - 1 
                ELSE 0 
            END
            WHERE id=? AND user_id=?
            """, (medicine_id, self.user_id))

            cursor.execute("""
            SELECT stock 
            FROM medicines
            WHERE id=? AND user_id=?
            """, (medicine_id, self.user_id))

            stock_data = cursor.fetchone()

            if stock_data and stock_data[0] <= LOW_STOCK_LIMIT:
                caregiver_email = get_user_email(self.user_id)

                if caregiver_email:
                    send_email(
                        caregiver_email,
                        "Low Medicine Stock Alert",
                        f"{name} stock is low. Remaining tablets: {stock_data[0]}"
                    )

        if status == "Skipped":
            caregiver_email = get_user_email(self.user_id)

            if caregiver_email:
                send_email(
                    caregiver_email,
                    "Missed Dose Alert",
                    f"The patient skipped medicine.\n\nMedicine: {name}\nDose: {dose}\nTime: {med_time}"
                )

        conn.commit()
        conn.close()

        self.active_popups.discard(medicine_id)

        popup.destroy()
        messagebox.showinfo("Saved", f"Medicine marked as {status}")

    def snooze(self, popup, medicine):
        medicine_id = medicine[0]

        self.active_popups.discard(medicine_id)

        popup.destroy()

        messagebox.showinfo(
            "Snoozed",
            f"Reminder snoozed for {SNOOZE_MINUTES} minutes"
        )

        self.root.after(
            SNOOZE_MINUTES * 60 * 1000,
            lambda: self.show_notification(medicine)
        )