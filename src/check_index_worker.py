from PyQt6.QtCore import QObject, pyqtSignal


class CheckIndexWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, out_dir: str):
        super().__init__()
        self.out_dir = out_dir

    def run(self) -> None:
        print(self.out_dir)