



```bash

DJANGO_SECRET_KEY=
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=learnflow.uz,www.learnflow.uz


DATABASE_URL=postgresql://user:password@host:5432/learnflow


CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_ACCEPT_CONTENT=['json']
CELERY_TIMEZONE=UTC


JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7



USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=learnflow-prod
AWS_S3_REGION_NAME=auto  
AWS_S3_ENDPOINT_URL=https://account-id.r2.cloudflarestorage.com
AWS_S3_CUSTOM_DOMAIN=cdn.learnflow.uz  


SUBMISSIONS_BUCKET=learnflow-submissions-prod
CERTIFICATES_BUCKET=learnflow-certificates-prod
MEDIA_BUCKET=learnflow-media-prod


EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=


SENTRY_DSN=
```



```yaml
services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes: [.:/app]
    env_file: .env
    depends_on: [db, redis]

  celery:
    build: .
    command: celery -A config worker -l info -Q default,fan_out,coding
    env_file: .env
    depends_on: [db, redis]

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: learnflow
      POSTGRES_USER: learnflow
      POSTGRES_PASSWORD: password

  redis:
    image: redis:7-alpine
```



**ADR-030:** Используем Celery + Redis для фоновых задач.

| Очередь | Назначение | Workers | Concurrency |
|---------|------------|---------|-------------|
| `default` | Email, SMS, Push, Outbox processing | 2-4 | 4 |
| `fan_out` | Fan-out на N студентов (LessonPublished) | 4-8 | 2 |
| `coding` | Sandbox execution (код студентов) | 8-16 | 1 |
| `pdf` | PDF generation (сертификаты) | 2-4 | 2 |



```bash

celery -A learnflow worker -l info -Q default -c 4 -n default@%h


celery -A learnflow worker -l info -Q fan_out -c 2 -n fanout@%h


celery -A learnflow worker -l info -Q coding -c 1 -n coding@%h


celery -A learnflow worker -l info -Q pdf -c 2 -n pdf@%h


celery -A learnflow beat -l info
```



```python

from celery.schedules import crontab

app.conf.beat_schedule = {
    'process-outbox-events': {
        'task': 'shared.tasks.process_outbox_events',
        'schedule': 10.0,  
    },
    'cleanup-old-outbox': {
        'task': 'shared.tasks.cleanup_old_outbox',
        'schedule': crontab(hour=3, minute=0),  
    },
    'send-daily-digest': {
        'task': 'notifications.tasks.send_daily_digest',
        'schedule': crontab(hour=9, minute=0),  
    },
}
```



**Flower** — web-based monitoring для Celery:

```bash
celery -A learnflow flower --port=5555
```

Доступ: http://localhost:5555

**Метрики для мониторинга:**
- Task success/failure rate
- Queue length (alerts если > 1000)
- Worker latency (p95)
- Memory usage per worker (restart если > 1 GB)

---



**ADR-031:** Используем S3-compatible object storage для файлов студентов и сертификатов.



**Production:** Cloudflare R2
- Zero egress fees (экономия ~$1000/год)
- S3-compatible API
- Интеграция с Cloudflare CDN

**Development:** MinIO (self-hosted)
- Docker container
- S3-compatible API
- Локальная разработка без cloud costs



```
learnflow-submissions-prod/
  ├── temp/                    
  ├── {assignment_id}/         
  │   ├── {submission_id}/
  │   │   ├── v1/
  │   │   │   ├── files.zip
  │   │   │   └── metadata.json
  │   │   ├── v2/
  │   │   │   └── files.zip

learnflow-submissions-quarantine/  
  ├── {date}/
  │   ├── {submission_id}/

learnflow-certificates-prod/
  ├── {year}/
  │   ├── {month}/
  │   │   ├── {certificate_id}.pdf

learnflow-media-prod/
  ├── course-thumbnails/
  ├── user-avatars/
  └── lesson-materials/
```



```
1. Student upload → S3 temp bucket
2. Celery task: ClamAV scan
3. If passed → move to permanent bucket
4. If failed → move to quarantine bucket + notify admin
5. Mentor видит только файлы со статусом 'passed'
```



**Presigned URLs** для secure downloads:

```python

import boto3
from datetime import timedelta

def get_submission_download_url(submission_file: SubmissionFile) -> str:
    """Генерирует presigned URL с TTL 1 час."""
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.SUBMISSIONS_BUCKET,
            'Key': submission_file.s3_key,
        },
        ExpiresIn=3600,  
    )
    return url
```

**Не прокси через Django** — прямой download с S3 (быстрее + дешевле)



**Submissions:**
- После 2 лет → переместить в cold storage (если R2 не поддерживает — оставить как есть)
- Failed virus scans → удалить после 30 дней

**Certificates:**
- Никогда не удалять (compliance)
- Versioning включен (на случай reissue)



```yaml

services:
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"  
      - "9001:9001"  
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio-data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  minio-data:
```

**Создание buckets (первый запуск):**

```bash

brew install minio/stable/mc  

wget https://dl.min.io/client/mc/release/linux-amd64/mc


mc alias set local http://localhost:9000 minioadmin minioadmin


mc mb local/learnflow-submissions-dev
mc mb local/learnflow-certificates-dev
mc mb local/learnflow-media-dev
mc mb local/learnflow-submissions-quarantine


mc anonymous set download local/learnflow-certificates-dev
```

---



```bash

python manage.py migrate --check  
python manage.py migrate          
```

Миграции применяются атомарно. Откат — отдельная миграция, не `migrate --fake`.

---



**Submissions Domain требует сканирование файлов студентов.**



```yaml
  clamav:
    image: clamav/clamav:latest
    ports: ["3310:3310"]
    volumes:
      - clamav-data:/var/lib/clamav
    environment:
      CLAMAV_NO_FRESHCLAM: "false"  

volumes:
  clamav-data:
```



```bash
CLAMAV_HOST=clamav
CLAMAV_PORT=3310
CLAMAV_TIMEOUT=30  
```



1. Student загружает файл → S3 temp bucket
2. Celery task запускает ClamAV scan
3. Если `passed` → перемещение в S3 permanent bucket
4. Если `failed` → удаление + уведомление студенту
5. Mentor видит только файлы со статусом `passed`

**См. также:** ADR-018 в DECISIONS.md

---



**Certificates Domain генерирует PDF из HTML template.**



```bash

weasyprint==62.3      
Pillow==10.4.0        
```



```bash
CERTIFICATE_TEMPLATE_BUCKET=learnflow-certificates
CERTIFICATE_OUTPUT_BUCKET=learnflow-certificates-public
CERTIFICATE_FONT_PATH=/app/fonts/  
```



```dockerfile

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
```



- Генерация PDF → очередь `default` (не `fan_out`)
- Timeout: 60 секунд на один сертификат
- Retry: 3 попытки с exponential backoff

**См. также:** ADR-025 в DECISIONS.md

---



- **Sentry** — ошибки Django и Celery
- **Flower** — мониторинг Celery tasks (`celery -A config flower`)
- **pgBadger** или **pg_stat_statements** — медленные запросы PostgreSQL
