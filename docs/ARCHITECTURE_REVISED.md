

**Status:** Active  
**Last Updated:** 2026-06-08  
**Supersedes:** Original ARCHITECTURE.md patterns  
**Related ADRs:** ADR-032 (Enrollment Extraction), ADR-033 (Feature-Slicing)

---



LearnFlow использует **Feature-Sliced Modular Monolith** с элементами **Pragmatic DDD**:
- **Django ORM** как основа (не скрываем за Repository Pattern)
- **CQRS** для разделения чтения и записи (Commands/Queries)
- **Event-Driven** интеграция между доменами (Django Signals + Outbox Pattern)
- **Feature-Sliced** структура — один файл = одна модель/команда/query (~150 строк)

**Ключевой принцип:** "Optimize for deletion, not creation"

Когда нужно изменить модель Assessment — редактируешь `assessment/domain/models/assessment.py`, а не ищешь её в 1500-строчном `models.py`.

---





```
courses/
├── models.py         
├── views.py          
├── serializers.py    
└── services.py       
```

**Проблемы:**
- Невозможно навигировать в больших файлах
- Слабое разделение ответственности
- Тяжело экстрагировать в микросервисы
- Nightmare для команды 10+ разработчиков

**Вердикт:** 2/10 — не подходит для масштабирования

---



```
learning/
├── models.py
├── selectors.py
├── services.py
├── events.py
└── api/
    ├── views.py
    └── serializers.py
```

**Проблемы:**
- `models.py` всё равно разрастается до 1000+ строк
- `selectors.py` и `services.py` тоже станут огромными
- Нет чёткого разделения на фичи

**Вердикт:** 6/10 — хорошее начало, требует улучшения

---



```
learning/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── aggregates/
│   ├── repositories/ (interfaces)
│   └── domain_services/
├── application/
│   ├── use_cases/
│   ├── commands/
│   ├── queries/
│   └── dtos/
├── infrastructure/
│   ├── persistence/
│   │   ├── django_models/
│   │   └── repositories/ (impl)
│   └── external/
└── presentation/
```

**Проблемы:**
- **Over-engineering** для Django
- Django ORM — не "persistence detail", а core framework
- Repository Pattern поверх ORM = ненужная индирекция
- DTO everywhere = дублирование
- Junior developers не поймут Hexagonal
- 3x больше файлов для той же функциональности

**Вердикт:** 4/10 — чистая архитектура, но непрактично для Django

---



```
learning/
├── domain/
│   ├── models/              
│   │   ├── course.py
│   │   ├── module.py
│   │   └── lesson.py
│   ├── value_objects/
│   ├── events/
│   └── services/
├── application/
│   ├── commands/            
│   │   ├── create_course.py
│   │   └── publish_course.py
│   ├── queries/             
│   │   ├── course_catalog.py
│   │   └── course_detail.py
│   └── handlers/
├── infrastructure/
│   └── tasks/
└── presentation/
    └── rest/
        ├── courses/         
        │   ├── create.py
        │   ├── detail.py
        │   ├── list.py
        │   └── serializers/
        │       ├── create.py
        │       ├── detail.py
        │       └── list.py
        └── enrollments/
```

**Преимущества:**
- ✅ Django ORM используется напрямую
- ✅ CQRS без over-engineering
- ✅ Файлы ~150 строк каждый
- ✅ Легко найти и изменить код
- ✅ Легко экстрагировать в микросервис
- ✅ Junior developers понимают структуру

**Вердикт:** 9/10 — оптимальный баланс для Django monolith

---





**Что здесь живёт:**
- Django Models (aggregate roots)
- Managers (custom QuerySets)
- Value Objects
- Domain Services (сложная бизнес-логика)

**Что НЕ живёт:**
- API serializers (это `presentation/`)
- Celery tasks (это `infrastructure/`)
- Database queries для views (это `application/queries/`)

**Пример:**

```python

from django.db import models
from shared.domain.base_models import UUIDModel, TimestampedModel

class Course(UUIDModel, TimestampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    status = models.CharField(max_length=20, choices=CourseStatus.choices)

    def can_be_published(self) -> bool:
        """Domain invariant: BR-06"""
        return self.modules.filter(is_published=True).exists()

    class Meta:
        db_table = 'learning_course'
```

```python

class PublicationDomainService:
    """Complex business logic spanning multiple aggregates."""
    
    @staticmethod
    def can_course_be_published(course) -> tuple[bool, str]:
        if not course.modules.filter(is_published=True).exists():
            return False, "Course must have at least one published module"
        
        if not course.instructor:
            return False, "Course must have an instructor"
        
        return True, ""
```

---



**Что здесь живёт:**
- Commands (write operations — CQRS)
- Queries (read operations — CQRS)
- Events (domain events + handlers)

**Commands Example:**

```python

from dataclasses import dataclass
from uuid import UUID
from django.db import transaction
from learning.domain.models.course import Course
from learning.domain.services.publication import PublicationDomainService
from shared.infrastructure.outbox.publisher import publish_to_outbox

@dataclass
class PublishCourseCommand:
    course_id: UUID
    published_by_id: UUID

class PublishCourseHandler:
    """Command handler following CQRS pattern."""
    
    @staticmethod
    def handle(cmd: PublishCourseCommand) -> Course:
        with transaction.atomic():
            
            course = Course.objects.select_for_update().get(pk=cmd.course_id)
            
            
            can_publish, reason = PublicationDomainService.can_course_be_published(course)
            if not can_publish:
                raise ValidationError(reason)
            
            
            course.status = 'published'
            course.published_at = timezone.now()
            course.published_by_id = cmd.published_by_id
            course.save(update_fields=['status', 'published_at', 'published_by'])
            
            
            transaction.on_commit(lambda: publish_to_outbox(
                event_type='CoursePublished',
                aggregate_id=course.id,
                payload={
                    'course_id': str(course.id),
                    'title': course.title,
                    'published_at': course.published_at.isoformat(),
                }
            ))
        
        return course
```

**Queries Example:**

```python

from dataclasses import dataclass
from typing import Optional
from django.db.models import QuerySet, Count, Q
from learning.domain.models.course import Course

@dataclass
class CourseCatalogQuery:
    category_slug: Optional[str] = None
    search: Optional[str] = None
    status: str = 'published'

class CourseCatalogQueryHandler:
    """Query handler following CQRS pattern."""
    
    @staticmethod
    def handle(query: CourseCatalogQuery) -> QuerySet[Course]:
        qs = Course.objects.filter(
            status=query.status,
            deleted_at__isnull=True,
        )
        
        if query.category_slug:
            qs = qs.filter(category__slug=query.category_slug)
        
        if query.search:
            qs = qs.filter(
                Q(title__icontains=query.search) |
                Q(description__icontains=query.search)
            )
        
        return qs.select_related('category').annotate(
            enrolled_count=Count('enrollments')
        ).order_by('-created_at')
```

---



**Что здесь живёт:**
- Celery tasks
- External integrations (S3, ClamAV, SendGrid)
- Background jobs

```python

from celery import shared_task
from submissions.domain.models.submission import SubmissionFile
from submissions.infrastructure.integrations.clamav_client import ClamAVClient

@shared_task(bind=True, max_retries=3)
def scan_submission_file(self, file_id: str):
    """Scan uploaded file with ClamAV."""
    file_obj = SubmissionFile.objects.get(pk=file_id)
    
    try:
        client = ClamAVClient()
        result = client.scan(file_obj.s3_key)
        
        if result == 'CLEAN':
            file_obj.scan_status = 'passed'
        else:
            file_obj.scan_status = 'failed'
        
        file_obj.save()
    except Exception as e:
        file_obj.scan_status = 'error'
        file_obj.save()
        raise self.retry(exc=e, countdown=60)
```

---



**Что здесь живёт:**
- REST APIs (DRF ViewSets/APIViews)
- Serializers
- GraphQL resolvers (future)
- WebSocket consumers (future)

**REST API Example:**

```python

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from learning.application.commands.create_course import CreateCourseCommand, CreateCourseHandler
from learning.presentation.rest.courses.serializers.create import CreateCourseSerializer

class CreateCourseAPIView(APIView):
    """
    POST /api/v1/learning/
    
    Feature-based endpoint — single responsibility.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        serializer = CreateCourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        cmd = CreateCourseCommand(
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            category_id=serializer.validated_data['category_id'],
            created_by_id=request.user.id,
        )
        
        
        course = CreateCourseHandler.handle(cmd)
        
        
        response_serializer = CourseDetailSerializer(course)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
```

---





```python

from shared.domain.base_models import UUIDModel
from django.db import models


from learning.domain.models.course import Course
from learning.domain.services.publication import PublicationDomainService
from shared.infrastructure.outbox.publisher import publish_to_outbox


from learning.domain.models.course import Course
from learning.application.commands.publish_course import PublishCourseHandler


from learning.application.commands.create_course import CreateCourseHandler
from learning.application.queries.course_catalog import CourseCatalogQueryHandler
```



```python

from learning.application.commands.create_course import CreateCourseHandler  


from learning.infrastructure.tasks import publish_course_task  


from progress.domain.models.course_progress import CourseProgress  


from progress.domain.services.initialization import ProgressInitService  
```



```
Presentation → Application → Domain ← Infrastructure
                    ↓
                  Events
                    ↓
            Other Domains (via handlers)
```

**Правило:** Зависимости всегда направлены внутрь. Domain ни от чего не зависит.

---





**Enrollment Domain = Integration Hub** для всей системы.

```
Payment → Enrollment → Progress → Certificates
            ↓
        Learning
```



```python

from django.dispatch import receiver
from payment.domain.events.payment_succeeded import payment_succeeded_signal
from enrollment.application.commands.activate_enrollment import ActivateEnrollmentHandler

@receiver(payment_succeeded_signal)
def handle_payment_succeeded(sender, payment_id, enrollment_id, **kwargs):
    """When payment succeeds → activate enrollment."""
    ActivateEnrollmentHandler.handle(enrollment_id, payment_id)
```

```python

from django.db import transaction
from enrollment.domain.models.enrollment import CourseEnrollment
from enrollment.domain.events.access_granted import access_granted_signal

class ActivateEnrollmentHandler:
    @staticmethod
    def handle(enrollment_id, payment_id):
        with transaction.atomic():
            enrollment = CourseEnrollment.objects.select_for_update().get(pk=enrollment_id)
            
            enrollment.status = 'active'
            enrollment.payment_id = payment_id
            enrollment.payment_status = 'paid'
            enrollment.save(update_fields=['status', 'payment_id', 'payment_status'])
            
            
            transaction.on_commit(lambda: access_granted_signal.send(
                sender=CourseEnrollment,
                enrollment_id=enrollment.id,
                user_id=enrollment.user_id,
                course_id=enrollment.course_id,
            ))
```



| Domain        | Owns                           | Reads From                | Writes To (via events)     |
|---------------|--------------------------------|---------------------------|----------------------------|
| Identity      | User, Role, Profile            | —                         | —                          |
| Learning      | Course, Module, Lesson         | Enrollment                | Enrollment                 |
| Enrollment    | CourseEnrollment, AccessRule   | Learning, Payment         | Progress, Certificates     |
| Progress      | CourseProgress, LessonProgress | Enrollment, Learning      | Enrollment, Assessment     |
| Payment       | Payment, Transaction           | Enrollment                | Enrollment                 |
| Assessment    | Assessment, Attempt            | Enrollment, Progress      | Progress, Submissions      |
| Submissions   | Assignment, Submission         | Enrollment, Assessment    | Assessment, Mentorship     |
| Mentorship    | MentorGroup, Attendance        | Enrollment, Submissions   | Progress                   |
| Certificates  | Certificate, Template          | Enrollment                | Notifications              |

---





```
assessment/
├── domain/
│   ├── models/
│   │   ├── __init__.py           
│   │   ├── assessment.py         
│   │   ├── item.py               
│   │   ├── attempt.py            
│   │   ├── response.py           
│   │   ├── coding.py             
│   │   ├── review.py             
│   │   └── part.py               
│   │
│   ├── value_objects/
│   │   ├── __init__.py
│   │   ├── grading_status.py    
│   │   ├── score.py              
│   │   └── time_limit.py
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   ├── assessment_passed.py
│   │   ├── assessment_failed.py
│   │   └── attempt_started.py   
│   │
│   └── services/
│       ├── __init__.py
│       ├── grading.py            
│       ├── auto_grader.py        
│       └── mentor_review.py      
│
├── application/
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── start_attempt.py      
│   │   ├── submit_response.py    
│   │   └── finalize_attempt.py   
│   │
│   ├── queries/
│   │   ├── __init__.py
│   │   ├── assessment_detail.py
│   │   ├── attempt_detail.py
│   │   └── available_assessments.py
│   │
│   └── handlers/
│       ├── __init__.py
│       └── event_handlers.py     
│
├── infrastructure/
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── coding_execution.py   
│   │   └── auto_grading.py       
│   │
│   └── integrations/
│       └── sandbox_client.py     
│
├── presentation/
│   ├── rest/
│   │   ├── assessments/
│   │   │   ├── __init__.py
│   │   │   ├── create.py         
│   │   │   ├── update.py         
│   │   │   ├── delete.py         
│   │   │   ├── detail.py         
│   │   │   ├── list.py           
│   │   │   └── serializers/
│   │   │       ├── create.py     
│   │   │       ├── update.py     
│   │   │       ├── detail.py     
│   │   │       └── list.py       
│   │   │
│   │   ├── attempts/
│   │   │   ├── start.py          
│   │   │   ├── submit_response.py
│   │   │   ├── finalize.py
│   │   │   └── serializers/
│   │   │
│   │   └── reviews/
│   │       ├── mentor_override.py
│   │       └── serializers/
│   │
│   └── graphql/                  
│
├── admin/
│   ├── __init__.py
│   ├── assessment.py             
│   └── filters.py
│
└── tests/
    ├── domain/
    ├── application/
    ├── infrastructure/
    └── presentation/
```

---



**⚠️ DANGER ZONE:** `shared/` легко превращается в свалку.



```
shared/
├── domain/
│   ├── base_models.py          
│   ├── value_objects/          
│   │   ├── email.py
│   │   ├── money.py
│   │   └── phone_number.py
│   └── exceptions.py           
│
├── application/
│   ├── base_command.py         
│   ├── base_query.py           
│   └── pagination.py           
│
├── infrastructure/
│   ├── outbox/
│   │   ├── models.py           
│   │   ├── publisher.py
│   │   └── processor.py
│   ├── storage/
│   │   └── s3_client.py        
│   └── monitoring/
│       └── tracing.py
│
└── presentation/
    ├── permissions.py          
    └── pagination.py           
```



```python

shared/utils.py
shared/helpers.py


shared/constants.py


shared/mixins.py


shared/validators.py


shared/decorators.py


shared/services.py
```

**Правило:** Если сомневаешься — НЕ клади в `shared/`. Лучше дублировать код.

---





```bash

mkdir -p assessment/domain/models
mkdir -p assessment/domain/events
mkdir -p assessment/domain/value_objects
mkdir -p assessment/domain/services

mkdir -p assessment/application/commands
mkdir -p assessment/application/queries
mkdir -p assessment/application/handlers

mkdir -p assessment/infrastructure/tasks
mkdir -p assessment/infrastructure/integrations

mkdir -p assessment/presentation/rest/assessments/serializers
mkdir -p assessment/presentation/rest/attempts/serializers
```



```bash








```



```python

from assessment.models import ModuleAssessment


from assessment.domain.models.assessment import ModuleAssessment
```



```python



```

---



| Benefit              | Description                                                      |
|----------------------|------------------------------------------------------------------|
| Navigability         | Find code in seconds: `assessment/domain/models/attempt.py`      |
| Maintainability      | Change one model = change one file (~150 lines)                  |
| Onboarding           | New developers understand structure in 30 minutes                |
| Testability          | Test Commands/Queries in isolation                               |
| Microservice Ready   | Extract domain → microservice in days, not months                |
| Code Review          | Review one feature = review one PR with 5-10 files               |
| Parallel Development | 10 developers work on different features without conflicts       |
| Scalability          | Add new features without touching existing code                  |

---





```python

class ModuleAssessment(models.Model): ...
class AssessmentItem(models.Model): ...
class AssessmentAttempt(models.Model): ...

```

```python

class ModuleAssessment(models.Model): ...
```



```python

class AssessmentSerializer(serializers.ModelSerializer): ...
class CreateAssessmentSerializer(serializers.Serializer): ...
class UpdateAssessmentSerializer(serializers.Serializer): ...

```

```python

class CreateAssessmentSerializer(serializers.Serializer): ...
```



```python

from progress.domain.models.course_progress import CourseProgress


from shared.infrastructure.outbox.publisher import publish_to_outbox
```



```python

shared/utils.py
shared/helpers.py
shared/assessment_utils.py  


assessment/domain/services/grading_utils.py
```

---



- ADR-029: Event System (Signals + Outbox)
- ADR-030: Celery + Redis
- ADR-031: S3-Compatible Storage
- ADR-032: Enrollment Domain Extraction
- ADR-033: Feature-Sliced Domain Structure

**Related Designs:**
- docs/design/ENROLLMENT_DOMAIN_V1.md
- docs/design/PAYMENT_DOMAIN_V1.md
- docs/design/ASSESSMENT_DOMAIN_V3.md

---

**Last Updated:** 2026-06-08  
**Next Review:** 2026-09-08 (after Phase 1B implementation)
