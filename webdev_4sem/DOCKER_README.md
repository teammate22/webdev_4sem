# Запуск Ridee через Docker

## Как собрать проект

Выполните команду из папки проекта, где лежит `docker-compose.yml`:

```powershell
docker compose build
```

## Как запустить проект

```powershell
docker compose up --build
```

После запуска сайт будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

## Как применить миграции

При обычном запуске миграции применяются автоматически перед стартом сервера.

Если нужно выполнить миграции вручную:

```powershell
docker compose exec django python manage.py migrate
```

## Как создать суперпользователя

Запустите контейнеры:

```powershell
docker compose up --build
```

В отдельном терминале выполните:

```powershell
docker compose exec django python manage.py createsuperuser
```

## Как заполнить базу демонстрационными данными

После запуска контейнеров выполните:

```powershell
docker compose exec django python manage.py seed_demo_data
```

Команда создаёт клиентов, водителей, тарифы, услуги, заказы, оплаты и отзывы. Если нужно пересоздать демо-данные заново:

```powershell
docker compose exec django python manage.py seed_demo_data --reset
```

## Где хранятся данные

В `docker-compose.yml` настроены два volume:

- `sqlite_data` — файл SQLite-базы `/app/data/db.sqlite3`.
- `media_data` — загруженные файлы `/app/media`.

Админка Django доступна по адресу:

```text
http://127.0.0.1:8000/admin/
```
