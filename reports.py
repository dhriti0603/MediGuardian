import tkinter as tk
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from database import connect_db
import matplotlib.pyplot as plt
import os


class ReportWindow:
    def __init__(self, root, user_id, user_name):
        self.root = root
        self.user_id = user_id
        self.user_name = user_name
        self.root.title("PDF Reports")
        self.root.geometry("700x430")
        self.root.config(bg="#f8f9fa")
        self.ui()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def ui(self):
        self.clear()

        tk.Label(
            self.root,
            text="PDF Report Generator",
            font=("Arial", 24, "bold"),
            bg="#f8f9fa",
            fg="#006d77"
        ).pack(pady=30)

        tk.Label(
            self.root,
            text="Generate report with charts, graphs, history and stock summary.",
            font=("Arial", 14),
            bg="#f8f9fa"
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Generate & Download PDF",
            width=30,
            bg="#006d77",
            fg="white",
            command=self.generate
        ).pack(pady=18)

        tk.Button(
            self.root,
            text="Back to Dashboard",
            width=30,
            bg="#555",
            fg="white",
            command=self.back
        ).pack(pady=8)

    def create_charts(self, taken, skipped, medicines):
        os.makedirs("temp_charts", exist_ok=True)

        pie_path = os.path.join("temp_charts", "adherence_pie.png")
        bar_path = os.path.join("temp_charts", "stock_bar.png")

        # Pie chart
        plt.figure(figsize=(5, 4))
        if taken + skipped > 0:
            plt.pie(
                [taken, skipped],
                labels=["Taken", "Skipped"],
                autopct="%1.1f%%",
                startangle=90
            )
        else:
            plt.text(0.5, 0.5, "No dose history", ha="center", va="center")
        plt.title("Dose Status Distribution")
        plt.tight_layout()
        plt.savefig(pie_path)
        plt.close()

        # Bar chart
        names = [m[0] for m in medicines]
        stocks = [m[3] for m in medicines]

        plt.figure(figsize=(7, 4))
        if names:
            plt.bar(names, stocks)
            plt.xticks(rotation=30, ha="right")
            plt.ylabel("Stock")
        else:
            plt.text(0.5, 0.5, "No medicine stock data", ha="center", va="center")
        plt.title("Medicine Stock Chart")
        plt.tight_layout()
        plt.savefig(bar_path)
        plt.close()

        return pie_path, bar_path

    def generate(self):
        try:
            default_name = f"medicine_report_{self.user_name.replace(' ', '_')}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf"

            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=default_name,
                filetypes=[("PDF Files", "*.pdf")],
                title="Save Medicine Report"
            )

            if not filename:
                return

            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
            SELECT medicine_name, dose, time, stock
            FROM medicines
            WHERE user_id=? AND active=1
            ORDER BY medicine_name
            """, (self.user_id,))
            medicines = cur.fetchall()

            cur.execute("""
            SELECT medicine_name, dose, time, status, date, action_time
            FROM history
            WHERE user_id=?
            ORDER BY id DESC
            """, (self.user_id,))
            history = cur.fetchall()

            conn.close()

            taken = 0
            skipped = 0

            for med, dose, med_time, status, date, action_time in history:
                if status == "Taken":
                    taken += 1
                elif status == "Skipped":
                    skipped += 1

            total = taken + skipped
            adherence = (taken / total * 100) if total else 0

            pie_path, bar_path = self.create_charts(taken, skipped, medicines)

            pdf = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            # Page 1
            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawString(100, height - 50, "Smart Medicine Reminder Report")

            pdf.setFont("Helvetica", 11)
            pdf.drawString(50, height - 85, f"Patient Name: {self.user_name}")
            pdf.drawString(50, height - 105, f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}")

            y = height - 145

            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(50, y, "1. Medicine Stock Summary")
            y -= 25

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(40, y, "Medicine")
            pdf.drawString(200, y, "Dose")
            pdf.drawString(330, y, "Time")
            pdf.drawString(430, y, "Stock")
            y -= 18

            pdf.setFont("Helvetica", 10)

            for med, dose, med_time, stock in medicines:
                if y < 100:
                    pdf.showPage()
                    y = height - 60

                pdf.drawString(40, y, str(med)[:25])
                pdf.drawString(200, y, str(dose)[:18])
                pdf.drawString(330, y, str(med_time))
                pdf.drawString(430, y, str(stock))
                y -= 17

            y -= 30

            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(50, y, "2. Adherence Summary")
            y -= 30

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(70, y, f"Total Taken Doses: {taken}")
            y -= 22
            pdf.drawString(70, y, f"Total Skipped Doses: {skipped}")
            y -= 22
            pdf.drawString(70, y, f"Adherence Percentage: {adherence:.2f}%")

            # Page 2 charts
            pdf.showPage()

            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(70, height - 50, "3. Graphs and Charts")

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(70, height - 90, "Dose Status Distribution")
            pdf.drawImage(pie_path, 80, height - 370, width=430, height=250)

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(70, height - 410, "Medicine Stock Chart")
            pdf.drawImage(bar_path, 60, height - 720, width=480, height=280)

            # Page 3 history
            pdf.showPage()

            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(70, height - 50, "4. Dose History")

            y = height - 85

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(40, y, "Medicine")
            pdf.drawString(170, y, "Dose")
            pdf.drawString(275, y, "Time")
            pdf.drawString(340, y, "Status")
            pdf.drawString(420, y, "Date")
            y -= 18

            pdf.setFont("Helvetica", 10)

            for med, dose, med_time, status, date, action_time in history:
                if y < 70:
                    pdf.showPage()
                    y = height - 60
                    pdf.setFont("Helvetica", 10)

                pdf.drawString(40, y, str(med)[:18])
                pdf.drawString(170, y, str(dose)[:14])
                pdf.drawString(275, y, str(med_time))
                pdf.drawString(340, y, str(status))
                pdf.drawString(420, y, str(date))
                y -= 17

            pdf.save()

            messagebox.showinfo(
                "Success",
                f"PDF with graphs downloaded successfully:\n{filename}"
            )

            try:
                os.startfile(filename)
            except:
                pass

        except Exception as e:
            messagebox.showerror("PDF Error", str(e))

    def back(self):
        from dashboard import DashboardWindow
        DashboardWindow(self.root, self.user_id, self.user_name)