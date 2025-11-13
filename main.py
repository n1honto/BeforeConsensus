# main.py
import tkinter as tk
from gui.main_window import DigitalRubleApp

def main():
    root = tk.Tk()
    app = DigitalRubleApp(root)

    # Настройка основного окна
    root.geometry("1200x800")
    root.minsize(1000, 700)

    root.mainloop()

if __name__ == "__main__":
    # Создаём необходимые директории
    import os
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    main()
