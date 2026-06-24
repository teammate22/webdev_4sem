# Ridee API Postman

## Как импортировать коллекцию

1. Открой Postman.
2. Нажми `Import`.
3. Выбери файл `Ridee API.postman_collection.json`.
4. После импорта открой коллекцию `Ridee API`.

## Переменная `base_url`

В коллекции уже есть переменная:

```text
base_url = http://127.0.0.1:8000
```

Если Django запущен на другом адресе или порту, измени значение `base_url` в Variables коллекции.

## Запуск Django-сервера

Перед проверкой запросов запусти сервер:

```bash
python manage.py runserver
```

## Запросы с фильтрацией

Фильтрацию заказов демонстрируют запросы из папки `Filters`:

```text
GET {{base_url}}/api/orders/?min_price=500
GET {{base_url}}/api/orders/?max_price=1000
GET {{base_url}}/api/orders/?tariff=1
GET {{base_url}}/api/orders/?status=1
GET {{base_url}}/api/orders/?client=1
```

Эти запросы используют `OrderFilter` и `DjangoFilterBackend`.

## Тестовые данные

Коллекция рассчитана на существующую демо-базу проекта Ridee. Запросы вида `/api/orders/1/`, `/api/drivers/1/`, `/api/tariffs/1/`, `/api/reviews/1/` требуют, чтобы записи с `id=1` существовали в базе данных.
