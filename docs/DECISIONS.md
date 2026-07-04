

Все важные архитектурные решения задокументированы здесь.
Перед добавлением нового — прочти существующие. Не отменяй ADR без обсуждения.

Формат: **Контекст → Решение → Причина → Последствия**

---



**Статус:** Принято  
**Дата:** Начало проекта

**Контекст:** Нужно решить стартовую архитектуру для LearnFlow.

**Решение:** Единый Django-монолит с программными границами между доменами.

**Причина:**
- Нет команды DevOps для поддержки service mesh
- Домены ещё не устоялись — преждевременная экстракция дорога
- Одна БД позволяет atomic transactions между доменами
- Код границ (Selectors/Services/Events) написан так, чтобы будущая экстракция была механической

**Последствия:** Реальные FK к Identity домену. Убрать при выделении в сервис одной миграцией.

---



**Статус:** Принято  
**Дата:** Дизайн Learning Domain

**Контекст:** Platform поддерживает online и offline обучение. Вопрос: где хранить режим?

**Отклонённые варианты:**
- `Course.mode = online|offline` → пришлось бы создавать "Python Backend Online" и "Python Backend Offline" как два отдельных курса с дублированным контентом.

**Решение:** `CourseEnrollment.delivery_format = online|offline`.  
Курс имеет флаги возможностей: `Course.supports_online` и `Course.supports_offline`.

**Причина:**
- Один курс — один набор контента (модули, уроки, материалы)
- Студент выбирает формат при записи, не курс выбирает за него
- `supports_*` флаги = capability declaration, `delivery_format` = student's choice

**Последствия:** Все completion checks читают `enrollment.delivery_format` в runtime, не snapshot.

---



**Статус:** Принято  
**Дата:** Дизайн Learning Domain

**Контекст:** Как ссылаться на `User` из Learning/Progress доменов?

**Отклонённые варианты:**
- `user_id = UUIDField()` без FK → нет DB integrity, нет ORM `select_related`, каскады вручную

**Решение:** `ForeignKey(settings.AUTH_USER_MODEL)` с реальными DB constraints.

**Причина:** Оба домена в одной БД. Real FK даёт: PROTECT/CASCADE семантику, `select_related`, DB integrity. При выделении в микросервисы — убирается одной миграцией.

**Последствия:** Зависимость на уровне схемы. Задокументирована, управляема.

---



**Статус:** Принято  
**Дата:** Дизайн UserProgress Domain

**Контекст:** Как реализовать lesson → module → course completion chain?

**Отклонённые варианты:**
- Event-driven (каждый шаг через event) → гонки, сложность отладки, нет гарантий порядка

**Решение:** Вся цепочка `_check_lesson → _check_module → _check_course` — один `transaction.atomic()` с `select_for_update()` на каждом уровне. Внешние events (Notifications, Analytics) — через `transaction.on_commit()`.

**Причина:** Единая транзакция = атомарность. Трейсить один call stack, не event chain. Параллелизм решён row-level locks.

**Последствия:** Требует `select_for_update()` на всех progress моделях в cascade chain.

---



**Статус:** Принято  
**Дата:** Дизайн UserProgress Domain

**Контекст:** Как отслеживать `required_content_count` и `viewed_required_count` без cross-domain queries в hot path?

**Решение:** Snapshot при enrollment. Инкремент/декремент через `F()` expressions + фоновые задачи для fan-out.

**Правила:**
1. Snapshot: `required_content_count` снимается при unlock урока
2. Обновление: через события от Learning Domain → Celery task → batch update
3. Hot path: только чтение своей таблицы, без JOIN к Learning Domain
4. Completed уроки: `WHERE status != 'completed'` в любом counter update

**Последствия:** F4 из review — нужно событие `LessonContentAdded` в Learning Domain.

---



**Статус:** Принято  
**Дата:** Дизайн Learning Domain v2

**Контекст:** Как связать курсы с категориями?

**Решение:** `Course.category_id → CourseCategory` — nullable FK. Один курс, одна категория.

**Причина:** Junction table нужна только если курс принадлежит нескольким категориям одновременно. Для LearnFlow это edge case, который пока не нужен. Добавить junction при необходимости без breaking changes.

**Последствия:** Если нужны мультикатегории — добавить `CourseCategoryAssignment` без изменения существующих данных.

---



**Статус:** Принято  
**Дата:** Review UserProgress Domain (F18)

**Контекст:** Bulk offline attendance (5 уроков одновременно) создаёт race condition на `completed_lessons_count`.

**Решение:** `select_for_update()` на `ModuleProgress` и `CourseProgress` в начале каждого completion check.

**Причина:** Без locks concurrent workers читают одно значение, пишут одно значение — теряют инкремент. Студент застревает навсегда.

**Последствия:** Row-level locking = serialization на уровне enrollment. Deadlock теоретически возможен — порядок lock acquisition должен быть lesson → module → course (всегда снизу вверх).

---



**Статус:** Принято  
**Дата:** Review UserProgress Domain (F1)

**Контекст:** Event handlers обновляли N строк синхронно, где N = кол-во enrolled студентов.

**Решение:** Все операции вида "обновить X у всех студентов на курсе" → Celery task + batch processing (500 строк/батч).

**Триггеры для async:** LessonPublished, LessonDeleted, LessonContentAdded, LessonContentDeleted, ModulePublished, AssessmentAdded.

**Последствия:** Краткая eventual consistency. Студент может не сразу увидеть новый урок (секунды, не минуты). Acceptable.

---



**Статус:** Принято  
**Дата:** Дизайн Assessment Domain

**Контекст:** Assessment содержит разные типы вопросов с разной стратегией оценки.

**Решение:**

| Тип              | Оценка      | Когда              |
|------------------|-------------|-------------------|
| single_choice    | Auto        | Синхронно при submit |
| multiple_choice  | Auto        | Синхронно при submit |
| coding           | Auto        | Async (execution service) |
| text_answer      | Manual      | Ментор            |
| project          | Manual      | Ментор через Submissions |

Attempt переходит в `pending_review` если есть manual items. Финальный pass/fail — только когда ВСЕ items оценены.

---

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужны разные виды assessment (quiz, project, interview, mixed).

**Отклонённые варианты:**
- `ModuleAssessment.type` — жёсткая типизация, mixed становится отдельным типом
- `has_quiz/has_project/has_interview` — булевы флаги, сложность валидации

**Решение:** Assessment = набор `AssessmentItem`. Состав items определяет "тип" автоматически.

**Причина:**
- Гибкость: можно создать любую комбинацию
- Простота: нет специальной логики для "mixed"
- Масштабируемость: новый тип item = просто добавить в enum

**Последствия:** UI должен показывать состав assessment динамически.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Ментор может пересмотреть авто-оценку. Нужна прозрачность.

**Решение:**
- `AssessmentResponse`: `auto_points`, `mentor_points`, `final_points`
- `AssessmentReviewLog`: audit trail всех изменений

**Причина:** Споры студент/ментор через год. История покажет кто и почему изменил.

**Последствия:** Дополнительная таблица, но критична для доверия к платформе.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Assessment item type=project требует кодовую базу/файлы/GitHub repo.

**Решение:** Assessment НЕ хранит проекты. Создаёт `Assignment` в Submissions Domain. Результат возвращается через событие `SubmissionReviewed`.

**Причина:**
- Разделение ответственности: Assessment = оценивание, Submissions = хранение работ
- Submissions может расти независимо (versioning, diff, CI integration)
- Assessment остаётся lightweight

**Последствия:** Cross-domain event dependency. Submissions Domain обязателен для project items.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужны интервью с менторами. Live-интервью сложны (scheduling, video, recording).

**Решение для v1:** `interview` тип = текстовый ответ + ментор проверяет (как `text_answer` с другим названием).

**Решение для v2:** Отдельная таблица `InterviewSession`, Zoom integration, scheduling.

**Причина:** MVP killer avoidance. Live-интервью — Phase 2.

**Последствия:** v1 ограничен async интервью. Live появится позже.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужны домашки для уроков и проектные задания для assessment.

**Отклонённые варианты:**
- `LessonHomework` + `ProjectTask` — две отдельные таблицы с дублированием полей
- Назвать сущность `Project` — странно звучит для "Что такое SOLID?"

**Решение:** Единая таблица `Assignment` с полем `type = theory | coding | project`.

**Причина:**
- Одна система submission для всех типов заданий
- Меньше дублирования кода (services, selectors, API)
- Легко добавлять новые типы

**Последствия:** `lesson_id` может быть NULL (для project из assessment).

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Студент пересдаёт работу после замечаний ментора.

**Решение:** `Submission` (контейнер) + `SubmissionRevision` (версии).

**Причина:** Студент почти всегда пересдаёт. Нужна история изменений.

**Последствия:** Ментор всегда проверяет конкретную ревизию, не Submission целиком.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Разные типы submission хранят разные данные (GitHub URL vs uploaded files vs text).

**Отклонённые варианты:**
- Отдельные таблицы для каждого типа — слишком много таблиц
- Отдельные поля `github_url`, `file_id`, `text_answer` — NULL everywhere

**Решение:** `SubmissionRevision.payload JSONB` с разной структурой по типу.

**Причина:** Гибкость, легко добавлять новые типы без миграций.

**Последствия:** Валидация payload на уровне application logic, не DB constraints.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужны и автоматические проверки (tests, linting) и ручная проверка ментора.

**Решение:** `AutoCheck` (автомат) ≠ `SubmissionReview` (ментор). Разные таблицы.

**Причина:**
- Автопроверка может быть зелёной, но ментор поставит низкий балл за архитектуру
- Ментор может одобрить даже если coverage < 80% (есть причины)
- Не смешивать источники оценки

**Последствия:** UI должен показывать оба результата отдельно.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Студенты загружают ZIP, PDF, DOCX — потенциальный вектор атаки.

**Решение:** Все загруженные файлы проходят ClamAV scan перед доступом ментора.

**Причина:** Безопасность. Нельзя давать ментору скачивать непроверенные файлы.

**Последствия:**
- Дополнительная задержка (секунды)
- Celery worker для сканирования
- S3 temp bucket для непроверенных файлов

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужна система назначения студентов менторам.

**Отклонённые варианты:**
- Студент выбирает ментора сам — балансировка нагрузки невозможна

**Решение:** Только admin назначает студентов в группы. Один ментор → одна группа → N студентов.

**Причина:** Популярные менторы перегружены, непопулярные простаивают. Нужен контроль.

**Последствия:** В v2 можно добавить авто-распределение (round-robin, capacity-based).

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужно планировать offline занятия.

**Отклонённые варианты:**
- Привязать Module к датам (Module 1: 2026-01-01, 2026-01-03...) — ломается при переносах

**Решение:** `OfflineSession` — отдельная сущность с `scheduled_start/end`, `status` (scheduled/cancelled/rescheduled).

**Причина:** Реальная жизнь: праздники, болезнь, отключение света. Расписание должно быть гибким.

**Последствия:** Занятия можно отменять, переносить без изменения структуры модуля.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Есть турникет с Face ID. Можно ли автоматически отмечать посещаемость?

**Отклонённые варианты:**
- FaceID → автоматическая attendance → LessonCompleted — ложные срабатывания

**Решение для v1:** Ментор отмечает вручную. Турникет показывает подсказки.

**Решение для v2:** Полуавтоматическая система (турникет предлагает, ментор корректирует).

**Причина:**
- Студент может войти в центр, но не пойти на урок
- Турникет может не сработать, но студент реально присутствует

**Последствия:** Ментор = источник истины для attendance.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Offline обучение не всегда укладывается в правила (контент просмотрен, домашка сдана).

**Решение:** `LessonProgress.completion_source` может быть `mentor_override`.

**Причина:** Ментор на месте, он знает лучше. Студент может выполнить задание устно в аудитории.

**Последствия:** Нужен audit trail: `override_by_id`, `override_reason`, `override_at`.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Ментор должен видеть что нужно проверить.

**Решение:** Read model `MentorWorkReview` — очередь работ с сортировкой (overdue → oldest).

**Причина:** Без этого ментор не знает что проверять первым. Это важнее чатов и комментариев.

**Последствия:** Таблица обновляется через события (SubmissionSubmitted, AssessmentNeedsMentorReview).

---



**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** Разные курсы требуют разные дизайны сертификатов.

**Решение:** `CertificateTemplate` таблица с конфигурацией layout/fonts. `Course → template_id`.

**Причина:** Один шаблон для всех курсов — плохой UX. Backend и Design курсы требуют разные визуалы.

**Последствия:** Admin может создавать новые шаблоны без кода.

---



**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** Студент может изменить имя в профиле после получения сертификата.

**Решение:** `student_full_name_snapshot`, `course_name_snapshot` — копии на момент выдачи.

**Причина:** Сертификат — юридический документ. Нельзя автоматически обновлять.

**Последствия:** Если нужно переиздать — через `CertificateReissueRequest`.

---



**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** Генерация PDF занимает 5-15 секунд.

**Отклонённые варианты:**
- Синхронная генерация в `CourseCompleted` handler — блокирует UserProgress

**Решение:** Celery task `generate_certificate.delay()`.

**Причина:** Не блокировать завершение курса.

**Последствия:** Сертификат доступен не мгновенно (статус `pending` → `issued`).

---



**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** 10,000 скачиваний = 10,000 генераций?

**Решение:** `Certificate.pdf_url` — сохраняем PDF в S3 один раз.

**Причина:** Генерация дорогая (CPU, время). Бессмысленно повторять.

**Последствия:** S3 storage cost (минимальный).

---



**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** Нужна возможность отозвать сертификат (списывание, ошибка выдачи).

**Решение:** `Certificate.status = 'revoked'` + `revoked_at`, `revoked_by_id`, `revoked_reason`.

**Причина:** Сертификаты могут быть выданы ошибочно или нечестно получены.

**Последствия:** Публичная страница показывает "Certificate Revoked" с причиной.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** В модульном монолите нужен механизм cross-domain взаимодействия через события. Есть три подхода:
1. **Django Signals** — встроено, просто, синхронно
2. **Domain Events + Event Bus** — framework-agnostic, типизировано
3. **Outbox Pattern** — гарантированная доставка, audit trail, eventual consistency

**Отклонённые варианты:**

**Только Django Signals:**
- ❌ Нет гарантий доставки при сбое handler
- ❌ Нет истории событий (нельзя replay)
- ❌ Нет retry механизма

**Только Outbox Pattern:**
- ❌ Overkill для простых событий (LessonCompleted → increment counter)
- ❌ Eventual consistency везде (не всегда нужна)
- ❌ Каждое событие = INSERT в БД (overhead)

**Только Domain Events:**
- ❌ Нужно писать EventBus с нуля
- ❌ Всё равно нужен Outbox для критичных событий

**Решение:** Гибридный подход — 90% событий через Django Signals, 10% критичных через Outbox.

**Django Signals для:**
- Cascade completion (LessonCompleted → check module)
- Counter updates (ContentDeleted → decrement count)
- Internal domain events (ModuleUnlocked → notification)
- Любые события где потеря = не критична (можно пересчитать вручную)

**Outbox Pattern для:**
- Создание aggregate root (`StudentEnrolled` → `CourseProgress`)
- Изменение баллов/денег (`SubmissionReviewed` → `final_points`)
- Внешние интеграции (`CertificateIssued` → email)
- Любые события где потеря = data corruption

**Причина:**
- Простота для 90% случаев (Django Signals — zero setup)
- Надёжность для критичных событий (Outbox — at-least-once delivery)
- Audit trail для compliance (все критичные события в БД)
- Готовность к микросервисам (Outbox легко переключить на RabbitMQ/Kafka)

**Последствия:**
- Две системы событий в кодовой базе (но чёткое разделение по назначению)
- Нужна таблица `DomainEventOutbox` + Celery beat task для обработки
- Критичные события обрабатываются асинхронно (eventual consistency)
- Обычные события обрабатываются синхронно (immediate consistency)

**Критерии выбора Outbox:**
1. Событие создаёт aggregate root (нельзя потерять)
2. Событие меняет деньги/баллы/сертификаты (финансовая консистентность)
3. Событие уходит во внешний сервис (retry нужен)
4. Потеря события = data corruption (нельзя восстановить вручную)

**Список критичных событий (Outbox):**
- `StudentEnrolled` → создаёт CourseProgress (aggregate root)
- `CourseCompleted` → генерирует Certificate (деньги, compliance)
- `SubmissionReviewed` → обновляет баллы AssessmentResponse
- `CertificateIssued` → отправка email
- `AssessmentAttemptStarted` (для project) → создаёт Assignment

**Список обычных событий (Django Signals):**
- `LessonCompleted` → increment module counter
- `ModuleCompleted` → increment course counter
- `ContentDeleted` → decrement required_content_count
- `LessonPublished` → создать LessonProgress строки (fan-out через Celery)
- `ModuleAssessmentPassed` → unlock next module
- `AttendanceMarked` → mark lesson completed (offline)

**Реализация:** См. `docs/ARCHITECTURE.md` раздел "Event System Implementation"

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужна система фоновых задач для:
- Fan-out операций (обновление N студентов)
- Coding execution (sandbox, долгие операции)
- Email/SMS отправка
- PDF generation (сертификаты)
- ClamAV virus scan (файлы студентов)
- Outbox events processing

**Отклонённые варианты:**

**Django-rq (Redis Queue):**
- ❌ Меньше функций чем Celery (нет chord, chain, группировки)
- ❌ Меньше community support
- ✅ Проще setup (но мы уже знаем Celery)

**Dramatiq:**
- ❌ Моложе Celery, меньше production опыта
- ✅ Чище API
- ❌ Меньше интеграций с Django

**APScheduler:**
- ❌ In-process (не масштабируется горизонтально)
- ❌ Нет distributed queue

**AWS SQS + Lambda:**
- ❌ Vendor lock-in (AWS only)
- ❌ Cold start latency для Lambda
- ❌ Дороже для наших объёмов

**Решение:** Celery 5.x + Redis 7.x

**Причина:**
- ✅ Industry standard для Django (проверено годами)
- ✅ Горизонтальное масштабирование (добавить workers = добавить процессы)
- ✅ Богатая функциональность: retry, rate limiting, chord, chain, group
- ✅ Celery Beat для периодических задач (outbox processing каждые 10 сек)
- ✅ Monitoring через Flower
- ✅ Redis как broker — быстрый, простой, уже используется для кэша
- ✅ Поддержка приоритетов через routing (default, fan_out, coding queues)

**Архитектура очередей:**

| Queue | Назначение | Workers | Приоритет |
|-------|------------|---------|-----------|
| `default` | Email, SMS, Push, Outbox processing | 2-4 | Средний |
| `fan_out` | Fan-out на N студентов (LessonPublished) | 4-8 | Низкий |
| `coding` | Sandbox execution (код студентов) | 8-16 | Высокий |
| `pdf` | PDF generation (сертификаты) | 2-4 | Низкий |

**Celery Beat tasks:**
```python

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
```

**Последствия:**
- Redis = single point of failure (митигация: Redis Sentinel для HA)
- Task serialization в JSON (не pickle — безопаснее)
- Monitoring через Flower обязателен (видеть stuck tasks)
- Worker memory leaks — перезапуск workers каждые N задач (`--max-tasks-per-child=1000`)

**Альтернатива для будущего:** Если вырастем > 100k студентов — можем мигрировать broker с Redis на RabbitMQ (более надёжный для очень больших объёмов), но пока Redis достаточно.

---



**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужно хранилище для:
- **Submissions Domain:** Проектные работы студентов (ZIP, PDF, code files)
- **Certificates Domain:** Сгенерированные PDF сертификаты
- **Learning Domain:** Lesson materials (опционально, для больших файлов)
- **Thumbnails:** Course/User thumbnails

**Объёмы (прогноз на год 1):**
- 10,000 студентов
- 100 assignments в среднем на студента
- Средний размер submission = 5 MB
- **Итого:** 10k × 100 × 5 MB = **5 TB в год**

**Отклонённые варианты:**

**Local Storage (Django MEDIA_ROOT):**
- ❌ Не масштабируется горизонтально (workers на разных машинах)
- ❌ Нет redundancy (потеря сервера = потеря файлов)
- ❌ Backup сложнее
- ✅ Дешевле (но не стоит экономить на критичных данных)
- **Вердикт:** Годится только для локальной разработки

**Database BLOB storage:**
- ❌ PostgreSQL раздувается (плохо для бэкапов)
- ❌ Медленнее чем object storage
- ❌ Нет CDN интеграции
- **Вердикт:** Плохая идея для файлов > 1 MB

**Решение:** S3-compatible object storage (AWS S3, MinIO, Cloudflare R2)

**Причина:**
- ✅ Industry standard (boto3 библиотека для Python)
- ✅ Redundancy из коробки (репликация между датацентрами)
- ✅ Scalable (petabytes если нужно)
- ✅ CDN интеграция (CloudFront, Cloudflare)
- ✅ Versioning для критичных файлов
- ✅ Lifecycle policies (archive старых submissions → Glacier)
- ✅ Presigned URLs для secure downloads (без прокси через Django)

**Выбор провайдера:**



**Плюсы:**
- ✅ Самый надёжный (99.999999999% durability — "11 девяток")
- ✅ CloudFront CDN из коробки
- ✅ Glacier для архива (дёшево)
- ✅ IAM для fine-grained permissions

**Минусы:**
- ❌ Дороже альтернатив
- ❌ Egress traffic costs (платишь за скачивание)

**Стоимость (примерный расчёт):**
- Storage: $0.023/GB/month → 5 TB = **$115/month**
- PUT requests: $0.005 per 1000 → 1M uploads = **$5/month**
- GET requests: $0.0004 per 1000 → 10M downloads = **$4/month**
- Egress: $0.09/GB → 500 GB/month = **$45/month**
- **Итого:** ~$170/month для 5 TB + трафик



**Плюсы:**
- ✅ S3-compatible API (легко мигрировать потом)
- ✅ **Zero egress fees** (бесплатный download)
- ✅ Cloudflare CDN интеграция
- ✅ Дешевле AWS (~50% экономия)

**Минусы:**
- ⚠️ Моложе AWS S3 (меньше track record)
- ⚠️ Нет Glacier-эквивалента (пока)

**Стоимость:**
- Storage: $0.015/GB/month → 5 TB = **$75/month**
- PUT requests: $4.50 per million → 1M = **$4.50/month**
- GET requests: $0.36 per million → 10M = **$3.60/month**
- Egress: **$0** (zero!)
- **Итого:** ~$83/month для 5 TB + трафик

**Экономия:** ~$87/month ($1044/year) vs AWS



**Плюсы:**
- ✅ S3-compatible API
- ✅ Self-hosted (полный контроль)
- ✅ Бесплатный (только infrastructure costs)

**Минусы:**
- ❌ Нужно управлять (DevOps overhead)
- ❌ Нужна репликация (setup distributed MinIO)
- ❌ Нужны бэкапы (ответственность на нас)

**Когда использовать:** Если уже есть Kubernetes кластер и DevOps команда.

**Решение для LearnFlow:** 

**Локальная разработка:** MinIO (Docker container)
```yaml

minio:
  image: minio/minio
  command: server /data --console-address ":9001"
  ports: ["9000:9000", "9001:9001"]
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin
  volumes: [minio-data:/data]
```

**Production:** Cloudflare R2 (zero egress = огромная экономия для образовательной платформы)

**Миграция в будущем:** Если R2 не устроит → легко мигрировать на AWS S3 (тот же boto3 код, только endpoint меняется)

**Структура buckets:**

```
learnflow-submissions-prod/
  ├── {assignment_id}/
  │   ├── {submission_id}/
  │   │   ├── v1/file.zip
  │   │   ├── v2/file.zip
  │   │   └── metadata.json
  
learnflow-certificates-prod/
  ├── {year}/
  │   ├── {month}/
  │   │   ├── {certificate_id}.pdf
  
learnflow-media-prod/
  ├── course-thumbnails/
  ├── user-avatars/
  └── lesson-materials/

learnflow-submissions-quarantine/  
```

**Security:**
- Submissions bucket = private (presigned URLs только)
- Certificates bucket = public read для `/verify/{code}` endpoint
- Virus quarantine bucket = admin only

**Lifecycle policies:**
- Submissions старше 2 лет → archive (cold storage)
- Failed virus scans старше 30 дней → delete
- Certificates — никогда не удалять (compliance)

**Последствия:**
- Django-storages library для интеграции
- Presigned URLs для secure downloads (не прокси через Django)
- ClamAV scan перед перемещения из temp в permanent bucket
- Versioning для submissions (S3 native versioning или наша логика)

**Конфигурация:**

```python

if USE_S3:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='auto')
    AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')  
    AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN', default=None)
    AWS_DEFAULT_ACL = None  
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  
    }
else:
    MEDIA_ROOT = BASE_DIR / 'media'
    MEDIA_URL = '/media/'
```

---



**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:**

`CourseEnrollment` модель изначально размещалась в Learning Domain (`courses/models.py`), но она не относится к контенту курсов. 

**Проблема:**
- Learning Domain отвечает за **ЧТО изучаем** (Course, Module, Lesson)
- Enrollment отвечает за **КТО изучает, на каких условиях, есть ли доступ**
- Смешивание этих ответственностей нарушает Single Responsibility Principle
- Enrollment является интеграционным хабом для Payment, Progress, Certificates
- Разные scaling характеристики (spike во время регистрации vs стабильное потребление контента)

**Отклонённые варианты:**

1. **Оставить CourseEnrollment в Learning Domain**
   - ❌ Нарушает SRP
   - ❌ Learning Domain становится god object
   - ❌ Сложно масштабировать независимо

2. **Создать Access Domain вместо Enrollment**
   - ❌ Слишком узкое название (не покрывает lifecycle: pending → active → completed)
   - ❌ Не отражает contract nature (start_date, end_date, payment_status)

**Решение:**

Создать **Enrollment Domain** как отдельный bounded context:

```
learnflow/
├── learning/          
│   ├── Course
│   ├── Module
│   └── Lesson
│
├── enrollment/        
│   ├── CourseEnrollment
│   ├── AccessRule
│   ├── Prerequisite
│   └── Waitlist
```

**Что владеет Enrollment Domain:**

| Ответственность          | Описание                                                  |
|--------------------------|-----------------------------------------------------------|
| Access Control           | Проверка доступа студента к курсу                         |
| Contract Terms           | Online/Offline, даты начала/окончания, статус оплаты      |
| Enrollment Lifecycle     | pending → active → suspended → dropped → completed        |
| Integration Hub          | Центральная точка для Payment, Progress, Certificates     |
| Business Rules           | Prerequisites, max students, enrollment deadlines         |

**События Enrollment Domain:**

```python

StudentEnrolled (Outbox)         → Progress (initialize)
EnrollmentCompleted (Signal)     → Certificates (generate)
AccessGranted (Signal)           → Learning (unlock content)
AccessRevoked (Signal)           → Learning (lock content)
EnrollmentSuspended (Signal)     → Notifications


PaymentSucceeded (from Payment)  → Activate enrollment
PaymentFailed (from Payment)     → Suspend enrollment
CourseCompleted (from Progress)  → Mark enrollment completed
CourseArchived (from Learning)   → Notify students
```

**Причина:**

1. **Разделение ответственности:** Content management ≠ Access management
2. **Integration Hub:** Enrollment естественный центр для Payment → Progress → Certificates flow
3. **Scalability:** Enrollment можно масштабировать независимо (spike during registration)
4. **Microservice Ready:** Легко экстрагировать в отдельный сервис
5. **Business Clarity:** "Who can access what" — чёткий bounded context

**Последствия:**

✅ **Положительные:**
- Чёткие границы доменов
- Learning Domain фокусируется только на контенте
- Enrollment становится natural integration point
- Легко добавлять новые типы enrollments (не только CourseEnrollment)
- Проще тестировать access control logic

⚠️ **Отрицательные:**
- Миграция данных: `learning_courseenrollment` → `enrollment_courseenrollment`
- Обновление импортов по всей кодовой базе
- Soft references между доменами: `enrollment.course_id: UUIDField` вместо FK
- Нужны интеграционные тесты для cross-domain событий

**Миграционный путь:**

```python






```

**Связанные решения:**
- ADR-033: Feature-Sliced Domain Structure
- docs/design/ENROLLMENT_DOMAIN_V1.md

---



**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:**

При текущей структуре (`domain/models.py`, `domain/services.py`) файлы разрастаются до 1000-1500+ строк:

**Пример проблемы:**

```python

class ModuleAssessment(models.Model): ...      
class AssessmentItem(models.Model): ...        
class AssessmentOption(models.Model): ...      
class AssessmentAttempt(models.Model): ...     
class AssessmentResponse(models.Model): ...    
class CodingTestCase(models.Model): ...        
class AssessmentPart(models.Model): ...        
class AssessmentPartResult(models.Model): ...  

```

**Проблемы:**
- 😱 Невозможно навигировать в файле 1500+ строк
- 🐌 IDE тормозит при открытии больших файлов
- 🔍 Сложно найти нужную модель/метод
- 🔀 Git conflicts при параллельной работе
- 📝 Code review 1500-строчного файла = nightmare
- ♻️ Изменение одной модели требует чтения всего файла

То же самое с `serializers.py`, `api.py`, `services.py`.

**Отклонённые варианты:**

1. **Оставить как есть (models.py, services.py)**
   - ❌ Не масштабируется для команды 10+ разработчиков
   - ❌ Плохой developer experience

2. **Full DDD + Hexagonal Architecture**
   ```
   domain/
   ├── entities/
   ├── value_objects/
   ├── aggregates/
   ├── repositories/ (interfaces)
   └── domain_services/
   
   infrastructure/
   ├── persistence/
   │   ├── django_models/
   │   └── repositories/ (impl)
   ```
   - ❌ Over-engineering для Django
   - ❌ Repository Pattern поверх ORM = unnecessary indirection
   - ❌ 3x больше файлов для той же функциональности
   - ❌ Junior developers не поймут

3. **Feature folders внутри app/**
   ```
   assessment/
   ├── features/
   │   ├── create_assessment/
   │   ├── start_attempt/
   │   └── submit_response/
   ```
   - ❌ Слишком глубокая вложенность
   - ❌ Сложно переиспользовать models между features

**Решение:**

**Feature-Sliced Modular Monolith** — разбиваем по слоям И по фичам:

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
│   │   └── part.py              
│   │
│   ├── value_objects/           
│   │   ├── grading_status.py
│   │   ├── score.py
│   │   └── time_limit.py
│   │
│   ├── events/                  
│   │   ├── assessment_passed.py
│   │   ├── assessment_failed.py
│   │   └── attempt_started.py
│   │
│   └── services/                
│       ├── grading.py
│       ├── auto_grader.py
│       └── mentor_review.py
│
├── application/
│   ├── commands/                
│   │   ├── start_attempt.py
│   │   ├── submit_response.py
│   │   └── finalize_attempt.py
│   │
│   └── queries/                 
│       ├── assessment_detail.py
│       ├── attempt_detail.py
│       └── available_assessments.py
│
├── presentation/rest/
│   ├── assessments/             
│   │   ├── create.py            
│   │   ├── update.py            
│   │   ├── detail.py            
│   │   ├── list.py              
│   │   └── serializers/         
│   │       ├── create.py
│   │       ├── update.py
│   │       ├── detail.py
│   │       └── list.py
│   │
│   └── attempts/
│       ├── start.py
│       ├── submit_response.py
│       └── serializers/
```

**Причина:**

**Принцип:** "Optimize for deletion, not creation"

- Когда нужно изменить `AssessmentAttempt` → редактируешь `domain/models/attempt.py` (~150 строк)
- Когда нужно изменить API создания assessment → редактируешь `rest/assessments/create.py` (~100 строк)
- Когда нужно удалить фичу → удаляешь один файл

**Метрики:**

| Метрика               | Old Structure | New Structure |
|-----------------------|---------------|---------------|
| Размер файла          | 1500+ lines   | ~150 lines    |
| Время навигации       | 30+ seconds   | 5 seconds     |
| Git conflicts         | Частые        | Редкие        |
| Onboarding time       | 2-3 дня       | 4-6 часов     |
| Parallel development  | Сложно        | Легко         |

**Последствия:**

✅ **Положительные:**
- Быстрая навигация: `assessment/domain/models/attempt.py`
- IDE не тормозит (файлы ~150 строк)
- Легко найти код (clear file structure)
- Меньше Git conflicts (разные разработчики = разные файлы)
- Code review проще (5-10 файлов вместо одного 1500-строчного)
- Легко удалить feature (delete one file)
- Микросервис-ready (extract domain → service в days, not months)

⚠️ **Отрицательные:**
- Больше файлов в проекте (~3x)
- Нужно помнить структуру папок
- Импорты становятся длиннее:
  ```python
  
  from assessment.models import AssessmentAttempt
  
  
  from assessment.domain.models.attempt import AssessmentAttempt
  ```
- Миграция существующего кода требует времени

**Правила:**

1. **Один файл = одна модель** (~150 строк максимум)
2. **Один файл = один Command/Query** (~100 строк максимум)
3. **Один файл = один API endpoint** (create.py, detail.py, list.py)
4. **Один файл = один Serializer** (по типу операции)
5. **`__init__.py` = explicit exports only**

**Пример __init__.py:**

```python

from .assessment import ModuleAssessment
from .item import AssessmentItem, AssessmentOption
from .attempt import AssessmentAttempt
from .response import AssessmentResponse

__all__ = [
    'ModuleAssessment',
    'AssessmentItem',
    'AssessmentOption',
    'AssessmentAttempt',
    'AssessmentResponse',
]
```

**Связанные решения:**
- ADR-032: Enrollment Domain Extraction
- docs/ARCHITECTURE_REVISED.md

---



**Статус:** ✅ Принято  
**Дата:** 2026-06-08



С введением Feature-Sliced Modular Monolith (ADR-033) нужна чёткая структура API URLs и версионирование:

1. Поддержка будущей экстракции в микросервисы
2. Предотвращение конфликтов имён между доменами
3. Явное и кешируемое версионирование
4. Соответствие REST best practices

**Проблема старой структуры:**
```
/api/v1/auth/login/          ❌ Нет domain prefix
/api/v1/me/                  ❌ Неясно какой домен владеет
```

Проблемы:
- Невозможно экстрагировать домены в сервисы (конфликты URLs)
- Неясно какой домен владеет endpoint'ом
- Swagger смешивает все домены вместе



**1. Структура URLs: Domain-Prefixed**

```
/api/{version}/{domain}/{feature}/{action}/

Примеры:
/api/v1/identity/auth/login/
/api/v1/identity/profile/me/
/api/v1/learning/courses/
/api/v1/enrollment/enroll/
```

**2. Стратегия версионирования: URL-Based (не Accept Header)**

- ✅ **Выбрано:** `/api/v1/`, `/api/v2/` в URL path
- ❌ **Отклонено:** Accept Header versioning (`Accept: application/json; version=v1`)

**Обоснование:**
- Явное и отлаживаемое (видно в логах, browser dev tools)
- Кешируемое CDN/proxy (Accept Header ломает кеширование)
- Проще для клиентов API (нет custom headers)
- Индустриальный стандарт (Stripe, GitHub, Twitter APIs)

**3. Swagger/OpenAPI Documentation**

- **Единый Swagger UI** на `/api/v1/schema/swagger/` (все домены)
- Группировка по tags: `Identity — Auth`, `Learning — Courses`, и т.д.
- Готово к per-domain extraction (будущее: `/api/v1/identity/docs/` при микросервисах)

**4. Feature-Sliced Presentation Layer**

```python
accounts/presentation/rest/
├── v1/
│   ├── auth/
│   │   ├── login.py
│   │   ├── register.py
│   │   └── serializers/
│   │       ├── login.py
│   │       └── register.py
│   ├── profile/
│   │   ├── me.py
│   │   └── serializers/
│   └── urls.py
└── v2/  
```

**Один файл = один endpoint** (не монолитный `api.py`).  
**Один serializer = одна операция** (не монолитный `serializers.py`).



**URLs Mapping:**

```python

urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
]


urlpatterns = [
    path('identity/', include('identity.presentation.rest.v1.urls')),
    path('learning/', include('learning.presentation.rest.v1.urls')),
    path('enrollment/', include('enrollment.presentation.rest.v1.urls')),
    
]
```

**Spectacular Settings:**

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'LearnFlow API',
    'VERSION': '1.0.0',
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Identity — Auth', 'description': 'Authentication & registration'},
        {'name': 'Identity — Profile', 'description': 'User profile management'},
        {'name': 'Learning — Courses', 'description': 'Course catalog & content'},
        
    ],
}
```



**Положительные:**
- ✅ Чёткие границы доменов в URLs
- ✅ Готовность к экстракции микросервисов
- ✅ Нет конфликтов имён (каждый домен изолирован)
- ✅ Явное версионирование (нет магических headers)
- ✅ Лучшая организация Swagger (группировка по доменам)
- ✅ Feature-Sliced структура = проще навигация по коду

**Отрицательные:**
- ❌ Более длинные URLs (`/api/v1/identity/auth/login/` vs `/api/v1/auth/login/`)
- ❌ Breaking change для существующих клиентов (требует миграции)

**План миграции:**
- Production клиентов пока нет → прямой переход (без compatibility layer)
- Будущее: Если клиенты появятся, добавить 301 redirects со старых URLs



**Альтернатива 1: Accept Header Versioning**
```http
POST /api/identity/auth/login/
Accept: application/json; version=v1
```
**Отклонено:** Ломает HTTP кеширование, сложнее отлаживать, менее распространено.

**Альтернатива 2: Без Domain Prefix**
```
/api/v1/auth/login/
/api/v1/courses/
```
**Отклонено:** Конфликты имён при экстракции в микросервисы.

**Альтернатива 3: Per-Domain Swagger**
```
/api/v1/identity/docs/
/api/v1/learning/docs/
```
**Отложено:** Реализовать при экстракции в микросервисы. Для монолита единый Swagger проще.



- **ADR-032:** Enrollment Domain Separation (установлены границы доменов)
- **ADR-033:** Feature-Sliced Modular Monolith (структура файлов)



- Stripe API: https://stripe.com/docs/api/versioning
- GitHub API: https://docs.github.com/en/rest/overview/api-versions
- REST API Versioning Best Practices: https://restfulapi.net/versioning/

---
