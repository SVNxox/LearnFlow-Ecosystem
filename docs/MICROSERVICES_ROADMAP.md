

**Дата создания:** 2026-06-07  
**Статус:** Планирование  
**Текущая архитектура:** Модульный монолит

---



LearnFlow начинается как модульный монолит с чёткими границами между доменами. Экстракция в микросервисы — **постепенный процесс**, начинающийся с периферийных доменов со слабой связанностью.

**Принцип:** Strangler Fig Pattern — новый функционал в микросервисах, старый остаётся в монолите до миграции.

**Цель:** Не "разбить монолит на микросервисы", а **изолировать домены требующие независимого scaling**.

---



| Критерий | Вес | Описание |
|----------|-----|----------|
| **Слабая связанность** | 30% | Мало зависимостей от других доменов |
| **Асинхронность** | 25% | Не блокирует критичный user flow |
| **Независимый scaling** | 20% | Нагрузка не коррелирует с основным трафиком |
| **Внешние интеграции** | 15% | Работает с внешними API (email, SMS, S3) |
| **Специфичная инфраструктура** | 10% | Нужны особые ресурсы (GPU, ClickHouse) |

---



| Домен | Оценка | Tier | Приоритет | Когда |
|-------|--------|------|-----------|-------|
| **Notifications** | 9/10 | 1 | Высокий | Год 1 Q2 |
| **Certificates** | 8/10 | 1 | Высокий | Год 1 Q3 |
| **Analytics** | 8/10 | 1 | Высокий | Год 1 Q4 |
| **Assessment** | 6/10 | 2 | Средний | Год 2 Q1 |
| **Submissions** | 5/10 | 2 | Средний | Год 2 Q2 |
| **Mentorship** | 4/10 | 2 | Средний | Год 2 Q3 |
| **UserProgress** | 2/10 | 3 | Низкий | Год 3+ |
| **Learning** | 2/10 | 3 | Низкий | Год 3+ |
| **Identity** | 1/10 | 3 | Никогда | - |

---





---



**Сложность:** Низкая  
**Время:** 4-6 недель  
**ROI:** Высокий


- ✅ Слабо связан (только слушает события)
- ✅ Внешние API (SendGrid, Twilio, FCM)
- ✅ Spike нагрузки при массовых уведомлениях
- ✅ Легко тестировать изолированно



```
Монолит                    RabbitMQ              Notifications Service
┌─────────────┐            ┌────────┐            ┌──────────────────┐
│ Course      │            │        │            │ Email Worker     │
│ Service     │──publish──►│ Events │──consume──►│ SMS Worker       │
│             │            │ Queue  │            │ Push Worker      │
└─────────────┘            └────────┘            └──────────────────┘
                                                          │
                                                          ▼
                                                   SendGrid/Twilio/FCM
```


- `CourseCompleted` → email с сертификатом
- `CertificateIssued` → email "Your certificate is ready"
- `AssessmentNeedsMentorReview` → push ментору
- `SubmissionReviewed` → email студенту
- `ModuleUnlocked` → push студенту


- **Язык:** Python (FastAPI) или Go
- **Message Broker:** RabbitMQ (topic exchange)
- **Storage:** PostgreSQL для templates + Redis для rate limiting
- **Email:** SendGrid API
- **SMS:** Twilio API
- **Push:** Firebase Cloud Messaging



**Шаг 1:** Создать Notifications Service (параллельно с монолитом)
```python

def publish_to_outbox(event_type, aggregate_id, payload):
    
    DomainEventOutbox.objects.create(...)
    
    
    if feature_flags.is_enabled('notifications_service'):
        rabbitmq_publish(event_type, payload)
```

**Шаг 2:** Feature flag для 10% трафика → 50% → 100%

**Шаг 3:** Удалить старый код отправки из монолита


- Email delivery rate (> 95%)
- SMS delivery rate (> 98%)
- Push delivery rate (> 90%)
- Lag между событием и доставкой (< 30 сек)


Feature flag `notifications_service = false` → возврат к монолиту

---



**Сложность:** Средняя  
**Время:** 6-8 недель  
**ROI:** Высокий (CPU-intensive)


- ✅ PDF generation — тяжёлая операция (блокирует workers)
- ✅ Snapshot данных (нет JOIN с другими доменами)
- ✅ Публичный API `/verify/{code}` — независимый endpoint
- ✅ S3 для storage — уже изолировано



```
Монолит                    RabbitMQ              Certificates Service
┌─────────────┐            ┌────────┐            ┌──────────────────┐
│ UserProgress│            │        │            │ PDF Generator    │
│ Service     │──publish──►│ Events │──consume──►│ Worker           │
│             │            │ Queue  │            │                  │
└─────────────┘            └────────┘            └──────────────────┘
                                                          │
                                                          ▼
Public API                                           S3 Storage
/api/v1/certificates/verify/{code}
```


- `CourseCompleted` → generate certificate (async)


- `CertificateIssued` → Notifications (email)


- **Язык:** Python (WeasyPrint для PDF)
- **Storage:** PostgreSQL + S3 для PDFs
- **Queue:** RabbitMQ
- **Cache:** Redis для verification codes (rate limiting)


```
POST   /api/v1/certificates/generate     
GET    /api/v1/certificates/{id}         
GET    /public/verify/{code}             
POST   /api/v1/certificates/{id}/revoke  
```



**Шаг 1:** Новые сертификаты генерируются в сервисе
```python

if feature_flags.is_enabled('certificates_service'):
    response = requests.post('http://certificates-service/api/v1/certificates/generate', ...)
else:
    certificate = CertificateService.generate_certificate(enrollment_id)
```

**Шаг 2:** Миграция старых сертификатов (data migration)

**Шаг 3:** Публичный endpoint `/verify` переключается на новый сервис


- PDF generation time (p95 < 5 сек)
- Verification API latency (p95 < 200ms)
- S3 storage costs

---



**Сложность:** Средняя  
**Время:** 8-10 недель  
**ROI:** Средний (улучшает UX, не критично)


- ✅ Read-only (не пишет в основную БД)
- ✅ Тяжёлые queries (агрегации по миллионам строк)
- ✅ Отдельная БД (ClickHouse для time-series)
- ✅ Не влияет на user flow



```
Монолит (Read Replica)     Kafka                Analytics Service
┌─────────────┐            ┌────────┐           ┌──────────────────┐
│ PostgreSQL  │            │        │           │ ClickHouse       │
│ (replica)   │──stream───►│ Events │──consume─►│ (OLAP DB)        │
│             │            │        │           │                  │
└─────────────┘            └────────┘           └──────────────────┘
                                                          │
                                                          ▼
                                                   Metabase/Grafana
```


- Course completion rates
- Average time per lesson
- Student engagement (daily/weekly active)
- Mentor performance (review time, approval rate)
- Certificate issuance trends


- **Язык:** Python (FastAPI) или Go
- **OLAP DB:** ClickHouse
- **Stream:** Kafka (CDC от PostgreSQL)
- **Visualization:** Metabase или Grafana



**Шаг 1:** CDC от PostgreSQL → Kafka (Debezium)

**Шаг 2:** Kafka → ClickHouse (материализованные view)

**Шаг 3:** API для метрик (internal)

**Шаг 4:** Metabase подключается к ClickHouse


- CDC lag (< 10 сек)
- ClickHouse query performance
- Disk usage (ClickHouse сжатие данных)

---





---



**Сложность:** Высокая  
**Время:** 10-12 недель  
**ROI:** Средний


- ⚠️ Средняя связанность (интеграция с Submissions)
- ⚠️ Coding execution требует изоляции (Docker sandbox)
- ✅ Auto-grading — CPU-intensive
- ⚠️ Pass/Fail → unlock next module (критичная транзакция)



```
Монолит                    RabbitMQ              Assessment Service
┌─────────────┐            ┌────────┐            ┌──────────────────┐
│ UserProgress│            │        │            │ Grading Engine   │
│ Service     │◄──publish──│ Events │◄──publish──│ Auto-grader      │
│             │            │ Queue  │            │ Coding Sandbox   │
└─────────────┘            └────────┘            └──────────────────┘
                                                          │
                                                          ▼
                                                   Docker Sandbox Pool
```


- `ModuleCompleted` → unlock assessment


- `ModuleAssessmentPassed` → UserProgress (unlock next module)
- `AssessmentNeedsMentorReview` → Mentorship
- `AssessmentAttemptStarted` (project) → Submissions


- **Язык:** Python или Go
- **Sandbox:** Docker с ограничениями (CPU, RAM, network off)
- **Queue:** RabbitMQ
- **Storage:** PostgreSQL


- **Транзакционность:** Pass/Fail должен атомарно unlock next module
- **Sandbox security:** Isolation студентского кода
- **Performance:** Auto-grading должен быть < 5 сек



**Шаг 1:** Coding sandbox экстрагируется первым (уже изолирован)

**Шаг 2:** Auto-grading переносится в сервис

**Шаг 3:** Mentor override остаётся в монолите (пока)

---



**Сложность:** Высокая  
**Время:** 8-10 недель  
**ROI:** Средний


- ⚠️ Тесно связан с Assessment (project items)
- ⚠️ File scanning (ClamAV) — sync или async?
- ✅ S3 storage — уже изолировано
- ⚠️ Mentor review → Mentorship (work queue)


- `AssessmentAttemptStarted` (project) → create Assignment


- `SubmissionReviewed` → Assessment (update points)
- `SubmissionSubmitted` → Mentorship (work queue)


- **File security:** ClamAV scan должен быть надёжным
- **Версионирование:** История revisions
- **Integration:** Тесная связь с Assessment

---



**Сложность:** Средняя  
**Время:** 6-8 недель  
**ROI:** Низкий


- ⚠️ Work queue зависит от Submissions и Assessment
- ⚠️ Offline sessions → attendance → UserProgress

---






- **Причина:** Все домены зависят от User
- **Альтернатива:** Мигрировать на Auth0 или Keycloak (external identity provider)


- **Причина:** Центр системы, высокая связанность
- **Решение:** Остаётся backbone монолита


- **Причина:** Получает события от всех, критичный path
- **Решение:** Остаётся в монолите

---





1. **Outbox Pattern** → легко заменить на RabbitMQ
2. **Selector/Service разделение** → чистые API boundaries
3. **UUID без FK** между доменами → готов к distributed system
4. **Event-driven architecture** → слабая связанность





```python

from apps.courses.models import Course
course = Course.objects.get(pk=course_id)


from apps.courses.selectors import CourseCatalogSelector
course = CourseCatalogSelector.get_course_by_id(course_id)
```



```python

urlpatterns = [
    path('api/v1/', include('apps.learning.api.v1.urls')),
    path('api/v2/', include('apps.learning.api.v2.urls')),  
]
```



```python

class FeatureFlags:
    @staticmethod
    def is_enabled(flag_name: str) -> bool:
        
        return redis.get(f'feature:{flag_name}') == 'true'


if FeatureFlags.is_enabled('use_certificates_service'):
    send_to_microservice(event)
else:
    send_via_monolith(event)
```



```python

from opentelemetry import trace

tracer = trace.get_tracer(__name__)


with tracer.start_as_current_span("enroll_student"):
    enrollment = CourseEnrollment.objects.create(...)
    
    with tracer.start_as_current_span("publish_event"):
        publish_to_outbox(StudentEnrolled(...))
```



```python

from pybreaker import CircuitBreaker

certificates_breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@certificates_breaker
def generate_certificate_via_service(enrollment_id):
    response = requests.post('http://certificates-service/...')
    return response.json()


try:
    result = generate_certificate_via_service(enrollment_id)
except CircuitBreakerError:
    
    result = CertificateService.generate_certificate(enrollment_id)
```

---




```
┌─────────────────────────────┐
│   Django Monolith           │
│   ┌──────────────────────┐  │
│   │ Learning             │  │
│   │ UserProgress         │  │
│   │ Assessment           │  │
│   │ Submissions          │  │
│   │ Certificates         │  │
│   │ Notifications        │  │
│   └──────────────────────┘  │
└─────────────────────────────┘
           │
           ▼
    PostgreSQL + Redis
```


```
┌─────────────────────┐     ┌──────────────────┐
│  Django Monolith    │     │  Notifications   │
│  ┌───────────────┐  │     │  Service         │
│  │ Learning      │  │     └──────────────────┘
│  │ UserProgress  │  │              │
│  │ Assessment    │  │              │
│  │ Submissions   │  │     ┌──────────────────┐
│  │ Mentorship    │  │     │  Certificates    │
│  └───────────────┘  │     │  Service         │
└─────────────────────┘     └──────────────────┘
           │                         │
           ▼                         ▼
    PostgreSQL              PostgreSQL + S3
           │
           ▼
      RabbitMQ ◄──────────────────┐
           │                       │
           ▼                       │
┌──────────────────┐              │
│  Analytics       │──────────────┘
│  Service         │
│  (ClickHouse)    │
└──────────────────┘
```

---



| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Distributed transactions | Высокая | Высокое | Saga Pattern, Outbox Pattern |
| Network latency | Средняя | Среднее | Кэширование, async где можно |
| Debugging сложнее | Высокая | Среднее | Distributed tracing (Jaeger) |
| Data consistency | Высокая | Высокое | Event sourcing, eventual consistency |
| Deployment сложнее | Высокая | Низкое | Kubernetes, Helm charts, CI/CD |
| Monitoring overhead | Средняя | Среднее | Centralized logging (ELK/Grafana) |

---



| Метрика | Монолит (текущий) | После Phase 1 | После Phase 2 |
|---------|-------------------|---------------|---------------|
| **API latency (p95)** | 300ms | 250ms | 200ms |
| **Database connections** | 50 | 30 | 20 |
| **CPU usage (peak)** | 80% | 60% | 50% |
| **Deployment time** | 15 min | 10 min/service | 5 min/service |
| **Cost (infrastructure)** | $500/mo | $700/mo | $1000/mo |
| **Team velocity** | 1x | 1.2x | 1.5x |

---



```
Год 1 Q1: ██████ Монолит (текущий)
Год 1 Q2: ██████ Notifications Service
Год 1 Q3: ██████ Certificates Service
Год 1 Q4: ██████ Analytics Service

Год 2 Q1: ██████ Assessment Service
Год 2 Q2: ██████ Submissions Service
Год 2 Q3: ██████ Mentorship Service
Год 2 Q4: ██████ Стабилизация

Год 3+:   ██████ Core остаётся монолитом (Learning, UserProgress, Identity)
```

---



**Не спешить с микросервисами.** Модульный монолит работает хорошо до 100k+ пользователей.

**Экстрагировать по необходимости:**
- Notifications — когда email/SMS стали узким местом
- Certificates — когда PDF generation блокирует workers
- Analytics — когда queries тормозят основную БД

**Core остаётся монолитом** — Learning, UserProgress, Identity слишком связаны для экстракции.

**Приоритет:** Business value > Architecture purity
