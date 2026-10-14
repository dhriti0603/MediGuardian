import tkinter as tk
from tkinter import ttk

BG = "#f4f9fb"
SIDEBAR = "#005f73"
PRIMARY = "#0a9396"
PRIMARY_DARK = "#005f73"
SECONDARY = "#94d2bd"
DANGER = "#d62828"
WARNING = "#ee9b00"
CARD = "#ffffff"
TEXT = "#1d3557"
WHITE = "#ffffff"
BORDER = "#d9e6ea"

FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_SUBTITLE = ("Segoe UI", 14)
FONT_TEXT = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 11, "bold")


def apply_theme(root):
    root.configure(bg=BG)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=WHITE,
        foreground=TEXT,
        rowheight=32,
        fieldbackground=WHITE,
        font=FONT_TEXT,
        borderwidth=0
    )

    style.configure(
        "Treeview.Heading",
        background=PRIMARY,
        foreground=WHITE,
        font=("Segoe UI", 11, "bold")
    )

    style.map(
        "Treeview",
        background=[("selected", SECONDARY)]
    )


def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()


def heading(parent, text):
    return tk.Label(
        parent,
        text=text,
        bg=BG,
        fg=PRIMARY_DARK,
        font=FONT_TITLE
    )


def subheading(parent, text):
    return tk.Label(
        parent,
        text=text,
        bg=BG,
        fg=TEXT,
        font=FONT_SUBTITLE
    )


def normal_label(parent, text, bg=BG):
    return tk.Label(
        parent,
        text=text,
        bg=bg,
        fg=TEXT,
        font=FONT_TEXT
    )


def primary_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=PRIMARY,
        fg=WHITE,
        activebackground=PRIMARY_DARK,
        activeforeground=WHITE,
        font=FONT_BUTTON,
        width=24,
        height=2,
        bd=0,
        cursor="hand2"
    )


def secondary_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=SECONDARY,
        fg=TEXT,
        activebackground=PRIMARY,
        activeforeground=WHITE,
        font=FONT_BUTTON,
        width=24,
        height=2,
        bd=0,
        cursor="hand2"
    )


def danger_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=DANGER,
        fg=WHITE,
        activebackground="#9b1d20",
        activeforeground=WHITE,
        font=FONT_BUTTON,
        width=24,
        height=2,
        bd=0,
        cursor="hand2"
    )


def small_button(parent, text, command, color=PRIMARY):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=WHITE,
        activebackground=PRIMARY_DARK,
        activeforeground=WHITE,
        font=("Segoe UI", 10, "bold"),
        width=14,
        bd=0,
        cursor="hand2",
        padx=5,
        pady=5
    )


def dashboard_card(parent, title, value, icon=""):
    box = tk.Frame(
        parent,
        bg=CARD,
        width=210,
        height=130,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    box.pack_propagate(False)

    tk.Label(
        box,
        text=icon,
        bg=CARD,
        fg=PRIMARY,
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(12, 0))

    tk.Label(
        box,
        text=title,
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 12, "bold")
    ).pack(pady=(5, 0))

    tk.Label(
        box,
        text=str(value),
        bg=CARD,
        fg=PRIMARY_DARK,
        font=("Segoe UI", 26, "bold")
    ).pack()

    return box