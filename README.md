# Yandex Webmaster External Links Dumper

Инструмент для выгрузки **внешних ссылок** из [Яндекс.Вебмастера](https://webmaster.yandex.ru/) с сохранением в Excel и подсветкой проблемных доменов.

## Возможности

- Авторизация по OAuth-токену.
- Автоматическая выгрузка всех ссылок порциями.
- Сохранение в Excel (.xlsx).
- Автоматическая генерация имени файла по шаблону  
  `<домен>_links_<YYYY-MM-DD>.xlsx`.
- Подсветка строк с "плохими" доменами в `source_url` !Важно! Подсветка работает по простому поиску ключевых слов (например: `porn`, `xxx`, `casino`, `viagra`).

Ограничение API: **анкорные тексты ссылок не выдаются**. Доступны только:
- `source_url` — страница-источник,
- `destination_url` — страница вашего сайта,
- `discovery_date` — дата, когда ссылка впервые обнаружена,
- `source_last_access_date` — дата последней проверки источника.

## Установка

1. Клонируйте репозиторий и создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows

2. Установите зависимости:
    ```bash
    pip install -r requirements.txt

3. Скопируйте .env.example → .env и заполните свои данные:
    ```bash
    YWM_OAUTH_TOKEN=my_token
    YWM_HOST_DOMAIN=example.com
    YWM_LIMIT=100
    YWM_OFFSET=0
    YWM_OUTPUT_DIR=C:/Users/User/Desktop/seo_reports

## Получение OAuth-токена

1. Зарегистрируйте приложение в Яндекс.OAuth
2. В доступах укажите `webmaster:hostinfo`
3. Сформируйте ссылку: 

`https://oauth.yandex.ru/authorize?response_type=token&client_id=MY_CLIENT_ID&scope=webmaster:hostinfo`
4. Перейдите по ней, разрешите доступ, скопируйте токен.

## Запуск
`python src/dump_external_links.py`

После завершения работы скрипт создаст файл:

`<YWM_OUTPUT_DIR>/<домен>_links_<YYYY-MM-DD>.xlsx`
