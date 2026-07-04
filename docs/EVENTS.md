

**Последнее обновление:** 2026-06-07  
**Цель:** Карта всех событий и их связей между доменами

---



События — основной механизм cross-domain взаимодействия в LearnFlow.

**Правила:**
- События dispatch через `transaction.on_commit()` (ПОСЛЕ коммита, не внутри транзакции)
- Payload события самодостаточен (потребитель не должен делать дополнительных запросов)
- Обработчики событий должны быть идемпотентны
- Fan-out операции (обновление N студентов) — только через Celery, не inline

---



**ADR-029:** Гибридный подход — Django Signals (90%) + Outbox Pattern (10%)



**Характеристики:**
- Синхронная обработка в той же транзакции (если не через `on_commit`)
- Immediate consistency
- Нет гарантий доставки при сбое handler
- Нет истории событий

**Когда использовать:**
- ✅ Counter updates (increment/decrement)
- ✅ Cascade completion checks
- ✅ Internal domain events
- ✅ Потеря не критична (можно пересчитать)

**События:** `LessonCompleted`, `ModuleCompleted`, `ContentDeleted`, `ModuleAssessmentPassed`, `AttendanceMarked`



**Характеристики:**
- Асинхронная обработка через Celery Beat (каждые 10 сек)
- Eventual consistency (~10 сек lag)
- At-least-once delivery с retry до 3 раз
- Полная история в БД (audit trail)

**Когда использовать:**
- ✅ Создание aggregate root
- ✅ Изменение денег/баллов/сертификатов
- ✅ Внешние интеграции (email, SMS)
- ✅ Потеря события = data corruption

**События:** `StudentEnrolled`, `CourseCompleted`, `SubmissionReviewed`, `CertificateIssued`, `AssessmentAttemptStarted`



| Вопрос | Да = Outbox | Нет = Signals |
|--------|-------------|---------------|
| Событие создаёт aggregate root? | ✅ Outbox | Django Signals |
| Потеря события = data corruption? | ✅ Outbox | Django Signals |
| Нужен retry при ошибке? | ✅ Outbox | Django Signals |
| Событие меняет деньги/баллы? | ✅ Outbox | Django Signals |
| Событие уходит во внешний сервис? | ✅ Outbox | Django Signals |
| Counter update / cascade check? | Django Signals | ✅ Signals |

**Подробно:** [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) раздел "Event System Implementation"

---




```python
@dataclass
class StudentEnrolled:
    enrollment_id: UUID
    user_id: UUID
    course_id: UUID
    delivery_format: str  
    enrolled_at: datetime
```

**Обработчик:** `UserProgress.handlers.handle_student_enrolled()`  
**Действие:** Инициализировать CourseProgress, ModuleProgress, LessonProgress для студента

---


```python
@dataclass
class LessonPublished:
    lesson_id: UUID
    module_id: UUID
    course_id: UUID
    lesson_order: int
    is_published: bool
```

**Обработчик:** `UserProgress.tasks.fan_out_lesson_unlock.delay()`  
**Действие:** Разблокировать урок для всех enrolled студентов (async Celery)

---


```python
@dataclass
class LessonDeleted:
    lesson_id: UUID
    module_id: UUID
    course_id: UUID
```

**Обработчик:** `UserProgress.tasks.fan_out_lesson_deletion.delay()`  
**Действие:** Пометить LessonProgress как stale (async Celery)

---


```python
@dataclass
class LessonContentAdded:
    lesson_id: UUID
    content_id: UUID
    is_required: bool
```

**Обработчик:** `UserProgress.tasks.fan_out_content_added.delay()`  
**Действие:** Обновить required_content_count для всех enrolled студентов (async Celery)

---


```python
@dataclass
class LessonContentDeleted:
    lesson_id: UUID
    content_id: UUID
    was_required: bool
```

**Обработчик:** `UserProgress.tasks.fan_out_content_deletion.delay()`  
**Действие:** Декрементировать required_content_count (async Celery)

---


```python
@dataclass
class CoursePublished:
    course_id: UUID
    title: str
    slug: str
    published_by_id: UUID
    occurred_at: datetime
```

**Обработчик:** Notifications, Analytics  
**Действие:** Уведомление, аналитика (UserProgress не слушает)

---




```python
@dataclass
class CourseCompleted:
    enrollment_id: UUID
    user_id: UUID
    course_id: UUID
    completed_at: datetime
```

**Обработчик:** `Learning.services.CourseEnrollmentService.complete_enrollment()`  
**Действие:** Обновить CourseEnrollment.status = 'completed', completed_at

---




```python
@dataclass
class ModuleCompleted:
    enrollment_id: UUID
    module_id: UUID
    course_id: UUID
    completed_at: datetime
```

**Обработчик:** `Assessment.handlers.handle_module_completed()`  
**Действие:** Разблокировать ModuleAssessment для студента

---




```python
@dataclass
class ModuleAssessmentPassed:
    enrollment_id: UUID
    module_id: UUID
    assessment_id: UUID
    attempt_id: UUID
    final_score: Decimal
    percentage: Decimal
    occurred_at: datetime
```

**Обработчик:** `UserProgress.services.ModuleProgressService.handle_assessment_passed()`  
**Действие:** 
1. ModuleProgress.assessment_passed = True
2. ModuleProgress.status = 'completed'
3. Разблокировать следующий модуль

---


```python
@dataclass
class ModuleAssessmentFailed:
    enrollment_id: UUID
    module_id: UUID
    assessment_id: UUID
    attempt_id: UUID
    attempt_number: int
    final_score: Decimal
    percentage: Decimal
    max_attempts_reached: bool
    occurred_at: datetime
```

**Обработчик:** Notifications, Analytics  
**Действие:** Уведомление студента, аналитика

---


```python
@dataclass
class AssessmentNeedsMentorReview:
    attempt_id: UUID
    assessment_id: UUID
    module_id: UUID
    enrollment_id: UUID
    student_id: UUID
    pending_items_count: int
    occurred_at: datetime
```

**Обработчик:** `Mentorship.handlers.handle_assessment_needs_review()`  
**Действие:** Добавить в MentorWorkQueue

---




```python
@dataclass
class AssessmentAttemptStarted:
    attempt_id: UUID
    assessment_id: UUID
    enrollment_id: UUID
    user_id: UUID
    project_item_ids: List[UUID]
```

**Обработчик:** `Submissions.handlers.handle_assessment_attempt_started()`  
**Действие:** Создать Assignment + Submission для каждого project item

---




```python
@dataclass
class SubmissionReviewed:
    submission_id: UUID
    assignment_id: UUID
    revision_id: UUID
    student_id: UUID
    mentor_id: UUID
    score: Decimal
    max_score: Decimal
    status: str  
    feedback: str
    reviewed_at: datetime
```

**Обработчик:** `Assessment.handlers.handle_submission_reviewed()`  
**Действие:** 
1. Обновить AssessmentResponse.final_points
2. Проверить не завершён ли весь attempt

---


```python
@dataclass
class SubmissionApproved:
    submission_id: UUID
    assignment_id: UUID
    enrollment_id: UUID
    student_id: UUID
    final_score: Decimal
    occurred_at: datetime
```

**Обработчик:** `UserProgress.handlers.handle_submission_approved()`  
**Действие:** LessonProgress.homework_submitted = True → проверить completion

---




```python
@dataclass
class SubmissionSubmitted:
    submission_id: UUID
    assignment_id: UUID
    revision_id: UUID
    revision_number: int
    student_id: UUID
    enrollment_id: UUID
    submission_type: str
    submitted_at: datetime
```

**Обработчик:** `Mentorship.handlers.handle_submission_submitted()`  
**Действие:** Добавить в MentorWorkQueue

---




```python
@dataclass
class AttendanceMarked:
    session_id: UUID
    student_id: UUID
    enrollment_id: UUID
    lesson_id: UUID
    status: str  
    marked_by_id: UUID
    marked_at: datetime
```

**Обработчик:** `UserProgress.handlers.handle_attendance_marked()`  
**Действие:** 
- Если status='present' → LessonProgress.status = 'completed' (completion_source='mentor_attendance')

---


```python
@dataclass
class OfflineSessionCompleted:
    session_id: UUID
    group_id: UUID
    lesson_id: UUID
    mentor_id: UUID
    attended_students_count: int
    completed_at: datetime
```

**Обработчик:** Notifications, Analytics  
**Действие:** Уведомление, аналитика

---


```python
@dataclass
class LessonCompletionOverride:
    enrollment_id: UUID
    lesson_id: UUID
    mentor_id: UUID
    reason: str
    occurred_at: datetime
```

**Обработчик:** `UserProgress.services.LessonProgressService.handle_mentor_override()`  
**Действие:** LessonProgress.status = 'completed' (completion_source='mentor_override')

---




```python
@dataclass
class CourseCompleted:
    enrollment_id: UUID
    user_id: UUID
    course_id: UUID
    completed_at: datetime
```

**Обработчик:** `Certificates.handlers.handle_course_completed()`  
**Действие:** 
1. Создать Certificate (status='pending')
2. Celery task: generate_certificate.delay()

---




```python
@dataclass
class CertificateIssued:
    certificate_id: UUID
    enrollment_id: UUID
    user_id: UUID
    course_id: UUID
    certificate_number: str
    verification_code: str
    pdf_url: str
    issued_at: datetime
```

**Обработчик:** `Notifications.handlers.handle_certificate_issued()`  
**Действие:** Отправить email студенту с ссылкой на сертификат

---


```python
@dataclass
class CertificateRevoked:
    certificate_id: UUID
    user_id: UUID
    course_id: UUID
    revoked_by_id: UUID
    reason: str
    revoked_at: datetime
```

**Обработчик:** Notifications, Analytics  
**Действие:** Уведомление студента, аналитика

---





```
1. Learning: CourseEnrollmentService.enroll()
      ↓
2. Event: StudentEnrolled
      ↓
3. UserProgress: ProgressInitialisationService.initialise_progress()
   - Создать CourseProgress
   - Создать ModuleProgress для всех модулей
   - Создать LessonProgress для первого урока (unlocked)
   - Остальные уроки: locked
```

---



```
1. Student просматривает контент → API: /progress/lessons/{id}/content/{id}/view/
      ↓
2. UserProgress: ContentViewService.record_view()
   - Инкремент viewed_required_count (F() expression)
   - Проверить: viewed >= required AND homework_submitted (если нужно)
      ↓
3. Если условия выполнены → LessonProgressService._check_lesson_completion()
   - LessonProgress.status = 'completed'
   - Event: LessonCompleted
      ↓
4. LessonProgressService._check_module_completion()
   - Инкремент completed_lessons_count
   - Если все уроки модуля завершены → Event: ModuleCompleted
      ↓
5. ModuleProgressService._check_course_completion()
   - Если все модули завершены → Event: CourseCompleted
```

---



```
1. Student создаёт Submission → POST /api/v1/submissions/assignments/{id}/submit/
      ↓
2. Student делает SubmissionRevision (GitHub URL)
      ↓
3. Event: SubmissionSubmitted
      ↓
4. Mentorship слушает → добавить в MentorWorkQueue
      ↓
5. Mentor проверяет → POST /api/v1/submissions/{id}/review/
      ↓
6. Event: SubmissionReviewed (status='approved')
      ↓
7. Assessment слушает → обновить AssessmentResponse.final_points (если project part of assessment)
      ↓
8. UserProgress слушает → homework_submitted = True → проверить lesson completion
```

---



```
1. Mentor создаёт OfflineSession
      ↓
2. Mentor начинает занятие → POST /api/v1/mentorship/sessions/{id}/start/
      ↓
3. Mentor отмечает Attendance (bulk) → POST /api/v1/mentorship/sessions/{id}/attendance/
   Body: [{ student_id: X, status: 'present' }, ...]
      ↓
4. Event: AttendanceMarked (для каждого студента)
      ↓
5. UserProgress слушает → LessonProgress.status = 'completed' (completion_source='mentor_attendance')
      ↓
6. Cascade: lesson → module → course completion
      ↓
7. Mentor завершает занятие → POST /api/v1/mentorship/sessions/{id}/complete/
      ↓
8. Event: OfflineSessionCompleted
```

---



```
1. UserProgress: последний модуль завершён
      ↓
2. CourseProgressService._check_course_completion()
   - CourseProgress.status = 'completed'
   - Event: CourseCompleted
      ↓
3. Learning слушает → CourseEnrollment.status = 'completed'
      ↓
4. Certificates слушает:
   - CertificateService.request_certificate()
   - Certificate created (status='pending')
      ↓
5. Celery task: generate_certificate.delay()
   - Render HTML from template
   - Generate PDF (WeasyPrint)
   - Upload to S3
   - Certificate.status = 'issued'
      ↓
6. Event: CertificateIssued
      ↓
7. Notifications слушает → send email to student
```

---



```
                  Notifications
                       ↑
                       |
    Learning ←──────→ UserProgress ←──────→ Certificates
       ↓                 ↑                        
       ↓                 |                        
       ↓            Assessment                   
       ↓                 ↑                        
       ↓                 |                        
       └──────→ Submissions ←──────→ Mentorship
                      ↓                   ↓
                      └───────────────────┘
```

**Легенда:**
- `→` — события
- Домены читают друг друга через Selectors
- Домены пишут друг в друга через Events или прямой service call в `on_commit()`

---



1. **Всегда dispatch после коммита:**
   ```python
   with transaction.atomic():
       
       transaction.on_commit(lambda: dispatch(EventName(...)))
   ```

2. **Payload должен быть самодостаточным:**
   ```python
   
   StudentEnrolled(enrollment_id=...)
   
   
   StudentEnrolled(enrollment_id=..., user_id=..., course_id=..., delivery_format=...)
   ```

3. **Обработчики должны быть идемпотентны:**
   ```python
   def handle_student_enrolled(sender, event, **kwargs):
       
       if CourseProgress.objects.filter(enrollment_id=event.enrollment_id).exists():
           return  
       
   ```

4. **Fan-out только через Celery:**
   ```python
   
   for lp in LessonProgress.objects.filter(lesson_id=lesson_id):
       lp.required_content_count = F('required_content_count') + 1
       lp.save()
   
   
   tasks.fan_out_content_added.delay(lesson_id=lesson_id, content_id=content_id)
   ```
