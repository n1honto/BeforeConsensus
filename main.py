# main.py
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent))

def main():
    from gui.main_window import DigitalRubleApp
    app = DigitalRubleApp()
    app.mainloop()

if __name__ == "__main__":
    main()
