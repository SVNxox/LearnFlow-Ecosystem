

> This file is read by Claude Code at the start of every session.
> It is the single source of truth for how AI should work with this codebase.
> Keep it updated as the project evolves.

---



**LearnFlow** — образовательная платформа.
- Поддерживает **online** (самостоятельное) и **offline** (групповое с ментором) обучение.
- Один курс работает для обоих форматов. Режим хранится в `CourseEnrollment.delivery_format`.
- Роли: `Student`, `Mentor`, `Staff`, `Admin`.

**Стек:** 
- Django monolith · PostgreSQL · Celery + Redis · Python 3.12+
- Storage: S3-compatible (Cloudflare R2 production, MinIO dev)
- Фоновые задачи: Celery 5.x с 4 очередями (default, fan_out, coding, pdf)

**Архитектура:** Модульный монолит → будущая экстракция в сервисы.

**Инфраструктурные решения:**
- ADR-030: Celery + Redis для фоновых задач
- ADR-031: S3-compatible storage (Cloudflare R2)

---





Перед реализацией новой функциональности, исправлением ошибок, рефакторингом, созданием миграций, проектированием моделей, API, сервисов, событий или тестов необходимо изучить соответствующую документацию.

**Обязательный порядок чтения для каждой новой сессии:**

1. `CLAUDE.md`
2. `docs/DOMAIN.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DATABASE.md`



Изучи соответствующий документ в зависимости от задачи:

| Задача                                        | Документ               |
| --------------------------------------------- | ---------------------- |
| Изменение структуры БД                        | `docs/DATABASE.md`     |
| Разработка или изменение API                  | `docs/API.md`          |
| Вопросы безопасности и прав доступа           | `docs/SECURITY.md`     |
| Инфраструктура, окружение и деплой            | `docs/DEPLOYMENT.md`   |
| Добавление нового домена или функциональности | `docs/CONTRIBUTING.md` |
| Архитектурные решения и их обоснование        | `docs/DECISIONS.md`    |
| Будущие планы развития проекта                | `docs/ROADMAP.md`      |



Перед реализацией домена обязательно изучи его дизайн-документ.

Learning Domain:
- docs/design/learnflow-learning-domain-v2.md
- docs/design/learnflow-application-layer.md

UserProgress Domain:
- docs/design/learnflow-userprogress-review-v2.md

Assessment Domain v3:
- docs/design/ASSESSMENT_DOMAIN_V3.md

Submissions Domain v1:
- docs/design/SUBMISSIONS_DOMAIN_V1.md

Mentorship Domain v1:
- docs/design/MENTORSHIP_DOMAIN_V1.md

Certificates Domain v1:
- docs/design/CERTIFICATES_DOMAIN_V1.md

Если реализация противоречит дизайн-документу, сначала сообщи о противоречии и запроси уточнение.



Файл:

`docs/CONVERSATION_LOG.md`



Хранит краткую историю важных обсуждений, договорённостей и решений по проекту.



После завершения задачи проверь:

* Изменились ли бизнес-правила.
* Появились ли новые инварианты.
* Были ли приняты архитектурные решения.
* Изменились ли границы доменов.
* Появились ли новые требования к системе.
* Были ли приняты важные технические решения с долгосрочными последствиями.

Если да — обнови `docs/CONVERSATION_LOG.md`.



* Архитектурные обсуждения.
* Изменения доменной модели.
* Новые бизнес-требования.
* Важные договорённости.
* Причины принятия решений.
* Ограничения и инварианты системы.



* Исправление опечаток.
* Форматирование кода.
* Незначительные рефакторинги.
* Рутинные изменения.
* Временные ошибки и отладку.
* Логи выполнения команд.



Каждая запись должна содержать:

* Дату
* Тему обсуждения
* Краткий контекст
* Итоговое решение
* Статус (Принято / Отложено / Отклонено)



Если решение является официальным архитектурным решением проекта, дополнительно обнови `docs/DECISIONS.md`.

`CONVERSATION_LOG.md` не заменяет `DECISIONS.md`, а дополняет его историей обсуждений.



* Не предполагай бизнес-логику без проверки документации.
* Не предполагай структуру базы данных без проверки документации.
* Не предполагай права доступа без проверки документации.
* Не предполагай рабочие процессы без проверки документации.
* Не придумывай поля моделей, связи, статусы или события, которых нет в документации.
* Если документация отсутствует, устарела, противоречива или недостаточна — остановись и запроси уточнение перед внесением изменений.



**ОБЯЗАТЕЛЬНО:** Используй `docs/PRE_IMPLEMENTATION_CHECKLIST.md` перед написанием любого production-ready кода.

Перед написанием кода кратко опиши:

1. Какие документы были прочитаны.
2. Какие домены затрагиваются.
3. Как ты понимаешь задачу.
4. План реализации на высоком уровне.
5. **Какие разделы PRE_IMPLEMENTATION_CHECKLIST применимы к этой задаче.**

Не приступай к написанию кода, пока не сформировано понимание задачи и затронутых доменов.

**Чеклист покрывает 14 критичных областей:**
1. Database Engineering (N+1, индексы, транзакции)
2. Domain Engineering & DDD (aggregate boundaries, cross-domain coupling)
3. Concurrency & Race Conditions (idempotency, TOCTOU, locks)
4. Event Architecture (Outbox vs Signals, idempotency handlers)
5. Caching Strategy (invalidation, stampede protection)
6. Security (IDOR, OWASP Top 10, secrets)
7. File Storage & Uploads (presigned URLs, virus scanning)
8. Code Execution / Sandbox (isolation, resource limits)
9. Observability (structured logging, monitoring)
10. Testing Strategy (unit, integration, performance tests)
11. Schema Evolution & Migrations (zero-downtime, rollback)
12. Performance (query optimization, pagination)
13. Audit Trail & Data Integrity (history, soft delete, timezones)
14. Scalability & Infrastructure (feature flags, auto-scaling, GDPR)

---



**Архитектура:** Feature-Sliced Modular Monolith (Pragmatic DDD)

**Принцип:** "Optimize for deletion, not creation" — изменение одной модели/фичи = изменение одного файла.

```
learnflow/
├── shared/                    
│   ├── domain/
│   │   ├── base_models.py    
│   │   ├── value_objects/    
│   │   └── exceptions.py
│   ├── application/
│   │   ├── base_command.py
│   │   ├── base_query.py
│   │   └── pagination.py
│   ├── infrastructure/
│   │   ├── outbox/           
│   │   ├── storage/          
│   │   └── monitoring/
│   └── presentation/
│       ├── permissions.py
│       └── pagination.py
│
├── accounts/                  
│   ├── domain/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   └── profile.py
│   │   └── value_objects/
│   ├── application/
│   │   ├── commands/
│   │   └── queries/
│   └── presentation/rest/
│       ├── auth/
│       └── profile/
│
├── learning/                  
│   ├── domain/
│   │   ├── models/           
│   │   │   ├── course.py     
│   │   │   ├── module.py     
│   │   │   ├── lesson.py     
│   │   │   └── content.py    
│   │   ├── value_objects/
│   │   │   ├── course_slug.py
│   │   │   └── delivery_format.py
│   │   ├── events/
│   │   │   ├── course_published.py
│   │   │   └── lesson_published.py
│   │   └── services/
│   │       └── publication.py
│   ├── application/
│   │   ├── commands/
│   │   │   ├── create_course.py
│   │   │   ├── publish_course.py
│   │   │   └── create_lesson.py
│   │   ├── queries/
│   │   │   ├── course_catalog.py
│   │   │   ├── course_detail.py
│   │   │   └── lesson_detail.py
│   │   └── handlers/
│   │       └── event_handlers.py
│   ├── infrastructure/
│   │   └── tasks/
│   │       └── fan_out_content_update.py
│   ├── presentation/rest/
│   │   ├── courses/
│   │   │   ├── create.py
│   │   │   ├── update.py
│   │   │   ├── publish.py
│   │   │   ├── detail.py
│   │   │   ├── list.py
│   │   │   └── serializers/
│   │   │       ├── create.py
│   │   │       ├── update.py
│   │   │       ├── detail.py
│   │   │       └── list.py
│   │   └── lessons/
│   │       ├── detail.py
│   │       └── serializers/
│   ├── admin/
│   │   ├── course.py
│   │   └── lesson.py
│   └── tests/
│
├── enrollment/                
│   ├── domain/                
│   │   ├── models/
│   │   │   ├── enrollment.py      
│   │   │   ├── access_rule.py
│   │   │   ├── prerequisite.py
│   │   │   └── waitlist.py
│   │   ├── value_objects/
│   │   │   ├── enrollment_status.py
│   │   │   ├── delivery_format.py
│   │   │   └── access_level.py
│   │   ├── events/
│   │   │   ├── student_enrolled.py       
│   │   │   ├── enrollment_completed.py   
│   │   │   ├── access_granted.py
│   │   │   └── access_revoked.py
│   │   └── services/
│   │       ├── enrollment_service.py
│   │       ├── access_control.py
│   │       └── prerequisite_checker.py
│   ├── application/
│   │   ├── commands/
│   │   │   ├── enroll_student.py
│   │   │   ├── drop_enrollment.py
│   │   │   ├── suspend_enrollment.py
│   │   │   └── reactivate_enrollment.py
│   │   ├── queries/
│   │   │   ├── enrollment_detail.py
│   │   │   ├── my_enrollments.py
│   │   │   └── check_access.py
│   │   └── handlers/
│   ├── infrastructure/tasks/
│   ├── presentation/rest/
│   │   ├── enrollments/
│   │   │   ├── create.py
│   │   │   ├── detail.py
│   │   │   ├── list.py
│   │   │   ├── drop.py
│   │   │   └── serializers/
│   │   └── access/
│   ├── admin/
│   └── tests/
│
├── progress/                  
│   ├── domain/
│   │   ├── models/
│   │   │   ├── course_progress.py
│   │   │   ├── module_progress.py
│   │   │   └── lesson_progress.py
│   │   ├── events/
│   │   │   ├── lesson_completed.py    
│   │   │   ├── module_completed.py    
│   │   │   └── course_completed.py    
│   │   └── services/
│   │       ├── initialization.py
│   │       └── completion_cascade.py
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── handlers/
│   ├── presentation/rest/
│   │   ├── progress/
│   │   └── completion/
│   └── tests/
│
├── payment/                   
│   ├── domain/                
│   │   ├── models/
│   │   │   ├── payment.py
│   │   │   ├── transaction.py
│   │   │   ├── refund.py
│   │   │   └── subscription.py
│   │   ├── value_objects/
│   │   │   ├── money.py
│   │   │   └── payment_status.py
│   │   ├── events/
│   │   │   ├── payment_succeeded.py   
│   │   │   ├── payment_failed.py      
│   │   │   └── refund_issued.py       
│   │   └── services/
│   │       ├── payment_processor.py
│   │       └── refund_processor.py
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── handlers/
│   ├── infrastructure/
│   │   ├── tasks/
│   │   └── integrations/
│   │       ├── stripe_client.py
│   │       └── payme_client.py     
│   ├── presentation/rest/
│   │   ├── payments/
│   │   │   ├── create.py
│   │   │   ├── webhook.py
│   │   │   └── serializers/
│   │   └── refunds/
│   └── tests/
│
├── assessment/                
│   ├── domain/
│   │   ├── models/           
│   │   │   ├── assessment.py     
│   │   │   ├── item.py           
│   │   │   ├── attempt.py        
│   │   │   ├── response.py       
│   │   │   ├── coding.py         
│   │   │   ├── review.py         
│   │   │   └── part.py           
│   │   ├── value_objects/
│   │   │   ├── grading_status.py
│   │   │   ├── score.py
│   │   │   └── time_limit.py
│   │   ├── events/
│   │   │   ├── assessment_passed.py
│   │   │   ├── assessment_failed.py
│   │   │   └── attempt_started.py    
│   │   └── services/
│   │       ├── grading.py
│   │       ├── auto_grader.py
│   │       └── mentor_review.py
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── handlers/
│   ├── infrastructure/
│   │   ├── tasks/
│   │   └── integrations/
│   │       └── sandbox_client.py
│   ├── presentation/rest/
│   │   ├── assessments/
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
│   │   ├── attempts/
│   │   │   ├── start.py
│   │   │   ├── submit_response.py
│   │   │   ├── finalize.py
│   │   │   └── serializers/
│   │   └── reviews/
│   ├── admin/
│   └── tests/
│
├── submissions/               
│   ├── domain/
│   │   ├── models/
│   │   │   ├── assignment.py
│   │   │   ├── submission.py
│   │   │   ├── revision.py
│   │   │   ├── file.py
│   │   │   └── review.py
│   │   ├── events/
│   │   └── services/
│   ├── application/
│   ├── infrastructure/
│   │   ├── tasks/
│   │   └── integrations/
│   │       └── clamav_client.py
│   ├── presentation/rest/
│   │   ├── submissions/
│   │   └── reviews/
│   └── tests/
│
├── mentorship/                
│   ├── domain/
│   │   ├── models/
│   │   │   ├── mentor_group.py
│   │   │   ├── offline_session.py
│   │   │   └── attendance.py
│   │   ├── events/
│   │   └── services/
│   ├── application/
│   ├── presentation/rest/
│   │   ├── attendance/
│   │   └── work_queue/
│   └── tests/
│
├── certificates/              
│   ├── domain/
│   │   ├── models/
│   │   │   ├── certificate.py
│   │   │   ├── template.py
│   │   │   └── audit_log.py
│   │   ├── value_objects/
│   │   │   └── verification_code.py
│   │   ├── events/
│   │   └── services/
│   ├── application/
│   ├── infrastructure/
│   │   ├── tasks/
│   │   └── integrations/
│   │       └── pdf_generator.py
│   ├── presentation/rest/
│   │   ├── certificates/
│   │   └── verification/      
│   └── tests/
│
├── notifications/             
├── analytics/                 
│
├── learnflow/                 
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py
│
├── docs/                      
│   ├── ARCHITECTURE_REVISED.md
│   ├── design/
│   │   ├── ENROLLMENT_DOMAIN_V1.md
│   │   └── PAYMENT_DOMAIN_V1.md
│   └── DECISIONS.md           
│
└── CLAUDE.md                  
```



**⚠️ CRITICAL:** `shared/` может превратиться в "мусорку" с `utils.py`, `helpers.py`, `constants.py`.

**РАЗРЕШЕНО в shared/:**
- `domain/base_models.py` — UUIDModel, TimestampedModel
- `domain/value_objects/` — Email, Money, PhoneNumber (только универсальные)
- `domain/exceptions.py` — DomainException, базовые исключения
- `application/base_command.py` — Abstract base для Commands
- `application/base_query.py` — Abstract base для Queries
- `infrastructure/outbox/` — DomainEventOutbox (ADR-029)
- `infrastructure/storage/` — S3Client wrapper
- `presentation/permissions.py` — Переиспользуемые DRF permissions

**ЗАПРЕЩЕНО в shared/:**
- ❌ `utils.py`, `helpers.py` — слишком общее, неясная ответственность
- ❌ `constants.py` — константы принадлежат доменам
- ❌ `mixins.py` — миксины обычно domain-specific
- ❌ `validators.py` — валидаторы принадлежат доменам
- ❌ `decorators.py` — декораторы обычно domain-specific
- ❌ Бизнес-логика — всегда в конкретном домене

**Правило:** Если сомневаешься, куда положить код — **не клади в shared/**. Лучше дублировать, чем создавать общую зависимость.

---





```
Views / API → Selector (READ) → Model (только чтение)
Views / API → Service (WRITE) → Model (только запись)
```

- **Selector** — только чтение. Никаких мутаций. Возвращает queryset или dataclass.
- **Service** — только запись. Все бизнес-правила здесь. Всегда `transaction.atomic()`.
- **Views** — никогда не пишут в модели напрямую. Только через Service.



**ADR-029:** Гибридный подход — Django Signals для обычных событий, Outbox Pattern для критичных.

```python

with transaction.atomic():
    
    transaction.on_commit(lambda: dispatch_event(...))
```

**Django Signals (90% событий):**
- Обычные события где потеря не критична
- Immediate consistency
- Примеры: `LessonCompleted`, `ModuleCompleted`, `ContentDeleted`

```python

from django.dispatch import Signal
lesson_completed = Signal()


transaction.on_commit(lambda: lesson_completed.send(
    sender=LessonProgress,
    enrollment_id=enrollment_id,
    lesson_id=lesson_id,
))


@receiver(lesson_completed)
def handle_lesson_completed(sender, enrollment_id, lesson_id, **kwargs):
    _check_module_completion(enrollment_id, lesson_id)
```

**Outbox Pattern (10% критичных событий):**
- Критичные события требующие guaranteed delivery
- Eventual consistency (обработка через Celery Beat каждые 10 сек)
- Примеры: `StudentEnrolled`, `CourseCompleted`, `SubmissionReviewed`, `CertificateIssued`

```python

with transaction.atomic():
    enrollment = CourseEnrollment.objects.create(...)
    
    
    publish_to_outbox(
        event_type='StudentEnrolled',
        aggregate_id=enrollment.id,
        payload={'enrollment_id': str(enrollment.id), 'user_id': str(user.id), ...}
    )
```

**Критерии выбора Outbox:**
1. Событие создаёт aggregate root (нельзя потерять)
2. Событие меняет деньги/баллы/сертификаты
3. Событие уходит во внешний сервис (retry нужен)
4. Потеря события = data corruption

**Обязательно:** Все event handlers должны быть идемпотентны.

Подробно: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) раздел "Event System Implementation"



```python

obj.count += 1
obj.save()


Model.objects.filter(pk=pk).update(count=F('count') + 1)
obj.refresh_from_db()
```



```python

obj = Model.objects.select_for_update().get(pk=pk)
```

Всегда `select_for_update()` перед чтением + инкрементом в completion chain.



```python


tasks.fan_out_content_update.delay(lesson_id=lesson_id, content_id=content_id)
```

---



| 
|---|-----------|
| 1 | `Course.mode` — НЕТ такого поля. Режим живёт в `CourseEnrollment.delivery_format` |
| 2 | `CourseEnrollment` (не `Enrollment`) — явное имя, разграничение от будущих enrollment типов |
| 3 | Реальные FK только к Identity Domain: `CourseEnrollment → User`, `Course → User (created_by)` |
| 4 | Завершение урока — терминальное состояние. Нельзя откатить без admin override |
| 5 | Fan-out на N студентов — только async (Celery). Никогда синхронно |
| 6 | `completed_at IS NULL OR status = 'completed'` — на всех progress таблицах |
| 7 | Снапшоты (required_content_count и т.д.) обновляются через события, не пересчитываются |
| 8 | Cross-domain writes (напр. `CourseEnrollmentService.complete_enrollment`) — только через `on_commit` |
| 9 | Assessment = контейнер items без type поля. Type живёт только в AssessmentItem (ADR-010) |
| 10 | Assignment заменяет LessonHomework + ProjectTask. Единая модель для theory/coding/project (ADR-014) |
| 11 | Версионирование submissions обязательно. SubmissionRevision хранит историю попыток (ADR-016) |
| 12 | Mentor override требует audit trail: override_by_id, override_reason, override_at (ADR-020) |
| 13 | Attendance = ментор отмечает вручную. Турникет AccessEvent != Attendance (ADR-021) |
| 14 | Certificate = snapshot данных. Не регенерировать при изменении course_title или user_name (ADR-025) |
| 15 | Публичная verification через 6-символьный код (A-Z, 0-9). Rate limiting обязателен (ADR-026) |
| 16 | **Enrollment Domain отделён от Learning** — CourseEnrollment живёт в `enrollment/`, не в `learning/` (ADR-032) |
| 17 | **Feature-Sliced Structure** — `domain/models/`, не `domain/models.py`. Один файл = одна модель (~150 строк) (ADR-033) |
| 18 | **Soft References между доменами** — используй `course_id: UUIDField`, не `ForeignKey` (кроме Identity) |
| 19 | **Shared Kernel строго ограничен** — только базовые модели и универсальные value objects. NO utils.py/helpers.py |
| 20 | **Payment Domain обязателен** — все платежи через отдельный bounded context, не в Enrollment |

---



**🆕 Enrollment Domain — Integration Hub (центральная точка интеграции)**

```
┌─────────────┐
│  Payment    │ PaymentSucceeded (Outbox)
│  Domain     │ ─────────────────────────┐
└─────────────┘                          │
                                         ▼
                                  ┌──────────────┐
                                  │  Enrollment  │
                                  │   Domain     │ ◄── Learning (CoursePublished)
                                  │ (INTEGRATION │
                                  │     HUB)     │
                                  └──────┬───────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
            StudentEnrolled      EnrollmentCompleted   AccessGranted
              (Outbox)              (Signal)            (Signal)
                    │                    │                    │
                    ▼                    ▼                    ▼
            ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
            │   Progress   │    │ Certificates │    │   Learning   │
            │   Domain     │    │   Domain     │    │   Domain     │
            └──────────────┘    └──────────────┘    └──────────────┘

Learning Domain ──emits──► CoursePublished ──► Enrollment (update catalog)
Learning Domain ──emits──► LessonPublished ──► UserProgress (add row)

Enrollment ──emits──► StudentEnrolled (Outbox) ──► Progress (initialize)
Enrollment ──emits──► EnrollmentCompleted ──► Certificates (generate)
Enrollment ──emits──► AccessGranted ──► Learning (unlock content)
Enrollment ──emits──► AccessRevoked ──► Learning (lock content)

Payment ──emits──► PaymentSucceeded (Outbox) ──► Enrollment (activate)
Payment ──emits──► PaymentFailed (Outbox) ──► Enrollment (suspend)
Payment ──emits──► RefundIssued (Outbox) ──► Enrollment (drop)

UserProgress ──emits──► CourseCompleted (Outbox) ──► Enrollment (mark completed)
UserProgress ──emits──► ModuleCompleted ──► Assessment (unlock next assessment)
UserProgress ──emits──► ModuleAssessmentUnlocked ──► Notifications

Assessment ──emits──► ModuleAssessmentPassed ──► UserProgress (unlock next module)
Assessment ──emits──► ModuleAssessmentFailed ──► Analytics, Notifications
Assessment ──emits──► AssessmentNeedsMentorReview ──► Mentorship (work queue)
Assessment ──emits──► AssessmentAttemptStarted (Outbox) ──► Submissions (create Assignment)

Submissions ──emits──► SubmissionReviewed (Outbox) ──► Assessment (update response points)
Submissions ──emits──► SubmissionApproved ──► UserProgress (homework gate)
Submissions ──emits──► SubmissionSubmitted ──► Mentorship (add to work queue)

Mentorship ──emits──► AttendanceMarked ──► UserProgress (offline completion)
Mentorship ──emits──► LessonCompletionOverride ──► UserProgress (mentor override)

Certificates ──emits──► CertificateIssued (Outbox) ──► Notifications (send email)
```

**Правила интеграции:**

1. **Домены НЕ импортируют models друг друга напрямую** — только через события или queries
2. **Читают** через Application Layer Queries (одна база) — разрешено
3. **Пишут** только через события (Django Signals или Outbox Pattern) — обязательно
4. **Soft References** для cross-domain связей — используй UUID, не FK (кроме Identity Domain)
5. **Enrollment = Integration Hub** — все домены интегрируются через него (Payment → Enrollment → Progress → Certificates)



| Domain        | Owns                           | Reads From                      | Writes To (via events)                |
|---------------|--------------------------------|---------------------------------|---------------------------------------|
| Identity      | User, Role, Profile            | —                               | —                                     |
| Learning      | Course, Module, Lesson         | Enrollment (check access)       | Enrollment (CoursePublished)          |
| Enrollment    | CourseEnrollment, AccessRule   | Learning, Payment, Identity     | Progress, Certificates, Notifications |
| Progress      | CourseProgress, LessonProgress | Enrollment, Learning            | Enrollment, Assessment                |
| Payment       | Payment, Transaction, Refund   | Enrollment                      | Enrollment, Notifications             |
| Assessment    | Assessment, Attempt, Response  | Enrollment, Progress            | Progress, Submissions, Mentorship     |
| Submissions   | Assignment, Submission         | Enrollment, Assessment          | Assessment, Mentorship                |
| Mentorship    | MentorGroup, Attendance        | Enrollment, Submissions         | Progress                              |
| Certificates  | Certificate, Template          | Enrollment                      | Notifications                         |
| Notifications | Template, Preferences          | ALL (via events)                | — (send-only)                         |
| Analytics     | Denormalized read models       | ALL (via events)                | — (read-only)                         |

---



| Действие              | Student | Mentor | Staff | Admin |
|-----------------------|---------|--------|-------|-------|
| Просмотр каталога     | ✓       | ✓      | ✓     | ✓     |
| Запись на курс        | ✓       | —      | —     | ✓     |
| Создание курса        | —       | —      | ✓     | ✓     |
| Публикация курса      | —       | —      | OWN   | ✓     |
| Архивация курса       | —       | —      | —     | ✓     |
| Просмотр черновиков   | —       | —      | OWN   | ✓     |
| Проверка заданий      | —       | ✓      | ✓     | ✓     |
| Оценка assessment     | —       | ✓      | OWN   | ✓     |
| Override прогресса    | —       | —      | —     | ✓     |
| Проверка submissions  | —       | ✓      | ✓     | ✓     |
| Submit homework/project | ✓     | —      | —     | —     |
| Создание mentor groups | —      | —      | —     | ✓     |
| Отметка attendance    | —       | ✓      | —     | ✓     |
| Lesson completion override | —  | ✓      | —     | ✓     |
| Генерация сертификатов | —      | —      | —     | AUTO  |
| Revoke сертификата    | —       | —      | —     | ✓     |
| Reissue сертификата   | —       | —      | —     | ✓     |
| Публичная verification | ✓      | ✓      | ✓     | ✓     |

`OWN` = только для своих курсов (`course.created_by == request.user`).
`AUTO` = система генерирует автоматически при CourseCompleted event.

**Примечание:** Mentor может override только для своих студентов (group check).

---



```
Таблицы:   {app}_{modelname}             → courses_course, progress_lessonprogress
Индексы:   idx_{table}_{field(s)}        → idx_course_status
Уникальные: uq_{table}_{field(s)}        → uq_lessonprogress_enr_lesson
Сервисы:   {Entity}Service               → CourseService, LessonProgressService
Селекторы: {Entity}Selector              → CourseCatalogSelector
События:   {Entity}{PastTense}           → CoursePublished, StudentEnrolled
Tasks:     {verb}_{object}               → fan_out_content_deletion
```

---



- ❌ Не трогай `apps/accounts/` — Identity Domain решён, не переделывай аутентификацию
- ❌ Не добавляй `mode` поле на `Course` — режим живёт только в `CourseEnrollment`
- ❌ Не пиши в модели напрямую из views — только через Services/Commands
- ❌ Не делай синхронный fan-out на N студентов в event handler
- ❌ Не используй `obj.counter += 1; obj.save()` — только `F()` expressions
- ❌ Не создавай отдельные курсы для online/offline — это один курс
- ❌ Не делай FK между доменами (кроме Identity) — используй soft references (UUID)
- ❌ Не проектируй новый домен без прочтения `docs/CONTRIBUTING.md`
- ❌ **Не создавай `models.py` — создавай `models/` папку с отдельными файлами**
- ❌ **Не клади всё в один `serializers.py` — создавай `serializers/` с файлами по операциям**
- ❌ **Не клади всё в один `api.py` — создавай `rest/{feature}/create.py, detail.py, list.py`**
- ❌ **Не клади бизнес-логику или utils в `shared/` — только базовые модели и value objects**
- ❌ **Не размещай CourseEnrollment в `learning/` — это `enrollment/` domain**
- ❌ **Не забывай про Payment Domain — это критичный bounded context, не часть Enrollment**

---



| Домен          | Дизайн | Код | Тесты |
|----------------|--------|-----|-------|
| Identity       | ✓      | ✓   | ?     |
| Learning       | ✓      | 85% | —     |
| Enrollment     | ✓      | 30% | —     |
| UserProgress   | ✓      | 90% | —     |
| Payment        | ✓      | —   | —     |
| Assessment     | ✓      | ✓   | —     |
| Submissions    | ✓      | ✓   | —     |
| Mentorship     | ✓      | —   | —     |
| Notifications  | —      | —   | —     |
| Analytics      | —      | —   | —     |
| Certificates   | ✓      | —   | —     |

**Phase 1A завершён (2026-06-07/08):** Дизайн Assessment v3, Submissions v1, Mentorship v1, Certificates v1 готовы. 19 новых ADR (ADR-010..028).

**Phase 1A+ завершён (2026-06-08):** 
- Принята Feature-Sliced Modular Monolith Architecture (ADR-033)
- Enrollment Domain выделен как отдельный bounded context (ADR-032)
- Payment Domain добавлен в архитектуру (дизайн v1)
- Установлены строгие правила для shared/ kernel
- Обновлена документация: ARCHITECTURE_REVISED.md, design docs

**Phase 1B в работе (2026-06-09 → 2026-06-10):**
- ✅ Learning Domain — Feature-Sliced структура применена (85%)
- ✅ UserProgress Domain — создан с нуля (90%):
  - 4 модели, 3 domain services, 6 commands/queries
  - Event handlers, Celery tasks, REST API v1
  - 13 fixes из Architecture Review реализованы
- ✅ Assessment Domain — создан и завершён (100%):
  - 8 моделей, 2 domain services, 6 commands/queries
  - Celery task для code execution (stub)
  - REST API v1 (7 endpoints)
  - ADR-010, ADR-011, ADR-012, ADR-013 реализованы
- ✅ Submissions Domain — создан и завершён (100%):
  - 6 моделей созданы (Assignment, Submission, Revision, File, AutoCheck, Review)
  - 2 Domain Services (SubmissionService, ReviewService)
  - 5 Commands, 5 Queries
  - REST API v1 (8 endpoints)
  - Event handlers (incoming + outgoing)
  - Infrastructure tasks (virus scanning, auto-checks stubs)
  - ADR-014, ADR-015, ADR-016, ADR-017, ADR-018, ADR-019 реализованы
  - **Статус:** docs/implementation/SUBMISSIONS_STATUS.md

**Следующий шаг:** 
1. ✅ Завершить Assessment Domain (Application Layer + REST API) — ГОТОВО
2. ✅ Завершить Submissions Domain (Application Layer + REST API + Event Handlers) — ГОТОВО
3. 🔄 Создать Payment Domain (дизайн готов v1)
4. 🔄 Завершить Enrollment Domain integration (Payment → Enrollment → Progress → Certificates)
5. 🔄 Создать Mentorship Domain (дизайн готов v1)
6. 🔄 Создать Certificates Domain (дизайн готов v1)
