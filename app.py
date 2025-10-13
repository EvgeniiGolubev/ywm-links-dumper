import sys
from PyQt6.QtWidgets import QApplication
from src.config import Settings
from src.ui import MainWindow


def main():
    settings = Settings()
    app = QApplication(sys.argv)
    app.setApplicationName("YWM External Links")
    win = MainWindow(settings)
    win.show()
    app.exec()

if __name__ == "__main__":
    main()