# Google OAuth2 в проекте Ridee

## Как создать Google OAuth Client

1. Откройте Google Cloud Console:

```text
https://console.cloud.google.com/
```

2. Создайте новый проект или выберите существующий.
3. Откройте `APIs & Services` -> `OAuth consent screen`.
4. Настройте экран согласия:
   - тип приложения: `External` для обычной проверки;
   - название приложения: `Ridee`;
   - email поддержки: ваш email.
5. Откройте `APIs & Services` -> `Credentials`.
6. Нажмите `Create Credentials` -> `OAuth client ID`.
7. В типе приложения выберите `Web application`.

## Какие Redirect URI указать

Для локального запуска Django:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
http://localhost:8000/accounts/google/login/callback/
```

Для Docker используется тот же адрес, если проект открыт на `127.0.0.1:8000`.

## Какие переменные окружения нужны

PowerShell:

```powershell
$env:GOOGLE_OAUTH_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
$env:GOOGLE_OAUTH_CLIENT_SECRET="your-google-client-secret"
```

Docker Compose:

```powershell
$env:GOOGLE_OAUTH_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
$env:GOOGLE_OAUTH_CLIENT_SECRET="your-google-client-secret"
docker compose up --build
```

## Как проверить вход

1. Запустите проект.
2. Откройте страницу входа:

```text
http://127.0.0.1:8000/accounts/login/
```

3. Нажмите кнопку `Войти через Google`.
4. После успешного входа пользователь будет перенаправлен на главную страницу Ridee.

Прямой URL Google OAuth:

```text
http://127.0.0.1:8000/accounts/google/login/
```
