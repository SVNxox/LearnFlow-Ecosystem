



**Модульный монолит** — единое Django-приложение с чёткими границами между доменами.

Домены изолированы программно (через паттерны Selector/Service/Events), но развёрнуты как единый процесс на одной PostgreSQL базе. Это позволяет в будущем экстрагировать домены в отдельные сервисы с минимальными изменениями.

---



```
learnflow/
├── apps/
│   ├── accounts/      
│   ├── courses/       
│   ├── progress/      
│   ├── assessment/    
│   ├── submissions/   
│   ├── mentorship/    
│   ├── notifications/ 
│   ├── analytics/     
│   └── certificates/  
├── config/
│   ├── settings/
│   ├── urls.py
│   └── celery.py
└── shared/
    ├── events.py      
    ├── selectors.py   
    └── services.py    
```

---



Каждый домен (`apps/*/`) имеет следующую структуру:

```
apps/courses/
├── models.py       
├── selectors.py    
├── services.py     
├── events.py       
├── tasks.py        
├── api/
│   ├── views.py    
│   ├── serializers.py
│   └── urls.py
├── admin.py
├── apps.py
└── tests/
    ├── test_selectors.py
    ├── test_services.py
    └── test_api.py
```

**Правило слоёв:**
```
Request → View → Service (write) / Selector (read) → Model
                     ↓
               transaction.on_commit → Event dispatch → Handlers
```

---




- **Владеет:** User, UserInfo, Role, UserRole, StudentProfile, MentorProfile, UserSettings
- **Предоставляет:** `settings.AUTH_USER_MODEL`, `UserSelector`, аутентификационные endpoints
- **Не трогать:** этот домен решён — расширяй через Profile, не меняй User


- **Владеет:** Course, Module, Lesson, CourseEnrollment, все Lesson* компоненты, CourseCategory
- **Предоставляет:** каталог курсов, структуру обучения, enrollment
- **Потребляет:** `accounts.User` (FK), ничего из других learning-доменов


- **Владеет:** CourseProgress, ModuleProgress, LessonProgress, LessonContentView
- **Предоставляет:** текущий прогресс студента, completion state, next lesson
- **Потребляет:** события от `courses`, `assessment`, `submissions`, `mentorship`


- **Владеет:** ModuleAssessment, AssessmentItem, AssessmentAttempt, AssessmentResponse, AssessmentReviewLog
- **Предоставляет:** module-level оценки, grading (auto + manual), pass/fail
- **Потребляет:** ссылку на `courses.Module`, `courses.CourseEnrollment`
- **Ключевое:** Assessment = контейнер без type поля (ADR-010)


- **Владеет:** Assignment, Submission, SubmissionRevision, SubmissionFile, AutoCheck, SubmissionReview
- **Предоставляет:** версионирование попыток, проверка файлов (ClamAV), auto-check, mentor review
- **Потребляет:** ссылку на `courses.Lesson` (для homework) или `assessment.AssessmentItem` (для project)
- **Ключевое:** Assignment заменяет LessonHomework (ADR-014)


- **Владеет:** MentorGroup, OfflineSession, Attendance, AccessEvent, MentorWorkQueue
- **Предоставляет:** offline обучение, attendance tracking, mentor work queue
- **Потребляет:** события от `submissions`, `assessment`
- **Ключевое:** Attendance = ментор отмечает вручную (ADR-021)


- **Владеет:** Certificate, CertificateTemplate, CertificateReissueRequest, CertificateAuditLog
- **Предоставляет:** выдача сертификатов, PDF generation, публичная verification
- **Потребляет:** событие `CourseCompleted` от `progress`
- **Ключевое:** Сертификат = snapshot данных (ADR-025)

---





**1. Прямой FK (только внутри монолита, к Identity):**
```python

user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
```

**2. Мягкая ссылка (UUID без FK) — для будущей экстракции:**
```python

lesson_id = models.UUIDField()  
```

**3. Чтение через Selector (cross-domain reads):**
```python

from apps.progress.selectors import ModuleProgressSelector
progress = ModuleProgressSelector.get_module_progress(enrollment_id, module_id)
```

**4. События (основной механизм cross-domain writes):**
```python

@receiver(student_enrolled)
def handle_student_enrolled(sender, enrollment_id, **kwargs):
    ProgressInitialisationService.initialise_progress(enrollment_id)
```

**5. Прямой service call через on_commit (финальный шаг каскада):**
```python

transaction.on_commit(
    lambda: CourseEnrollmentService.complete_enrollment(enrollment_id)
)
```



Полная карта всех событий между доменами: [`docs/EVENTS.md`](EVENTS.md)

**Ключевые потоки:**
```
Learning ──► StudentEnrolled ──► UserProgress (initialise)
Learning ──► LessonPublished ──► UserProgress (unlock)

UserProgress ──► CourseCompleted ──► Learning (EnrollmentCompleted)
UserProgress ──► CourseCompleted ──► Certificates (generate)
UserProgress ──► ModuleCompleted ──► Assessment (unlock)

Assessment ──► ModuleAssessmentPassed ──► UserProgress (unlock next module)
Assessment ──► AssessmentNeedsMentorReview ──► Mentorship (add to queue)
Assessment ──► AssessmentAttemptStarted ──► Submissions (create Assignment for project)

Submissions ──► SubmissionReviewed ──► Assessment (update response points)
Submissions ──► SubmissionApproved ──► UserProgress (homework gate)
Submissions ──► SubmissionSubmitted ──► Mentorship (add to work queue)

Mentorship ──► AttendanceMarked ──► UserProgress (offline completion)
Mentorship ──► LessonCompletionOverride ──► UserProgress (mentor override)

Certificates ──► CertificateIssued ──► Notifications (send email)
```



- ❌ Прямой импорт model из другого домена (кроме accounts → Identity)
- ❌ Синхронный cross-domain write внутри транзакции другого домена
- ❌ Circular event dependencies (A emits → B handles → B emits → A handles)

---



**Celery** используется для:

| Задача                            | Причина                              |
|-----------------------------------|--------------------------------------|
| Fan-out на N студентов            | O(n) DB writes, timeout при sync     |
| Запуск кода (coding assessment)   | Sandboxed execution, секунды/минуты  |
| Отправка уведомлений              | Внешние API, ненужный sync           |
| Генерация сертификатов            | PDF rendering, медленно              |
| Пересчёт analytics                | Heavy queries, только в фоне         |

**Правило:** если операция обновляет строки пропорционально числу enrolled студентов — это Celery task, не inline код.

---



**ADR-029:** Гибридный подход — Django Signals для обычных событий, Outbox Pattern для критичных.



Используется для событий где потеря не критична и нужна immediate consistency.

**Пример: LessonCompleted**

```python

from django.dispatch import Signal

lesson_completed = Signal()  


class LessonProgressService:
    @staticmethod
    def mark_lesson_completed(enrollment_id: UUID, lesson_id: UUID):
        with transaction.atomic():
            lp = LessonProgress.objects.select_for_update().get(
                enrollment_id=enrollment_id,
                lesson_id=lesson_id,
            )
            lp.status = 'completed'
            lp.completed_at = timezone.now()
            lp.save(update_fields=['status', 'completed_at', 'updated_at'])
            
            
            transaction.on_commit(lambda: lesson_completed.send(
                sender=LessonProgress,
                enrollment_id=enrollment_id,
                lesson_id=lesson_id,
            ))


from django.dispatch import receiver
from apps.courses.events import lesson_completed

@receiver(lesson_completed)
def handle_lesson_completed(sender, enrollment_id, lesson_id, **kwargs):
    """Проверяет завершение модуля при завершении урока."""
    
    _check_module_completion(enrollment_id, lesson_id)
```



Используется для событий требующих guaranteed delivery и audit trail.

**Структура:**

```python

from django.db import models
from uuid import uuid4

class DomainEventOutbox(models.Model):
    """Outbox для критичных событий с гарантированной доставкой."""
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event_type = models.CharField(max_length=100, db_index=True)
    aggregate_id = models.UUIDField(db_index=True)  
    payload = models.JSONField()
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'shared_domaineventoutbox'
        indexes = [
            models.Index(fields=['processed_at', 'occurred_at']),  
            models.Index(fields=['event_type', 'aggregate_id']),   
        ]
        ordering = ['occurred_at']
    
    def __str__(self):
        return f"{self.event_type} ({self.aggregate_id})"
```

**Пример: StudentEnrolled (критичное событие)**

```python

from dataclasses import dataclass, asdict
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class StudentEnrolled:
    """Критичное событие — создаёт CourseProgress (aggregate root)."""
    enrollment_id: UUID
    user_id: UUID
    course_id: UUID
    delivery_format: str
    occurred_at: datetime


from shared.models import DomainEventOutbox

def publish_to_outbox(event_type: str, aggregate_id: UUID, payload: dict):
    """Сохраняет событие в outbox для guaranteed delivery."""
    DomainEventOutbox.objects.create(
        event_type=event_type,
        aggregate_id=aggregate_id,
        payload=payload,
    )


class CourseEnrollmentService:
    @staticmethod
    def enroll_student(course_id: UUID, user: User, delivery_format: str):
        with transaction.atomic():
            enrollment = CourseEnrollment.objects.create(
                user=user,
                course_id=course_id,
                delivery_format=delivery_format,
                status='active',
                enrolled_at=timezone.now(),
            )
            
            
            event = StudentEnrolled(
                enrollment_id=enrollment.id,
                user_id=user.id,
                course_id=course_id,
                delivery_format=delivery_format,
                occurred_at=timezone.now(),
            )
            
            publish_to_outbox(
                event_type='StudentEnrolled',
                aggregate_id=enrollment.id,
                payload=asdict(event),
            )
        
        return enrollment
```

**Обработка Outbox событий (Celery Beat):**

```python

from celery import shared_task
from django.utils import timezone
from shared.models import DomainEventOutbox
from shared.event_handlers import EVENT_HANDLERS
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_outbox_events(self):
    """
    Обрабатывает необработанные события из outbox.
    Запускается каждые 10 секунд через Celery Beat.
    """
    events = DomainEventOutbox.objects.filter(
        processed_at__isnull=True
    ).order_by('occurred_at')[:100]  
    
    for event_record in events:
        try:
            
            handler = EVENT_HANDLERS.get(event_record.event_type)
            if not handler:
                logger.error(f"No handler for event type: {event_record.event_type}")
                event_record.processed_at = timezone.now()
                event_record.last_error = f"No handler for {event_record.event_type}"
                event_record.save()
                continue
            
            
            handler(event_record.payload)
            
            
            event_record.processed_at = timezone.now()
            event_record.save(update_fields=['processed_at'])
            
        except Exception as e:
            event_record.retry_count += 1
            event_record.last_error = str(e)
            event_record.save(update_fields=['retry_count', 'last_error'])
            
            if event_record.retry_count >= 3:
                logger.error(
                    f"Event {event_record.id} ({event_record.event_type}) "
                    f"failed after 3 retries: {e}"
                )
                
            else:
                logger.warning(
                    f"Event {event_record.id} failed (retry {event_record.retry_count}/3): {e}"
                )


from apps.progress.services import ProgressInitialisationService
from apps.certificates.services import CertificateService
from apps.assessment.services import AssessmentService

def handle_student_enrolled(payload: dict):
    """Handler для StudentEnrolled события."""
    ProgressInitialisationService.initialise_progress(
        enrollment_id=payload['enrollment_id']
    )

def handle_course_completed(payload: dict):
    """Handler для CourseCompleted события."""
    CertificateService.generate_certificate(
        enrollment_id=payload['enrollment_id']
    )

def handle_submission_reviewed(payload: dict):
    """Handler для SubmissionReviewed события."""
    AssessmentService.update_response_points(
        response_id=payload['response_id'],
        points=payload['points'],
    )


EVENT_HANDLERS = {
    'StudentEnrolled': handle_student_enrolled,
    'CourseCompleted': handle_course_completed,
    'SubmissionReviewed': handle_submission_reviewed,
    'CertificateIssued': handle_certificate_issued,
    'AssessmentAttemptStarted': handle_assessment_attempt_started,
}


from celery.schedules import crontab

app.conf.beat_schedule = {
    'process-outbox-events': {
        'task': 'shared.tasks.process_outbox_events',
        'schedule': 10.0,  
    },
}
```



| Критерий | Django Signals | Outbox Pattern |
|----------|----------------|----------------|
| Создание aggregate root | ❌ | ✅ |
| Изменение денег/баллов | ❌ | ✅ |
| Внешние интеграции | ❌ | ✅ |
| Audit trail требуется | ❌ | ✅ |
| Counter updates | ✅ | ❌ |
| Cascade completion | ✅ | ❌ |
| Internal domain events | ✅ | ❌ |
| Immediate consistency | ✅ | ❌ |
| Eventual consistency | ❌ | ✅ |



1. **StudentEnrolled** — создаёт CourseProgress (aggregate root)
2. **CourseCompleted** — генерирует Certificate (деньги, compliance)
3. **SubmissionReviewed** — обновляет баллы AssessmentResponse
4. **CertificateIssued** — отправка email (внешний сервис)
5. **AssessmentAttemptStarted** (для project) — создаёт Assignment



1. **LessonCompleted** → increment module counter
2. **ModuleCompleted** → increment course counter
3. **ContentDeleted** → decrement required_content_count
4. **LessonPublished** → создать LessonProgress (fan-out через Celery)
5. **ModuleAssessmentPassed** → unlock next module
6. **AttendanceMarked** → mark lesson completed (offline)



**Обязательно:** Все event handlers должны быть идемпотентными.

```python

def handle_student_enrolled(payload):
    CourseProgress.objects.create(enrollment_id=payload['enrollment_id'])
    


def handle_student_enrolled(payload):
    CourseProgress.objects.get_or_create(
        enrollment_id=payload['enrollment_id'],
        defaults={
            'status': 'not_started',
            'total_modules_count': ...,
        }
    )
    
```



**Метрики для Outbox:**
- Количество необработанных событий (`processed_at IS NULL`)
- Средний lag (разница между `occurred_at` и `processed_at`)
- Количество failed событий (`retry_count >= 3`)

**Алерты:**
- Outbox lag > 5 минут → алерт
- Failed events > 10 → алерт
- Unprocessed events > 1000 → алерт

```python

from prometheus_client import Gauge

outbox_unprocessed = Gauge('outbox_unprocessed_events', 'Number of unprocessed outbox events')
outbox_lag_seconds = Gauge('outbox_lag_seconds', 'Lag between occurred_at and processed_at')
outbox_failed = Gauge('outbox_failed_events', 'Number of failed events')

def update_outbox_metrics():
    outbox_unprocessed.set(DomainEventOutbox.objects.filter(processed_at__isnull=True).count())
    outbox_failed.set(DomainEventOutbox.objects.filter(retry_count__gte=3).count())
    
    
    avg_lag = DomainEventOutbox.objects.filter(
        processed_at__isnull=False
    ).aggregate(
        avg_lag=Avg(F('processed_at') - F('occurred_at'))
    )['avg_lag']
    
    if avg_lag:
        outbox_lag_seconds.set(avg_lag.total_seconds())
```



Когда понадобится выделить домен в микросервис — достаточно заменить Outbox publisher:

```python

def publish_to_outbox(event_type, aggregate_id, payload):
    DomainEventOutbox.objects.create(...)


def publish_to_message_broker(event_type, aggregate_id, payload):
    rabbitmq_channel.basic_publish(
        exchange='domain_events',
        routing_key=event_type,
        body=json.dumps(payload),
    )
```

Код в Services остаётся без изменений — меняется только реализация `publish_*`.

---



- **PostgreSQL 16** — единая база для всех доменов
- UUID primary keys везде (`gen_random_uuid()`)
- Soft delete через `deleted_at TIMESTAMPTZ` (не hard delete)
- Все timestamps — `TIMESTAMPTZ` (с таймзоной)
- Именование таблиц: `{app}_{model}` → `courses_course`, `progress_lessonprogress`

Подробная схема: [`docs/DATABASE.md`](./DATABASE.md)
