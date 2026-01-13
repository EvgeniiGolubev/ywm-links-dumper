from pathlib import Path
from urllib.parse import urlparse
from PyQt6.QtCore import QThread, Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, \
    QFileDialog, QHBoxLayout, QPlainTextEdit, QSizePolicy, QProgressBar
from src.config import Settings
from src.export_links_worker import ExportLinksWorker


class ExportLinksTab(QWidget):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.oauth_token = self.settings.oauth_token
        self.out_dir = self.settings.out_dir
        self.host_domain = self.settings.host_domain
        self.limit = self.settings.limit
        self.offset = self.settings.offset

        out_dir_label = QLabel("Выберите, где будет располагаться итоговый файл:")
        self.out_dir_field = QLineEdit()
        if self.out_dir:
            self.out_dir_field.setText(self.out_dir)
        field_search_btn = QPushButton("Обзор...")
        field_search_btn.clicked.connect(self.__choose_folder)

        out_dir_hbox = QHBoxLayout()
        out_dir_hbox.addWidget(self.out_dir_field)
        out_dir_hbox.addWidget(field_search_btn)

        token_label = QLabel("Введите ваш oauth токен из Вебмастера:")
        self.token_field = QLineEdit()
        self.token_field.setPlaceholderText("Введите токен здесь...")
        if self.oauth_token:
            self.token_field.setText(self.oauth_token)

        host_domain_label = QLabel("Введите домен сайта, подключенного в Вебмастере (пример: domain.com):")
        self.host_domain_field = QLineEdit()
        self.host_domain_field.setPlaceholderText("Введите домен здесь...")
        if self.host_domain:
            self.host_domain_field.setText(self.host_domain)

        self.log_field = QPlainTextEdit()
        self.log_field.setReadOnly(True)
        self.log_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.run_button = QPushButton("Запустить")
        self.run_button.setMaximumWidth(120)
        self.run_button.setMinimumHeight(30)
        self.run_button.clicked.connect(self.__run)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(250)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)

        self.progress_bar.setStyleSheet("""
        QProgressBar {
            border: 1px solid #3A3A3A;
            border-radius: 3px;
            background-color: rgba(255, 255, 255, 0.05);
        }
        QProgressBar::chunk {
            background-color: #0078D7;
            border-radius: 2px;
        }
        """)

        run_box = QHBoxLayout()
        run_box.setAlignment(Qt.AlignmentFlag.AlignLeft)
        run_box.addWidget(self.run_button)
        run_box.addWidget(self.progress_bar)

        vbox = QVBoxLayout(self)
        vbox.addWidget(out_dir_label)
        vbox.addLayout(out_dir_hbox)
        vbox.addWidget(token_label)
        vbox.addWidget(self.token_field)
        vbox.addWidget(host_domain_label)
        vbox.addWidget(self.host_domain_field)
        vbox.addWidget(self.log_field)
        vbox.addLayout(run_box)

    def __choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Выбрать папку")
        if folder:
            self.out_dir_field.setText(folder)

    def __run(self) -> None:
        self.__add_log("Начинаем работу...")
        self.run_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.__save_new_data()

        if not self.__check_fields():
            self.progress_bar.setVisible(False)
            self.run_button.setEnabled(True)
            return

        self.thread = QThread(self)
        self.worker = ExportLinksWorker(self.oauth_token, self.out_dir, self.host_domain, self.limit, self.offset)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.__add_log)
        self.worker.finished.connect(self.__on_worker_finished)
        self.worker.error.connect(self.__on_worker_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def __save_new_data(self) -> None:
        self.oauth_token = self.token_field.text().strip()
        if self.oauth_token:
            self.__save_setting("YWM_OAUTH_TOKEN", self.oauth_token)

        self.out_dir = self.out_dir_field.text().strip()
        if self.out_dir:
            self.__save_setting("YWM_OUTPUT_DIR", self.out_dir)

        raw_host = self.host_domain_field.text().strip()
        self.host_domain = self.__extract_domain(raw_host)
        if self.host_domain:
            self.__save_setting("YWM_HOST_DOMAIN", self.host_domain)

    def __extract_domain(self, value: str) -> str:
        value = value.strip()

        if not value.startswith(("http://", "https://")):
            value = "http://" + value

        parsed = urlparse(value)
        domain = parsed.netloc or parsed.path

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    def __save_setting(self, key: str, value: str) -> None:
        try:
            self.settings.save(key, value)
        except Exception as e:
            self.__add_log(f"Ошибка в сохранении настроек: {e}")

    def __add_log(self, message: str) -> None:
        self.log_field.appendPlainText(message)

    def __check_fields(self) -> bool:
        if not self.out_dir:
            self.__add_log("Не задан путь к итоговому файлу!")
            self.progress_bar.setVisible(False)
            self.run_button.setEnabled(True)
            return False

        try:
            p = Path(self.out_dir).expanduser()
            if not p.exists():
                self.__add_log(f"Папка не существует: {p}")
                return False
            if not p.is_dir():
                self.__add_log(f"Указан не каталог: {p}")
                return False
        except Exception as e:
            self.__add_log(f"Нет доступа к каталогу '{self.out_dir}': {e}")
            return False

        if not self.oauth_token:
            self.__add_log("Не задан oauth токен из Вебмастера!")
            return False

        if not self.host_domain:
            self.__add_log("Не задан домен сайта!")
            return False

        return True

    def __on_worker_finished(self, msg: str) -> None:
        self.__add_log(msg)
        self.__add_log("Работа завершена!")
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.__add_log("\n")

    def __on_worker_error(self, msg: str) -> None:
        self.__add_log(msg)
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.__add_log("\n")