

Руководство для быстрого запуска LearnFlow локально.

---




- **Python 3.12+**
- **PostgreSQL 16+**
- **Redis 7+**
- **Git**


- **Docker** и **Docker Compose** (для изолированной разработки)
- **ClamAV** (для сканирования файлов студентов)

---





```bash
git clone https://github.com/your-org/learnflow.git
cd learnflow
```



```bash
python -m venv .venv
source .venv/bin/activate  

.venv\Scripts\activate     
```



```bash
pip install -r requirements.txt
```



Создай файл `.env` в корне проекта:

```bash
cp .env.example .env
```

Отредактируй `.env`:

```bash

DJANGO_SECRET_KEY=your-secret-key-here-change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1


DATABASE_URL=postgresql://learnflow:password@localhost:5432/learnflow


CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1


JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7


USE_S3=False
MEDIA_ROOT=./media


EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```



```bash

psql -U postgres


CREATE DATABASE learnflow;
CREATE USER learnflow WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE learnflow TO learnflow;
\q
```



```bash
python manage.py migrate
```



```bash
python manage.py createsuperuser


```



```bash
python manage.py loaddata fixtures/sample_courses.json
```



```bash
python manage.py runserver
```

Приложение доступно по адресу: **http://localhost:8000**

Django Admin: **http://localhost:8000/admin**

---





```bash
git clone https://github.com/your-org/learnflow.git
cd learnflow
```



```bash
cp .env.example .env

```



```bash
docker-compose up -d
```

Это запустит:
- **web** (Django) на порту 8000
- **db** (PostgreSQL) на порту 5432
- **redis** на порту 6379
- **celery** (worker)



```bash
docker-compose exec web python manage.py migrate
```



```bash
docker-compose exec web python manage.py createsuperuser
```



Приложение доступно по адресу: **http://localhost:8000**



```bash
docker-compose down
```

---





```bash

celery -A learnflow worker -l info -Q default,fan_out,coding
```



```bash

docker-compose logs -f celery
```

---





```bash
python manage.py makemigrations
```



```bash
python manage.py migrate
```



```bash
python manage.py startapp app_name
```



```bash
pytest

pytest --cov=apps --cov-report=html
```



```bash
python manage.py createsuperuser
```



```bash
python manage.py shell
```



```bash
python manage.py flush
```

---





1. Перейди в Django Admin: http://localhost:8000/admin
2. Перейди в **Courses → Courses**
3. Нажми **Add Course**
4. Заполни поля:
   - Title: "Python для начинающих"
   - Slug: "python-beginners" (автозаполнится)
   - Status: "draft"
5. Сохрани



**Через Django Admin:**

1. **Accounts → Users** → выбери студента
2. **Courses → Course Enrollments**
3. Нажми **Add Course Enrollment**
4. Выбери:
   - User: студент
   - Course: курс
   - Delivery format: "online" или "offline"
5. Сохрани

**Через API:**

```bash
curl -X POST http://localhost:8000/api/v1/enrollments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"course_id": "COURSE_UUID"}'
```



1. **Mentorship → Attendance**
2. Нажми **Add Attendance**
3. Выбери:
   - Session: offline session
   - Student: студент
   - Status: "present"
4. Сохрани



Сертификаты генерируются автоматически при завершении курса через событие `CourseCompleted`.

**Ручная генерация (для тестов):**

```bash
python manage.py shell

from apps.certificates.services import CertificateService
from apps.learning.models import CourseEnrollment

enrollment = CourseEnrollment.objects.get(id='ENROLLMENT_UUID')
certificate = CertificateService.generate_certificate(enrollment.id)
print(certificate.verification_code)
```

---





```bash

curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "student@test.com", "password": "password"}'


{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}


curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "REFRESH_TOKEN"}'
```



```bash

curl http://localhost:8000/api/v1/courses/


curl http://localhost:8000/api/v1/courses/{course_id}/
```



```bash
curl -X POST http://localhost:8000/api/v1/enrollments/ \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"course_id": "COURSE_UUID"}'
```



```bash

curl http://localhost:8000/api/v1/progress/courses/{enrollment_id}/ \
  -H "Authorization: Bearer ACCESS_TOKEN"


curl -X POST http://localhost:8000/api/v1/progress/lessons/{lesson_id}/complete/ \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Полная документация API: [`docs/API.md`](API.md)

---



```
learnflow/
├── accounts/          
├── courses/           
├── progress/          
├── assessment/        
├── submissions/       
├── mentorship/        
├── certificates/      
├── notifications/     
├── learnflow/         
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   └── urls.py
├── docs/              
├── requirements.txt
├── manage.py
└── README.md
```

---





```
django.db.utils.OperationalError: could not connect to server
```

**Решение:**
1. Проверь что PostgreSQL запущен: `sudo systemctl status postgresql`
2. Проверь `DATABASE_URL` в `.env`
3. Проверь что БД создана: `psql -U postgres -l`



```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Решение:**
1. Проверь что Redis запущен: `sudo systemctl status redis`
2. Проверь `CELERY_BROKER_URL` в `.env`



```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Решение:**
1. Удали БД: `dropdb learnflow`
2. Создай заново: `createdb learnflow`
3. Примени миграции: `python manage.py migrate`



**Решение:**
1. Проверь что виртуальное окружение активировано
2. Переустанови зависимости: `pip install -r requirements.txt`
3. Проверь что находишься в корне проекта

---



После успешного запуска:

1. **Изучи документацию:**
   - [`CLAUDE.md`](../CLAUDE.md) — карта проекта для AI
   - [`docs/DOMAIN.md`](DOMAIN.md) — бизнес-логика
   - [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — архитектура
   - [`docs/DATABASE.md`](DATABASE.md) — схема БД

2. **Прочитай Contributing Guide:**
   - [`docs/CONTRIBUTING.md`](CONTRIBUTING.md) — как добавлять код

3. **Изучи паттерны:**
   - Selector / Service разделение
   - Domain Events
   - Celery для async операций

4. **Начни с небольших задач:**
   - Исправь опечатку в документации
   - Добавь unit test для selector
   - Реализуй простой API endpoint

---



- **Документация:** [`docs/`](.)
- **API Reference:** [`docs/API.md`](API.md)
- **Architecture Decisions:** [`docs/DECISIONS.md`](DECISIONS.md)
- **Testing Guide:** [`docs/TESTING.md`](TESTING.md)
- **Deployment Guide:** [`docs/DEPLOYMENT.md`](DEPLOYMENT.md)

---



- Создай issue в GitHub: https://github.com/your-org/learnflow/issues
- Задай вопрос в Slack: 
- Прочитай FAQ: [`docs/FAQ.md`](FAQ.md) (если существует)

---

**Готов к разработке!** 🚀
