# Mailhog в проекте Ridee

## Как открыть Mailhog

Запустите проект через Docker:

```powershell
docker compose up --build
```

Откройте веб-интерфейс Mailhog:

```text
http://127.0.0.1:8025/
```

SMTP-сервер Mailhog внутри Docker доступен Django по адресу:

```text
mailhog:1025
```

## Как проверить отправку письма

1. Запустите проект:

```powershell
docker compose up --build
```

2. Откройте тестовый endpoint:

```text
http://127.0.0.1:8000/api/test-email/
```

3. Перейдите в Mailhog:

```text
http://127.0.0.1:8025/
```

4. В списке писем должно появиться письмо с темой `Тестовое письмо Ridee`.

Если проект запускается без Docker, Mailhog должен быть доступен локально на `localhost:1025`.
