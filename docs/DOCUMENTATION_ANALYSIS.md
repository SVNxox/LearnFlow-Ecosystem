

**Дата:** 2026-06-07  
**Цель:** Определить что нужно обновить/создать для навигации по проекту

---



1. **DATABASE.md** — ✅ Обновлён (добавлены 4 новых домена, 35+ таблиц)
2. **DECISIONS.md** — ✅ Обновлён (добавлены ADR-010..028)
3. **CONVERSATION_LOG.md** — ✅ Обновлён (запись о дизайне доменов)
4. **CLAUDE.md** — ✅ Обновлён (статусы доменов)

---




**Текущее состояние:** Описаны только Learning, UserProgress, Assessment (старая версия)

**Что нужно добавить:**
- Submissions Domain endpoints
- Mentorship Domain endpoints
- Certificates Domain endpoints
- Обновить Assessment endpoints под v3 (новые поля, grading_status, mentor override)

**Приоритет:** 🔴 ВЫСОКИЙ

---


**Текущее состояние:** Описаны базовые концепции (online/offline, роли, учебный флоу)

**Что нужно добавить:**
- Раздел про Submissions (Assignment, Revision, AutoCheck)
- Раздел про Mentorship (MentorGroup, OfflineSession, Attendance)
- Раздел про Certificates (Template, Verification, Revoke)
- Обновить Assessment раздел (без type поля, mentor override)
- Обновить бизнес-правила (BR-11..20 для новых доменов)

**Приоритет:** 🔴 ВЫСОКИЙ

---


**Текущее состояние:** Описана общая архитектура, но нет новых доменов

**Что нужно добавить:**
- Обновить "Границы доменов" — добавить Submissions, Mentorship, Certificates
- Обновить "Cross-domain взаимодействие" с новыми событиями
- Диаграмма зависимостей доменов (кто кого слушает)

**Приоритет:** 🟡 СРЕДНИЙ

---


**Текущее состояние:** Устарел (Phase 1 — "текущая")

**Что нужно обновить:**
- ✅ Phase 1A — завершён (дизайн доменов)
- 🔴 Phase 1B — реализация кода (сейчас)
- Обновить таблицу статусов доменов

**Приоритет:** 🟡 СРЕДНИЙ

---


**Текущее состояние:** Описана общая безопасность

**Что нужно добавить:**
- Submissions: проверка файлов на вирусы (ClamAV)
- Submissions: ограничения размера файлов, MIME types
- Certificates: публичная verification страница (rate limiting)
- Mentorship: access control для mentor work queue

**Приоритет:** 🟡 СРЕДНИЙ

---


**Текущее состояние:** Паттерны Selector/Service/Event актуальны

**Что можно добавить (опционально):**
- Примеры для новых доменов
- Паттерн версионирования (SubmissionRevision)
- Паттерн mentor override с audit log

**Приоритет:** 🟢 НИЗКИЙ (не обязательно сейчас)

---


**Текущее состояние:** Общая инфраструктура актуальна

**Что можно добавить (опционально):**
- Celery queues для новых доменов (file_scan, pdf_generation)
- ClamAV setup для virus scanning
- WeasyPrint/ReportLab для PDF generation

**Приоритет:** 🟢 НИЗКИЙ (не обязательно сейчас)

---




**Цель:** Единая точка входа для разработчиков и AI

**Содержание:**
```markdown



1. Начни с README.md
2. Прочти CLAUDE.md (карта проекта)
3. Изучи DOMAIN.md (бизнес-логика)
4. Посмотри ARCHITECTURE.md (как устроено)


- Схема БД → DATABASE.md
- API endpoints → API.md
- Архитектурные решения → DECISIONS.md
- Текущие задачи → TASKS.md


- Identity (accounts/) — готов
- Learning (courses/) — в разработке
- UserProgress (progress/) — дизайн готов
- Assessment (assessment/) — дизайн готов v3
- Submissions (submissions/) — дизайн готов v1
- Mentorship (mentorship/) — дизайн готов v1
- Certificates (certificates/) — дизайн готов v1


- docs/design/ASSESSMENT_DOMAIN_V3.md
- docs/design/SUBMISSIONS_DOMAIN_V1.md
- docs/design/MENTORSHIP_DOMAIN_V1.md
- docs/design/CERTIFICATES_DOMAIN_V1.md
```

**Приоритет:** 🔴 ВЫСОКИЙ

---


**Цель:** Карта всех событий и их связей между доменами

**Содержание:**
```markdown



- StudentEnrolled → initialise progress
- LessonPublished → unlock lesson
- CoursePublished → ...


- CourseCompleted → EnrollmentCompleted


- ModuleCompleted → unlock assessment


- ModuleAssessmentPassed → unlock next module


- SubmissionReviewed → update response points


- AttendanceMarked → complete lesson (offline)


- CourseCompleted → generate certificate


- CertificateIssued → send email
```

**Приоритет:** 🟡 СРЕДНИЙ

---


**Цель:** Быстрый старт для локальной разработки

**Содержание:**
```markdown



- Python 3.12+
- PostgreSQL 16
- Redis 7


1. Clone repo
2. Create .env
3. Install deps
4. Run migrations
5. Create superuser
6. Run server


...


- Create course
- Enroll student
- Mark attendance
```

**Приоритет:** 🟢 НИЗКИЙ (можно позже)

---


**Цель:** Стратегия тестирования

**Содержание:**
- Unit tests (selectors, services)
- Integration tests (cross-domain flows)
- Fixtures (pytest)
- Coverage requirements

**Приоритет:** 🟢 НИЗКИЙ (когда начнём писать тесты)

---




1. 🔴 Создать **docs/NAVIGATION.md** — единая точка входа
2. 🔴 Обновить **API.md** — добавить новые endpoints
3. 🔴 Обновить **DOMAIN.md** — описать новые домены


4. 🟡 Обновить **ARCHITECTURE.md** — добавить новые домены
5. 🟡 Создать **docs/EVENTS.md** — карта событий
6. 🟡 Обновить **ROADMAP.md** — актуализировать статус
7. 🟡 Обновить **SECURITY.md** — добавить новые аспекты безопасности


8. 🟢 Обновить **CONTRIBUTING.md** — примеры новых паттернов
9. 🟢 Обновить **DEPLOYMENT.md** — новые зависимости
10. 🟢 Создать **docs/QUICK_START.md**
11. 🟢 Создать **docs/TESTING.md**

---



**Обязательно обновить:** 3 файла (API.md, DOMAIN.md, NAVIGATION.md)  
**Важно обновить:** 4 файла (ARCHITECTURE.md, ROADMAP.md, SECURITY.md, EVENTS.md)  
**Можно позже:** 4 файла (CONTRIBUTING.md, DEPLOYMENT.md, QUICK_START.md, TESTING.md)

**Оценка времени:**
- Этап 1 (критично): ~2-3 часа
- Этап 2 (важно): ~2 часа
- Этап 3 (позже): ~1-2 часа

**Всего:** ~5-7 часов работы над документацией
