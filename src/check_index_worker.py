import time
from urllib.parse import quote
from PyQt6.QtCore import QObject, pyqtSignal
from playwright.sync_api import sync_playwright
from src.utils import write_indexation_xlsx


class CheckIndexWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, out_dir: str, links: list):
        super().__init__()
        self.out_dir = out_dir
        self.links = [x.strip() for x in links if x.strip()]
        self._is_running = True
        self.profile_dir = "pw_profile"
        self.timeout_ms = 25000
        self.max_attempts_per_url = 2
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    def run(self) -> None:
        try:
            if not self.links:
                self.error.emit("Список ссылок пуст.")
                return

            rows = []

            with sync_playwright() as p:
                self.context_headless = self.__open_context(p, headless=True)
                self.page_headless = self.context_headless.new_page()

                for i, url in enumerate(self.links, start=1):
                    if not self._is_running:
                        self.log.emit("Остановлено пользователем")
                        break

                    self.log.emit(f"[{i}/{len(self.links)}] {url}")

                    google_indexed = self.__check_google(p, url)
                    yandex_indexed = self.__check_yandex(p, url)

                    rows.append({
                        "url": url,
                        "google_index": "да" if google_indexed else "нет",
                        "yandex_index": "да" if yandex_indexed else "нет",
                    })

                    time.sleep(1)

                self.context_headless.close()

            result_msg = write_indexation_xlsx(rows, self.out_dir)
            self.log.emit(result_msg)
            self.finished.emit("Проверка успешно завершена!")
        except Exception as e:
            self.error.emit(f"Ошибка в run: {str(e)}")

    def __check_google(self, p, url: str) -> bool:
        search_url = self.__build_search_url(url)
        attempt = 0

        while attempt < self.max_attempts_per_url:
            html = self.__query_search(search_url)
            if html is None:
                if attempt >= 1:
                    self.log.emit("Капча не пройдена повторно, пропускаем URL.")
                    return False

                self.__solve_captcha_in_visible_browser(p, search_url)
                attempt += 1
                continue

            if html is False:
                attempt += 1
                time.sleep(2)
                continue

            return self.__parse_indexed_google(html)

        return False

    def __check_yandex(self, p, url: str) -> bool:
        search_url = f"https://yandex.ru/search/?text=\"{quote(url)}\""
        attempt = 0

        while attempt < self.max_attempts_per_url:
            html = self.__query_search(search_url)

            if html is None:  # Капча
                if attempt >= 1: return False
                self.__solve_captcha_in_visible_browser(p, search_url)
                attempt += 1
                continue

            if html is False:
                attempt += 1
                continue

            h = html.lower()

            if "ничего не нашлось" in h or "не найден" in h:
                return False

            if any(x in h for x in ["serp-item", "organic", "path", "favicons"]):
                return True

            attempt += 1
            time.sleep(1)

        return False

    def __is_captcha(self, page) -> bool:
        url = (page.url or "").lower()
        if "/sorry/" in url:
            return True

        try:
            captcha_form = page.query_selector("#captcha-form")
            recaptcha_frame = page.query_selector("iframe[src*='recaptcha']")

            if captcha_form or recaptcha_frame:
                return True
        except:
            pass
        return False

    def __parse_indexed_google(self, html: str) -> bool:
        h = html.lower()

        if "did not match any documents" in h or "ничего не найдено" in h:
            return False

        if 'id="search"' in h or 'id="rso"' in h or 'id="result-stats"' in h:
            return True
        return False

    def __query_search(self, search_url: str) -> str:
        page = self.page_headless

        try:
            page.goto("about:blank")
            page.goto(
                search_url,
                timeout=self.timeout_ms,
                wait_until="domcontentloaded"
            )

            try:
                page.wait_for_load_state("networkidle", timeout=6000)
            except:
                pass

            if self.__is_captcha(page):
                return None

            for _ in range(2):
                try:
                    return page.content()
                except:
                    page.wait_for_timeout(200)

            return False
        except Exception as e:
            self.log.emit(f"Ошибка загрузки страницы: {e}")
            return False

    def __solve_captcha_in_visible_browser(self, p, search_url: str) -> None:
        self.log.emit("!!! ОБНАРУЖЕНА КАПЧА !!!")
        self.log.emit("Закрываю фоновый поток и открываю окно...")

        if self.context_headless:
            self.context_headless.close()

        context = self.__open_context(p, headless=False)
        page = context.new_page()
        try:
            page.goto(search_url, timeout=60000)
            self.log.emit("Жду, пока вы решите капчу и закроете браузер...")
            page.wait_for_event("close", timeout=300000)
        except Exception as e:
            self.log.emit(f"Окно закрыто или возникла ошибка: {e}")
        finally:
            context.close()

        self.log.emit("Возобновляю фоновую работу...")
        self.context_headless = self.__open_context(p, headless=True)
        self.page_headless = self.context_headless.new_page()

    def __open_context(self, p, headless: bool):
        return p.chromium.launch_persistent_context(
            user_data_dir=self.profile_dir,
            headless=headless,
            user_agent=self.user_agent,
            locale="ru-RU",
            args=["--disable-blink-features=AutomationControlled"]
        )

    def __build_search_url(self, url: str) -> str:
        return f"https://www.google.com/search?q=site:{quote(url)}&hl=ru"