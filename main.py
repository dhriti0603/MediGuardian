import tkinter as tk
from database import create_tables
from auth import AuthWindow
from config import APP_NAME
from theme import apply_theme


def main():
    create_tables()

    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("1120x700")
    root.resizable(True, True)

    apply_theme(root)

    AuthWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()