# Celery в проекте Ridee

## Как запускается worker

В Docker worker запускается отдельным сервисом `celery_worker`:

```powershell
docker compose up --build celery_worker
```

При полном запуске проекта worker стартует вместе с остальными сервисами:

```powershell
docker compose up --build
```

Команда внутри контейнера:

```text
celery -A webdev_4sem worker --loglevel=info
```

## Как запускается beat

Celery beat запускается отдельным сервисом `celery_beat`:

```powershell
docker compose up --build celery_beat
```

Команда внутри контейнера:

```text
celery -A webdev_4sem beat --loglevel=info
```

Beat использует расписание из `CELERY_BEAT_SCHEDULE` в `webdev_4sem/settings.py`.

## Периодическая задача

Задача:

```text
core.tasks.recalculate_driver_ratings
```

Она ежедневно пересчитывает `Driver.rating` по средней оценке отзывов заказов водителя.

Расписание:

```text
каждый день в 03:00 по TIME_ZONE проекта
```

## Как проверить выполнение задачи

Запустите Redis, Django, worker и beat:

```powershell
docker compose up --build
```

Для ручной проверки можно вызвать задачу из Django shell:

```powershell
docker compose exec django python manage.py shell -c "from core.tasks import recalculate_driver_ratings; print(recalculate_driver_ratings())"
```

В логах `celery_worker` должно быть видно выполнение задачи:

```powershell
docker compose logs celery_worker
```

В логах `celery_beat` можно проверить, что beat отправляет задачу по расписанию:

```powershell
docker compose logs celery_beat
```
