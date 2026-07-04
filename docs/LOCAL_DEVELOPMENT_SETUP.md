

Это руководство описывает как запустить LearnFlow **локально** (без Docker) для разработки и тестирования.

---



- Python 3.12+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (для frontend)
- MinIO (для S3-совместимого хранилища)

---





```bash

sudo apt update
sudo apt install postgresql postgresql-contrib


sudo apt install redis-server


sudo apt install python3.12 python3.12-venv python3-pip


curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```



```bash

brew install postgresql@14 redis python@3.12 node


brew services start postgresql@14
brew services start redis
```

---



```bash

sudo systemctl start postgresql  



sudo -u postgres psql
```

В psql:

```sql
CREATE USER learnflow WITH PASSWORD 'learnflow';
CREATE DATABASE learnflow_local OWNER learnflow;
GRANT ALL PRIVILEGES ON DATABASE learnflow_local TO learnflow;
\q
```

Проверка подключения:

```bash
psql -U learnflow -d learnflow_local -h localhost


```

---



```bash

sudo systemctl start redis  



redis-cli ping

```

---





```bash

wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/


mkdir -p ~/minio-data


minio server ~/minio-data --console-address ":9001"
```



```bash
brew install minio/stable/minio


mkdir -p ~/minio-data


minio server ~/minio-data --console-address ":9001"
```

**MinIO будет доступен:**
- API: http://localhost:9000
- Web Console: http://localhost:9001
- Логин: `minioadmin` / `minioadmin`

**Создать bucket:**

1. Открыть http://localhost:9001
2. Войти (minioadmin / minioadmin)
3. Buckets → Create Bucket
4. Имя: `learnflow-local`
5. Создать

---





```bash
cd /home/svn/PyCharmMiscProject/DjangoProject/LearnFlow\ Ecosystem/learnflow


python3.12 -m venv .venv
source .venv/bin/activate  



pip install -r requirements.txt
```



```bash

cp .env.local.example .env


nano .env
```

**Основные переменные в `.env`:**

```bash
SECRET_KEY=local-dev-secret-key
DEBUG=True
DATABASE_URL=postgres://learnflow:learnflow@localhost:5432/learnflow_local
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_S3_ENDPOINT_URL=http://localhost:9000
AWS_STORAGE_BUCKET_NAME=learnflow-local
```



```bash

export DJANGO_SETTINGS_MODULE=learnflow.settings.local


python manage.py migrate


python manage.py createsuperuser
```



```bash

export DJANGO_SETTINGS_MODULE=learnflow.settings.local
python manage.py runserver

```



```bash

export DJANGO_SETTINGS_MODULE=learnflow.settings.local
celery -A learnflow worker --loglevel=info


export DJANGO_SETTINGS_MODULE=learnflow.settings.local
celery -A learnflow beat --loglevel=info
```

---



```bash
cd src/frontend


npm install


cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF


npm run dev

```

---





```bash

curl http://localhost:8000/api/v1/health/




```



```bash


```



```bash
psql -U learnflow -d learnflow_local -h localhost -c "SELECT COUNT(*) FROM accounts_user;"

```



```bash
redis-cli
> KEYS *

```



```bash



```

---





1. Открыть http://localhost:3000/register
2. Зарегистрироваться с test email
3. **Email будет напечатан в консоли Django** (не отправлен реально)
4. Скопировать verification link из консоли
5. Открыть link в браузере
6. Войти на http://localhost:3000/login



1. Создать submission
2. Upload файл
3. Проверить в MinIO console — файл должен появиться в bucket

---





```bash

python manage.py makemigrations


python manage.py migrate


python manage.py createsuperuser


python manage.py shell


python manage.py diffsettings
```



```bash

pg_dump -U learnflow -h localhost learnflow_local > backup.sql


psql -U learnflow -h localhost learnflow_local < backup.sql


python manage.py flush
```



```bash

redis-cli FLUSHDB


redis-cli KEYS "*"


redis-cli DEL "lf_local:auth:fails:127.0.0.1"
```



```bash

celery -A learnflow inspect active


celery -A learnflow purge
```

---





**Решение:**
```bash

sudo systemctl status postgresql
sudo systemctl start postgresql


psql -U learnflow -d learnflow_local -h localhost
```



**Решение:**
```bash

sudo systemctl status redis
sudo systemctl start redis


redis-cli ping
```



**Решение:**
```bash

ps aux | grep minio


minio server ~/minio-data --console-address ":9001"


```



**Это нормально!** В локальной разработке используется Console backend.

Emails печатаются в **консоль Django** (терминал где запущен `python manage.py runserver`).

Ищите в консоли:
```
Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Verify your email
From: noreply@learnflow.local
To: user@example.com
...
```



**Решение:**
```bash

source .venv/bin/activate


pip install -r requirements.txt
```



**Решение:**
```bash

cat src/frontend/.env.local




CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---



После полной установки должны работать:

| Сервис | Порт | URL | Статус |
|--------|------|-----|--------|
| Django | 8000 | http://localhost:8000 | `python manage.py runserver` |
| Frontend | 3000 | http://localhost:3000 | `npm run dev` |
| PostgreSQL | 5432 | localhost:5432 | `systemctl status postgresql` |
| Redis | 6379 | localhost:6379 | `systemctl status redis` |
| MinIO API | 9000 | http://localhost:9000 | `minio server ~/minio-data` |
| MinIO Console | 9001 | http://localhost:9001 | Login: minioadmin |
| Celery Worker | - | - | `celery -A learnflow worker` |
| Celery Beat | - | - | `celery -A learnflow beat` |

---



| Настройка | local.py | development.py |
|-----------|----------|----------------|
| **Использование** | Локальная разработка (без Docker) | Docker Compose |
| **Database** | localhost:5432 | db:5432 (Docker service) |
| **Redis** | localhost:6379 | redis:6379 (Docker service) |
| **MinIO** | localhost:9000 | minio:9000 (Docker service) |
| **Email** | Console (печать в терминал) | Console или SMTP |
| **CORS** | localhost:3000 | * (разрешены все) |
| **Password hasher** | MD5 (быстрый) | BCrypt (безопасный) |
| **Lockout** | 3 попытки / 5 мин | 5 попыток / 15 мин |

**Когда использовать:**
- `local.py` — разработка без Docker (быстрый старт, легкая отладка)
- `development.py` — разработка с Docker Compose (близко к production)
- `production.py` — production deployment (HTTPS, security headers)

---





```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.envFile": "${workspaceFolder}/.env",
  "python.linting.pylintEnabled": true,
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```



1. Settings → Project → Python Interpreter
2. Add Interpreter → Existing environment
3. Выбрать `.venv/bin/python`
4. Settings → Django
   - Enable Django support
   - Django project root: `/path/to/learnflow`
   - Settings: `learnflow/settings/local.py`
   - Manage script: `manage.py`

---



После установки локального окружения:

1. ✅ Запустить все сервисы (Django, Frontend, PostgreSQL, Redis, MinIO)
2. ✅ Создать суперпользователя
3. ✅ Зарегистрировать тестового пользователя
4. ✅ Протестировать login/register flow
5. ✅ Протестировать file upload
6. ✅ Проверить email в консоли
7. ✅ Открыть MinIO console и проверить uploaded файлы

---



- **Django docs:** https://docs.djangoproject.com/
- **PostgreSQL docs:** https://www.postgresql.org/docs/
- **Redis docs:** https://redis.io/docs/
- **MinIO docs:** https://min.io/docs/minio/linux/index.html
- **Celery docs:** https://docs.celeryq.dev/

---

**Готово!** 🎉 Теперь у вас локальное окружение для разработки LearnFlow.

Для вопросов и проблем: создайте issue в репозитории.
