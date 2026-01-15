from PyQt6.QtCore import QObject, pyqtSignal


class CheckIndexWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, out_dir: str, links: list):
        super().__init__()
        self.out_dir = out_dir
        self.links = links

    def run(self) -> None:
        for url in self.links:
            print(f'site:{url}')