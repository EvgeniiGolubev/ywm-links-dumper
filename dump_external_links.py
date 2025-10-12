import sys
from PyQt6.QtWidgets import QApplication
from src.config import Settings
from src.ui import MainWindow


def main():
    s = Settings()
    app = QApplication(sys.argv)
    win = MainWindow(s.oauth_token, s.output_dir, s.host_domain, s.limit, s.offset)
    win.show()
    app.exec()

if __name__ == "__main__":
    main()