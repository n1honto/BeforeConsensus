from gui.main_window import DigitalRubleApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = DigitalRubleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
