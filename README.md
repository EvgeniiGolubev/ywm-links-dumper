# Yandex Webmaster External Links Dumper

Инструмент для выгрузки внешних ссылок из [Яндекс.Вебмастера](https://webmaster.yandex.ru/) с сохранением в Excel и подсветкой проблемных доменов.
Теперь доступна удобная графическая оболочка с поддержкой сборки в `.exe` файл через PyInstaller.

## Основные функции

- Авторизация по OAuth-токену.
- Автоматическая выгрузка всех ссылок порциями.
- Сохранение в Excel (.xlsx).
- Автоматическая генерация имени файла по шаблону `<домен>_links_<YYYY-MM-DD>.xlsx`.
- Подсветка строк с "плохими" доменами в `source_url` **!Важно!** Подсветка работает по простому поиску ключевых слов (например: `porn`, `xxx`, `casino`, `viagra`).
- Графический интерфейс.
- Возможность сборки в `.exe`
- Автоматическое сохранение настроек в `Документах` пользователя (OAuth-токен, домен, путь вывода и лимиты выгрузки).

Ограничение API: **анкорные тексты ссылок не выдаются**. Доступны только:
- `source_url` — страница-источник,
- `destination_url` — страница вашего сайта,
- `discovery_date` — дата, когда ссылка впервые обнаружена,
- `source_last_access_date` — дата последней проверки источника.

## Установка (для разработки)

1. Клонируйте репозиторий и создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows

2. Установите зависимости:
    ```bash
    pip install -r requirements.txt

## Получение OAuth-токена

1. Зарегистрируйте приложение в Яндекс.OAuth
2. В доступах укажите `webmaster:hostinfo`
3. Сформируйте ссылку:
`https://oauth.yandex.ru/authorize?response_type=token&client_id=MY_CLIENT_ID&scope=webmaster:hostinfo`
4. Перейдите по ней, разрешите доступ, скопируйте токен.

## Запуск
1. В режиме Python: `python app.py`
2. В виде собранного `.exe`: `dist/YWM_ExternalLinks.exe`
3. После завершения работы скрипт создаст файл: `<YWM_OUTPUT_DIR>/<домен>_links_<YYYY-MM-DD>.xlsx`
4. Настройки будут автоматически сохранены в: `C:\Users\<Имя>\Documents\YWM_ExternalLinks\settings.ini`

## Сборка в .exe
```bash
pyinstaller --noconsole --onefile --name YWM_ExternalLinks --icon=assets/icon.ico --add-data "assets/icon.ico;assets" app.py
