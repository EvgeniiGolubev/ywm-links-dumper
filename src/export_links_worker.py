from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from src.api import YWMClient
from src.utils import write_xlsx

class ExportLinksWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, oauth_token: Optional[str], out_dir: str, host_domain: Optional[str],
                 limit: int, offset: int):
        super().__init__()

        self.oauth_token = oauth_token
        self.out_dir = out_dir
        self.host_domain = host_domain
        self.limit = limit
        self.offset = offset

    def run(self) -> None:
        try:
            api = YWMClient(self.oauth_token)

            self.log.emit("Получаем user_id...")
            user_id = api.get_user_id()
            if user_id == -1:
                self.error.emit("Не удалось получить user_id!")
                return

            self.log.emit(f"OK: user_id = {user_id}")

            self.log.emit("Получаем host_id...")
            host_id = api.find_host_id(user_id, self.host_domain)
            if not host_id:
                self.error.emit(f"Хост с доменом '{self.host_domain}' не найден в вашем аккаунте Вебмастера!")
                return

            self.log.emit(f"OK: host_id = {host_id}")

            self.log.emit(f"Выгружаем внешние ссылки: user_id={user_id} host_id={host_id} limit={self.limit} offset={self.offset}")
            rows = list(api.iter_external_links(user_id, host_id, self.limit, self.offset))

            if not rows:
                self.log.emit("Ссылок не найдено.")
                self.finished.emit("Выгрузка завершена без данных.")
                return

            result = write_xlsx(rows, self.out_dir, self.host_domain)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))