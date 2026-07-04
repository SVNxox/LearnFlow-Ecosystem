





1. Откройте https://myaccount.google.com/
2. Перейдите в **Security** (Безопасность)
3. Включите **2-Step Verification** (Двухфакторная аутентификация), если еще не включена
4. После включения 2FA вернитесь в Security
5. Найдите **App passwords** (Пароли приложений)
6. Создайте новый App Password:
   - Select app: **Mail**
   - Select device: **Other** (введите "LearnFlow")
7. Скопируйте сгенерированный 16-символьный пароль



Откройте `.env` и замените:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=ваш-email@gmail.com
EMAIL_HOST_PASSWORD=ваш-16-символьный-app-password
DEFAULT_FROM_EMAIL=noreply@learnflow.local
```



```bash

pkill -f "runserver"
pkill -f "celery.*worker"


./start_local.sh
```



Зарегистрируйте нового пользователя:

```bash
curl -X POST http://localhost:8000/api/v1/identity/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ваш-email@gmail.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

Проверьте почту — письмо с верификационной ссылкой должно прийти в течение нескольких секунд.

---





1. Зарегистрируйтесь на https://www.mailgun.com/
2. Верифицируйте домен или используйте sandbox домен
3. Получите SMTP credentials



```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@вашдомен.mailgun.org
EMAIL_HOST_PASSWORD=ваш-mailgun-smtp-password
DEFAULT_FROM_EMAIL=noreply@вашдомен.com
```

---





1. Зарегистрируйтесь на https://sendgrid.com/
2. Создайте API Key в Settings → API Keys



```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=ваш-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@вашдомен.com
```

---





```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=ваш-email@yandex.ru
EMAIL_HOST_PASSWORD=ваш-пароль
DEFAULT_FROM_EMAIL=noreply@learnflow.uz
```

---





```bash
python manage.py shell -c "
from django.conf import settings
print(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
print(f'EMAIL_HOST: {settings.EMAIL_HOST}')
print(f'EMAIL_PORT: {settings.EMAIL_PORT}')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
"
```



```bash
python manage.py shell -c "
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test.',
    'noreply@learnflow.local',
    ['ваш-email@gmail.com'],
    fail_silently=False,
)
print('Email sent!')
"
```



```bash
tail -f celery.log | grep -A 10 "send_verification_email"
```



1. **SMTPAuthenticationError** — неправильный email или пароль
2. **SMTPServerDisconnected** — проверьте EMAIL_HOST и EMAIL_PORT
3. **Connection timeout** — проверьте firewall или VPN
4. **App Password not working** — убедитесь что 2FA включена в Gmail
