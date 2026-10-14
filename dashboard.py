import tkinter as tk
from database import connect_db
from reminder import ReminderSystem
from config import LOW_STOCK_LIMIT
from theme import (
    BG, SIDEBAR, PRIMARY, PRIMARY_DARK, SECONDARY, DANGER,
    WHITE, TEXT, clear_window, dashboard_card
)



class DashboardWindow:
    def __init__(self, root, user_id, user_name):
        self.root = root
        self.user_id = user_id
        self.user_name = user_name

        self.root.title("Dashboard - MediGuardian")
        self.root.geometry("1120x700")
        self.root.config(bg=BG)

        self.show_dashboard()

        if not hasattr(self.root, "reminder_system"):
            self.root.reminder_system = ReminderSystem(self.root, self.user_id)
            self.root.reminder_system.start()

    def clear(self):
        clear_window(self.root)

    def count(self, query, params=()):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(query, params)
        value = cur.fetchone()[0]
        conn.close()
        return value

    def sidebar(self):
        side = tk.Frame(self.root, bg=SIDEBAR, width=250)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Label(
            side,
            text="💊 MED REMINDER",
            font=("Segoe UI", 17, "bold"),
            bg=SIDEBAR,
            fg=WHITE
        ).pack(pady=28)

        buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("💊 Manage Medicines", self.open_medicine),
            ("📜 History", self.open_history),
            ("📊 Analytics", self.open_analytics),
            ("📄 PDF Reports", self.open_reports),
            ("⚠ Low Stock / Refill", self.open_low_stock),
            ("👤 Profile Settings", self.open_profile),
        ]

        for text, command in buttons:
            tk.Button(
                side,
                text=text,
                command=command,
                bg=SECONDARY,
                fg=TEXT,
                activebackground=PRIMARY,
                activeforeground=WHITE,
                font=("Segoe UI", 11, "bold"),
                width=24,
                height=2,
                bd=0,
                cursor="hand2",
                anchor="w",
                padx=15
            ).pack(pady=6)

        tk.Button(
            side,
            text="🚪 Logout",
            command=self.logout,
            bg=DANGER,
            fg=WHITE,
            activebackground="#9b1d20",
            activeforeground=WHITE,
            font=("Segoe UI", 11, "bold"),
            width=24,
            height=2,
            bd=0,
            cursor="hand2"
        ).pack(pady=25)

    def show_dashboard(self):
        self.clear()
        self.sidebar()

        main = tk.Frame(self.root, bg=BG)
        main.pack(side="right", fill="both", expand=True)

        tk.Label(
            main,
            text=f"Welcome, {self.user_name}",
            font=("Segoe UI", 26, "bold"),
            bg=BG,
            fg=PRIMARY_DARK
        ).pack(pady=(30, 5))

        tk.Label(
            main,
            text="MediGuardian",
            font=("Segoe UI", 15),
            bg=BG,
            fg=TEXT
        ).pack(pady=(0, 20))

        card_frame = tk.Frame(main, bg=BG)
        card_frame.pack(pady=10)

        total = self.count(
            "SELECT COUNT(*) FROM medicines WHERE user_id=? AND active=1",
            (self.user_id,)
        )

        taken = self.count(
            "SELECT COUNT(*) FROM history WHERE user_id=? AND status='Taken'",
            (self.user_id,)
        )

        skipped = self.count(
            "SELECT COUNT(*) FROM history WHERE user_id=? AND status='Skipped'",
            (self.user_id,)
        )

        low = self.count(
            "SELECT COUNT(*) FROM medicines WHERE user_id=? AND stock<=? AND active=1",
            (self.user_id, LOW_STOCK_LIMIT)
        )

        total_doses = taken + skipped
        adherence = (taken / total_doses * 100) if total_doses > 0 else 0

        cards = [
            ("Total Medicines", total, "💊"),
            ("Today's Reminders", total, "⏰"),
            ("Taken Doses", taken, "✅"),
            ("Skipped Doses", skipped, "❌"),
            ("Low Stock", low, "⚠"),
            ("Adherence", f"{adherence:.1f}%", "📈"),
        ]

        for index, (title, value, icon) in enumerate(cards):
            row = index // 3
            col = index % 3
            card = dashboard_card(card_frame, title, value, icon)
            card.grid(row=row, column=col, padx=18, pady=18)

        bottom = tk.Frame(main, bg=WHITE, highlightbackground="#d9e6ea", highlightthickness=1)
        bottom.pack(pady=25, padx=40, fill="x")

        tk.Label(
            bottom,
            text="💡 Health Tip",
            font=("Segoe UI", 14, "bold"),
            bg=WHITE,
            fg=PRIMARY_DARK
        ).pack(anchor="w", padx=20, pady=(15, 5))

        tk.Label(
            bottom,
            text="Take medicines at the same time daily and never skip prescribed doses without consulting your doctor.",
            font=("Segoe UI", 12),
            bg=WHITE,
            fg=TEXT,
            wraplength=750,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))

    def open_medicine(self):
        from medicine import MedicineWindow
        MedicineWindow(self.root, self.user_id, self.user_name)

    def open_history(self):
        from history import HistoryWindow
        HistoryWindow(self.root, self.user_id, self.user_name)

    def open_analytics(self):
        from analytics import AnalyticsWindow
        AnalyticsWindow(self.root, self.user_id, self.user_name)

    def open_reports(self):
        from reports import ReportWindow
        ReportWindow(self.root, self.user_id, self.user_name)

    def open_profile(self):
        from profile_page import ProfileWindow
        ProfileWindow(self.root, self.user_id, self.user_name)

    def open_low_stock(self):
        from refill import RefillWindow
        RefillWindow(self.root, self.user_id, self.user_name)

    def logout(self):
        if hasattr(self.root, "reminder_system"):
            delattr(self.root, "reminder_system")

        from auth import AuthWindow
        AuthWindow(self.root)