



| Домен         | Дизайн | Код | Тесты | API   | Продакшн | Обновлено  |
|---------------|:------:|:---:|:-----:|:-----:|:--------:|------------|
| Identity      | ✅     | ✅  | ?     | ✅    | 🔲       | 2026-06-08 |
| Learning      | ✅     | ✅  | 🔲    | ✅    | 🔲       | 2026-06-14 |
| UserProgress  | ✅     | ✅  | 🔲    | ✅    | 🔲       | 2026-06-14 |
| Assessment    | ✅ v3  | ✅  | 🔲    | ✅    | 🔲       | 2026-06-14 |
| Submissions   | ✅ v1  | ✅  | 🔲    | ✅    | 🔲       | 2026-06-14 |
| Enrollment    | ✅     | ✅  | 🔲    | ✅    | 🔲       | 2026-06-14 |
| Payment       | ✅     | ✅  | 🔲    | ✅    | 🔲       | 2026-06-14 |
| Mentorship    | ✅ v1  | ✅  | 🔲    | ✅    | 🔲       | 2026-06-14 |
| Certificates  | ✅ v1  | ✅  | 🔲    | ✅    | 🔲       | 2026-06-14 |
| Notifications | 🔲     | 🔲  | 🔲    | 🔲    | 🔲       | —          |
| Analytics     | 🔲     | 🔲  | 🔲    | 🔲    | 🔲       | —          |

**Легенда:** Дизайн = спецификация готова | Код = domain/app слои | API = REST endpoints подключены

---



**Цель:** Спроектировать Assessment, Submissions, Mentorship, Certificates перед началом реализации кода.

**Результаты:**
- ✅ Дизайн Assessment v3 (ADR-010..013)
- ✅ Дизайн Submissions v1 (ADR-014..018)
- ✅ Дизайн Mentorship v1 (ADR-019..023)
- ✅ Дизайн Certificates v1 (ADR-024..028)
- ✅ 35+ таблиц спроектированы
- ✅ 19 новых ADR
- ✅ Документация обновлена (DATABASE.md, DECISIONS.md, API.md, DOMAIN.md, EVENTS.md)

---



**Цель:** Студент может записаться на курс и пройти его от начала до конца.

**Статус:** ✅ **MVP COMPLETE — 9/9 доменов подключены к API**

**Результаты:**


- ✅ Learning Domain — 100% (REST API v1 подключён)
- ✅ UserProgress Domain — 100% (создан с нуля, REST API v1)
- ✅ Assessment Domain v3 — 100% (8 моделей, REST API v1)
- ✅ Submissions Domain v1 — 100% (6 моделей, REST API v1, исправлены импорты)
- ✅ Enrollment Domain — 100% (Integration Hub, REST API v1)
- ✅ Payment Domain — 100% (3 модели, webhooks, REST API v1, исправлены class names)
- ✅ Mentorship Domain v1 — 100% (Attendance, REST API v1, исправлены импорты)
- ✅ Certificates Domain v1 — 100% (PDF async, REST API v1, исправлены импорты)
- ✅ Identity Domain — 100% (был готов)


- ✅ Исправлено 28 файлов с неправильными импортами
- ✅ Исправлено 5 class name mismatches
- ✅ Все домены подключены к `/api/v1/`
- ✅ `python manage.py check` — 0 ошибок
- ✅ 60 миграций применены
- ✅ Feature-Sliced Architecture применена ко всем доменам


- ✅ Course Catalog (Learning)
- ✅ Enrollment Flow (Enrollment → Payment → Progress)
- ✅ Progress Tracking (Lesson/Module/Course completion)
- ✅ Assessments (Quiz, Coding, Essay)
- ✅ Submissions (Homework, Projects)
- ✅ Reviews (Mentor work queue)
- ✅ Attendance (Offline sessions)
- ✅ Certificates (Auto-generation on completion)
- ✅ Payments & Refunds (Stripe/Payme webhooks ready)

---



**Цель:** Убедиться что все домены работают корректно, написать критичные тесты, подготовить к production.

**Приоритет 1 — Integration Testing (E2E flows)**
- [ ] Happy path: Student enrolls → completes course → gets certificate
- [ ] Payment flow: Create payment → webhook → enrollment activated
- [ ] Assessment flow: Start attempt → submit responses → auto-grade → pass/fail
- [ ] Submission flow: Create assignment → submit → review → approve
- [ ] Attendance flow: Mark attendance → lesson completed (offline)

**Приоритет 2 — Unit Tests (Critical paths)**
- [ ] Learning: Course publication, content management
- [ ] Progress: Completion cascade (lesson → module → course)
- [ ] Assessment: Grading logic (auto + manual)
- [ ] Enrollment: Access control, prerequisites
- [ ] Payment: Refund validation, idempotency
- [ ] Certificates: Generation, verification

**Приоритет 3 — Event System Validation**
- [ ] Проверить все Outbox events обрабатываются
- [ ] Проверить Signal handlers не теряют события
- [ ] Добавить идемпотентность в критичные handlers
- [ ] Celery tasks: retry logic, dead letter queue

**Приоритет 4 — Admin Interface**
- [ ] Django Admin для всех моделей
- [ ] Базовые фильтры и поиск
- [ ] Read-only поля для audit trail
- [ ] Inline editing для связанных объектов

**Приоритет 5 — API Documentation**
- [ ] drf-spectacular schema generation
- [ ] Swagger UI доступен
- [ ] Примеры запросов для всех endpoints
- [ ] Authentication flow документирован

**Приоритет 6 — Data Fixtures**
- [ ] Создать тестовые курсы (3-5 курсов)
- [ ] Тестовые пользователи (student, mentor, staff, admin)
- [ ] Тестовые enrollments и progress
- [ ] Management command для быстрого seeding

**Приоритет 7 — Performance & Monitoring**
- [ ] Проверить N+1 queries (django-debug-toolbar)
- [ ] Добавить select_related/prefetch_related где нужно
- [ ] Logging для критичных операций
- [ ] Metrics stubs (Prometheus/Grafana ready)

---



**Цель:** Менторы могут вести группы, проверять задания. Студенты получают сертификаты.

**Задачи:**
- [ ] Certificates Domain (PDF generation, verification)
- [ ] Дизайн Notifications Domain
- [ ] Email/Push уведомления для ключевых событий
- [ ] Дизайн Analytics Domain
- [ ] Dashboard для Staff/Admin

---



**Задачи:**
- [ ] Redis кеш для каталога курсов
- [ ] Вынос Coding Execution в отдельный сервис
- [ ] CDN для LessonContent
- [ ] Горизонтальное масштабирование Celery workers

**См. также:** [MICROSERVICES_ROADMAP.md](MICROSERVICES_ROADMAP.md) — детальный план экстракции доменов в микросервисы

---



**Цель:** Постепенная экстракция периферийных доменов для независимого scaling.

**Год 1:**
- Q2: Notifications Service
- Q3: Certificates Service
- Q4: Analytics Service

**Год 2:**
- Q1: Assessment Service
- Q2: Submissions Service
- Q3: Mentorship Service

**Год 3+:**
- Core остаётся монолитом (Learning, UserProgress, Identity)

**Детали:** [MICROSERVICES_ROADMAP.md](MICROSERVICES_ROADMAP.md)

---



| Вопрос | Приоритет | Блокирует |
|--------|-----------|-----------|
| Сохранять ли прогресс при повторной записи на курс? | Medium | Phase 2 |
| Как хранить исходный код из coding assessment? | High | Phase 1B |
| Sandbox для execution: внутренний или внешний сервис? | High | Phase 1B |
| Мобильное приложение: нужен ли GraphQL? | Low | Phase 3 |
