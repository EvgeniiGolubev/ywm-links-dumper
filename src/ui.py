import sys
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QPlainTextEdit, QSizePolicy, QTabWidget

from src.check_index_tab import CheckIndexTab
from src.config import Settings
from src.export_links_tab import ExportLinksTab


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

        self.setWindowTitle("SEO Tools")
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon(self.__resource_path("assets/icon.ico")))

        export_links_tab = ExportLinksTab(settings)
        check_index_tab = CheckIndexTab(settings)

        tab = QTabWidget()
        tab.addTab(export_links_tab, 'Выгрузить ссылки из Вебмастера')
        tab.addTab(check_index_tab, 'Проверить индексацию ссылок')

        self.setCentralWidget(tab)

    def __resource_path(self, relative_path: str) -> str:
        if hasattr(sys, '_MEIPASS'):
            # В режиме exe
            return str(Path(sys._MEIPASS) / relative_path)
        else:
            # В режиме разработки
            return str(Path(__file__).parent.parent / relative_path)