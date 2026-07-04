





Перед написанием кода — задокументируй в `docs/`:
1. Обнови `docs/DATABASE.md` — добавь таблицы нового домена
2. Добавь ADR в `docs/DECISIONS.md` для каждого нетривиального решения
3. Обнови `docs/ARCHITECTURE.md` — секция Boundaries
4. Обнови `CLAUDE.md` — карта доменов (статус → СПРОЕКТИРОВАН)



```bash
mkdir -p apps/{domain_name}/api
mkdir -p apps/{domain_name}/tests
touch apps/{domain_name}/{__init__,apps,models,selectors,services,events,tasks,admin}.py
touch apps/{domain_name}/api/{__init__,views,serializers,urls}.py
touch apps/{domain_name}/tests/{__init__,test_selectors,test_services,test_api}.py
```



```
models.py → migrations → selectors.py → services.py → events.py → api/ → tests/
```

---



```python

class CourseCatalogSelector:
    """
    Правила:
    - Только чтение. Никаких мутаций.
    - Принимает user для visibility rules.
    - Возвращает queryset или dataclass.
    - Никогда не вызывает Service.
    """

    @staticmethod
    def get_published_courses(filters: dict, user=None) -> QuerySet:
        qs = Course.objects.filter(
            status='published',
            deleted_at__isnull=True
        )
        if category_slug := filters.get('category_slug'):
            qs = qs.filter(category__slug=category_slug)
        return qs.select_related('category').annotate(
            enrolled_count=Count('courseenrollment')
        ).order_by('-created_at')
```

---



```python

class CourseService:
    """
    Правила:
    - Только запись.
    - Каждый публичный метод — transaction.atomic().
    - Бизнес-правила — здесь.
    - События — через transaction.on_commit().
    - Никогда не возвращает Response объект.
    """

    @staticmethod
    def publish_course(course_id: UUID, actor: User) -> Course:
        with transaction.atomic():
            course = Course.objects.select_for_update().get(pk=course_id)

            
            if not course.module_set.filter(is_published=True).exists():
                raise ValidationError("Course must have at least one published module")

            course.status = 'published'
            course.save(update_fields=['status', 'updated_at'])

            transaction.on_commit(lambda: dispatch(CoursePublished(
                course_id=course.id,
                title=course.title,
                published_by_id=actor.id,
            )))

        return course
```

---



```python

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from django.dispatch import Signal


course_published = Signal()


@dataclass(frozen=True)
class CoursePublished:
    course_id: UUID
    title: str
    slug: str
    published_by_id: UUID
    occurred_at: datetime = field(default_factory=datetime.utcnow)

def dispatch(event: CoursePublished):
    course_published.send(sender=CoursePublished, event=event)


@receiver(course_published)
def handle_course_published(sender, event: CoursePublished, **kwargs):
    
    SearchIndexService.index_course(event.course_id)
```

---



```python

from celery import shared_task
from itertools import islice

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fan_out_content_deletion(self, lesson_id: str, content_id: str):
    """
    Обновляет LessonProgress.required_content_count для всех enrolled студентов.
    Запускается из handle_content_deleted event handler.
    """
    BATCH_SIZE = 500

    qs = LessonProgress.objects.filter(
        lesson_id=lesson_id,
        status__ne='completed',  
        is_active=True,
    ).only('id', 'viewed_required_count')

    
    batch = list(islice(qs.iterator(), BATCH_SIZE))
    while batch:
        ids = [lp.id for lp in batch]
        LessonProgress.objects.filter(id__in=ids).update(
            required_content_count=F('required_content_count') - 1
        )
        
        for lp in batch:
            _check_lesson_completion_safe(lp.enrollment_id, lp.lesson_id)
        batch = list(islice(qs.iterator(), BATCH_SIZE))
```

---



```python

def _check_module_completion(enrollment_id: UUID, module_id: UUID):
    with transaction.atomic():
        
        mp = ModuleProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id,
            module_id=module_id,
        )

        if mp.status == 'completed':
            return  

        
        ModuleProgress.objects.filter(pk=mp.pk).update(
            completed_lessons_count=F('completed_lessons_count') + 1
        )
        mp.refresh_from_db()

        if mp.completed_lessons_count < mp.total_lessons_count:
            return

        
```

---



```python

from shared.models import DomainEventOutbox

def publish_to_outbox(event_type: str, aggregate_id: UUID, payload: dict):
    """
    ADR-029: Outbox Pattern для критичных событий с гарантированной доставкой.
    Используй для событий где потеря = data corruption.
    """
    DomainEventOutbox.objects.create(
        event_type=event_type,
        aggregate_id=aggregate_id,
        payload=payload,
    )


class CourseEnrollmentService:
    """
    StudentEnrolled = критичное событие (создаёт aggregate root CourseProgress).
    Потеря события → студент записан, но прогресс не инициализирован.
    """

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
            
            
            publish_to_outbox(
                event_type='StudentEnrolled',
                aggregate_id=enrollment.id,
                payload={
                    'enrollment_id': str(enrollment.id),
                    'user_id': str(user.id),
                    'course_id': str(course_id),
                    'delivery_format': delivery_format,
                    'occurred_at': timezone.now().isoformat(),
                }
            )
        
        return enrollment


def handle_student_enrolled(payload: dict):
    """
    Handler для StudentEnrolled события.
    Идемпотентен — можно вызвать дважды без side effects.
    """
    ProgressInitialisationService.initialise_progress(
        enrollment_id=payload['enrollment_id']
    )


EVENT_HANDLERS = {
    'StudentEnrolled': handle_student_enrolled,
    'CourseCompleted': handle_course_completed,
    'SubmissionReviewed': handle_submission_reviewed,
}
```

**Когда использовать Outbox:**
- Событие создаёт aggregate root (StudentEnrolled → CourseProgress)
- Событие меняет деньги/баллы (SubmissionReviewed → final_points)
- Событие уходит во внешний сервис (CertificateIssued → email)
- Потеря события = data corruption

**Когда НЕ использовать Outbox:**
- Counter updates (ContentDeleted → decrement count)
- Cascade completion (LessonCompleted → check module)
- Internal domain events где потеря не критична

**Обработка:** Celery Beat task каждые 10 секунд обрабатывает необработанные события из outbox. Retry до 3 раз при ошибке.

---



```python

class SubmissionService:
    """
    ADR-016: Версионирование submissions обязательно.
    Каждая попытка = новый SubmissionRevision.
    """

    @staticmethod
    def submit_revision(submission_id: UUID, content: str, actor: User) -> SubmissionRevision:
        with transaction.atomic():
            submission = Submission.objects.select_for_update().get(pk=submission_id)
            
            
            latest_version = submission.revisions.aggregate(
                Max('version_number')
            )['version_number__max'] or 0
            
            revision = SubmissionRevision.objects.create(
                submission=submission,
                version_number=latest_version + 1,
                content=content,
                submitted_by=actor,
                submitted_at=timezone.now(),
            )
            
            
            submission.current_revision = revision
            submission.status = 'submitted'
            submission.save(update_fields=['current_revision', 'status', 'updated_at'])
            
            transaction.on_commit(lambda: dispatch(SubmissionSubmitted(
                submission_id=submission.id,
                revision_id=revision.id,
                version_number=revision.version_number,
            )))
        
        return revision
```

**Почему версионирование:**
- История попыток студента (для анализа прогресса)
- Возможность вернуться к предыдущей версии
- Audit trail для проверок ментора

---



```python

class AttendanceService:
    """
    ADR-020: Mentor override требует обязательного audit trail.
    """

    @staticmethod
    def override_lesson_completion(
        enrollment_id: UUID,
        lesson_id: UUID,
        actor: User,
        reason: str,
    ):
        with transaction.atomic():
            lp = LessonProgress.objects.select_for_update().get(
                enrollment_id=enrollment_id,
                lesson_id=lesson_id,
            )
            
            
            lp.status = 'completed'
            lp.completed_at = timezone.now()
            lp.override_by = actor
            lp.override_reason = reason  
            lp.override_at = timezone.now()
            lp.save(update_fields=[
                'status', 'completed_at',
                'override_by', 'override_reason', 'override_at',
                'updated_at'
            ])
            
            transaction.on_commit(lambda: dispatch(LessonCompletionOverride(
                enrollment_id=enrollment_id,
                lesson_id=lesson_id,
                overridden_by_id=actor.id,
                reason=reason,
            )))
```

**Почему audit trail:**
- Ответственность ментора (кто и почему переопределил)
- Расследование споров (студент оспаривает оценку)
- Compliance (история изменений критических данных)

---



```python

class CertificateService:
    """
    ADR-025: Certificate = snapshot данных на момент выдачи.
    Не регенерировать при изменении course/user.
    """

    @staticmethod
    def generate_certificate(enrollment_id: UUID) -> Certificate:
        enrollment = CourseEnrollment.objects.select_related(
            'course', 'user__userinfo'
        ).get(pk=enrollment_id)
        
        
        certificate = Certificate.objects.create(
            enrollment_id=enrollment.id,
            user_id=enrollment.user.id,
            course_id=enrollment.course.id,
            
            student_full_name=enrollment.user.userinfo.full_name,
            course_title=enrollment.course.title,
            issued_date=timezone.now().date(),
            verification_code=generate_verification_code(),
            status='valid',
        )
        
        
        pdf_url = generate_certificate_pdf(certificate)
        certificate.pdf_url = pdf_url
        certificate.save(update_fields=['pdf_url'])
        
        return certificate
```

**Почему snapshot:**
- Курс переименовали → сертификат остаётся с прежним названием
- Студент сменил имя → сертификат остаётся на старое имя
- Сертификат = юридический документ (неизменяемый после выдачи)

---





```python

class TestCourseService:
    def test_publish_course_success(self, db, staff_user, draft_course_with_module):
        """Нормальный путь: курс с модулями публикуется."""
        course = CourseService.publish_course(draft_course_with_module.id, staff_user)
        assert course.status == 'published'

    def test_publish_course_no_modules_raises(self, db, staff_user, empty_draft_course):
        """BR-06: нельзя опубликовать пустой курс."""
        with pytest.raises(ValidationError, match="published module"):
            CourseService.publish_course(empty_draft_course.id, staff_user)

    def test_publish_emits_event(self, db, staff_user, publishable_course, mocker):
        """Событие диспетчеризируется после commit."""
        mock = mocker.patch('apps.learning.events.dispatch')
        CourseService.publish_course(publishable_course.id, staff_user)
        mock.assert_called_once()
        assert isinstance(mock.call_args[0][0], CoursePublished)
```



- ✅ Каждое бизнес-правило (BR-*) — негативный тест
- ✅ Идемпотентность event handlers
- ✅ Каскад completion (lesson → module → course)
- ✅ Race condition защита (можно с `threading` или `pytest-xdist`)
- ✅ Permission checks (каждая роль для каждого эндпоинта)
- ✅ Event payload корректность

---



- [ ] Selector не мутирует данные
- [ ] Service использует `transaction.atomic()`
- [ ] Events через `transaction.on_commit()`
- [ ] Счётчики через `F()`, не `+=`
- [ ] Fan-out → Celery task, не inline
- [ ] `select_for_update()` в completion cascade
- [ ] ADR добавлен если решение нетривиальное
- [ ] `docs/DATABASE.md` обновлён для новых таблиц
- [ ] `CLAUDE.md` обновлён если изменился статус домена
- [ ] Тесты покрывают все бизнес-правила
