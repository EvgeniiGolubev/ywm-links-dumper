from pathlib import Path
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QWidget, QPlainTextEdit, QSizePolicy, QVBoxLayout, QPushButton, QProgressBar, QHBoxLayout, \
    QLabel, QLineEdit, QFileDialog
from src.check_index_worker import CheckIndexWorker
from src.config import Settings


class CheckIndexTab(QWidget):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.out_dir = self.settings.out_dir

        out_dir_label = QLabel("Выберите, где будет располагаться итоговый файл:")
        self.out_dir_field = QLineEdit()
        if self.out_dir:
            self.out_dir_field.setText(self.out_dir)
        field_search_btn = QPushButton("Обзор...")
        field_search_btn.clicked.connect(self.__choose_folder)

        out_dir_hbox = QHBoxLayout()
        out_dir_hbox.addWidget(self.out_dir_field)
        out_dir_hbox.addWidget(field_search_btn)

        links_field_label = QLabel("Добавьте список ссылок в поле ниже:")
        self.links_field = QPlainTextEdit()
        self.links_field.setPlaceholderText("Вставь ссылки по одной на строку...")
        self.links_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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

        layout = QVBoxLayout(self)
        layout.addWidget(out_dir_label)
        layout.addLayout(out_dir_hbox)
        layout.addWidget(links_field_label)
        layout.addWidget(self.links_field)
        layout.addWidget(self.log_field)
        layout.addLayout(run_box)

    def __run(self) -> None:
        self.__add_log("Начинаем работу...")
        self.links_field.setReadOnly(True)
        self.run_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.__save_new_output_dir()

        if not self.__check_out_dir_field():
            self.progress_bar.setVisible(False)
            self.run_button.setEnabled(True)
            return

        self.thread = QThread(self)
        self.worker = CheckIndexWorker(self.out_dir, self.__get_urls_from_field())
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

    def __choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Выбрать папку")
        if folder:
            self.out_dir_field.setText(folder)

    def __save_new_output_dir(self) -> None:
        self.out_dir = self.out_dir_field.text().strip()
        if self.out_dir:
            try:
                self.settings.save("YWM_OUTPUT_DIR", self.out_dir)
            except Exception as e:
                self.__add_log(f"Ошибка в сохранении настроек: {e}")

    def __check_out_dir_field(self) -> bool:
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

        return True

    def __get_urls_from_field(self) -> list[str]:
        raw = self.links_field.toPlainText()
        return raw.splitlines()

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

    def __add_log(self, message: str) -> None:
        self.log_field.appendPlainText(message)