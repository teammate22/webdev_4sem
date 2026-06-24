# Настройка Sentry для Ridee

## 1. Создать проект в Sentry

1. Зарегистрируйтесь или войдите на https://sentry.io/.
2. Создайте новый проект.
3. В качестве платформы выберите `Django`.
4. Откройте настройки проекта.

## 2. Где взять DSN

DSN находится в настройках проекта Sentry:

`Project Settings` -> `Client Keys (DSN)` -> поле `DSN`.

Пример формата:

```powershell
https://PUBLIC_KEY@oXXXX.ingest.sentry.io/PROJECT_ID
```

## 3. Как задать переменную окружения

Проект читает DSN из переменной окружения `SENTRY_DSN`. Если переменная не задана, сайт работает как обычно, но ошибки не отправляются в Sentry.

PowerShell:

```powershell
$env:SENTRY_DSN="https://PUBLIC_KEY@oXXXX.ingest.sentry.io/PROJECT_ID"
..\venv\Scripts\python.exe manage.py runserver
```

CMD:

```cmd
set SENTRY_DSN=https://PUBLIC_KEY@oXXXX.ingest.sentry.io/PROJECT_ID
..\venv\Scripts\python.exe manage.py runserver
```

## 4. Как проверить отправку ошибки

1. Запустите сервер с заданной переменной `SENTRY_DSN`.
2. Откройте тестовый endpoint:

```text
http://127.0.0.1:8000/api/test-sentry/
```

3. В браузере должна появиться ошибка сервера.
4. Через несколько секунд событие должно появиться в проекте Sentry.

Если `SENTRY_DSN` не задан, endpoint всё равно выбросит ошибку, но событие не будет отправлено в Sentry.
