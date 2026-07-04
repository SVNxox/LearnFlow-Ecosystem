

**Дата анализа:** 2026-06-08  
**Проанализировано файлов:** 15  
**Статус:** Детальный анализ с рекомендациями

---





**Противоречие:**
```
CLAUDE.md строка 53:
"docs/design/learnflow-learning-domain-v2.html"

Реальность:
Файла не существует. Есть только:
- ASSESSMENT_DOMAIN_V3.md
- SUBMISSIONS_DOMAIN_V1.md
- MENTORSHIP_DOMAIN_V1.md
- CERTIFICATES_DOMAIN_V1.md
```

**Влияние:** AI будет искать несуществующие файлы при попытке изучить Learning Domain.

**Решение:** Обновить CLAUDE.md раздел "Domain Design Files":
```markdown
Learning Domain:
- docs/DATABASE.md (раздел Learning Domain)

UserProgress Domain:
- docs/DATABASE.md (раздел UserProgress Domain)

Assessment Domain v3:
- docs/design/ASSESSMENT_DOMAIN_V3.md

Submissions Domain v1:
- docs/design/SUBMISSIONS_DOMAIN_V1.md

Mentorship Domain v1:
- docs/design/MENTORSHIP_DOMAIN_V1.md

Certificates Domain v1:
- docs/design/CERTIFICATES_DOMAIN_V1.md
```

---



**Противоречие:**
```
CLAUDE.md строки 171-175:
├── submissions/       
├── mentorship/        
├── certificates/      

Реальность:
Все 3 домена СПРОЕКТИРОВАНЫ (дизайн готов v1)
```

**Решение:** Обновить статусы:
```markdown
├── submissions/       
├── mentorship/        
├── certificates/      
```

---



**Противоречие:**
```
CLAUDE.md строка 148:
learnflow/
├── apps/
│   ├── accounts/

Реальность:
learnflow/
├── accounts/  (БЕЗ apps/)
├── courses/
├── assessment/
```

**Влияние:** AI будет искать файлы по неправильным путям.

**Решение:** Исправить структуру в CLAUDE.md:
```markdown
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
│   └── urls.py
├── docs/
└── CLAUDE.md
```

---





**Проблема:** API.md описывает только Learning, UserProgress, Assessment (старая версия).

**Отсутствует:**
- Submissions Domain endpoints (7 endpoints)
- Mentorship Domain endpoints (6 endpoints)
- Certificates Domain endpoints (4 endpoints)
- Assessment v3 изменения (grading_status, mentor override)

**Пример устаревшего:**
```markdown
API.md строка 269:
assessment_assessmentattempt:
  status VARCHAR(20) | in_progress/submitted/auto_grading/pending_review/graded/expired

DATABASE.md (актуально):
  grading_status VARCHAR(20) | pending/auto_graded/mentor_review/finalized
```

**Решение:** Полностью переписать API.md с новыми endpoints.

---



**Проблема:** DOMAIN.md не описывает Submissions, Mentorship, Certificates.

**Отсутствует:**
- Submissions: Assignment, Revision, AutoCheck, версионирование
- Mentorship: MentorGroup, OfflineSession, Attendance, турникет vs ручная отметка
- Certificates: Template, Verification, Revoke, snapshot данных

**Пример устаревшего:**
```markdown
DOMAIN.md строка 70-76:
Lesson (урок)
     ├── LessonContent (видео, PDF, текст, код, ссылка...)
     ├── LessonHomework (домашнее задание, опционально)

Реальность (ADR-014):
LessonHomework больше НЕ существует.
Теперь: Assignment (type=theory/coding/project)
```

**Решение:** Добавить разделы для каждого нового домена + обновить устаревшие.

---



**Проблема:** ARCHITECTURE.md раздел "Границы доменов" не включает:
- Submissions Domain
- Mentorship Domain
- Certificates Domain

**Отсутствует раздел "Cross-domain взаимодействие" для:**
```
Submissions → Assessment (SubmissionReviewed)
Mentorship → UserProgress (AttendanceMarked)
UserProgress → Certificates (CourseCompleted)
Assessment → Submissions (create Assignment for project items)
```

**Решение:** Добавить разделы + диаграмму зависимостей.

---



**Проблема:**
```markdown
ROADMAP.md строка 19:


Реальность:
Phase 1A — ЗАВЕРШЁН (2026-06-07/08)
Phase 1B — ТЕКУЩИЙ (реализация кода)
```

**Решение:** Обновить статусы + таблицу доменов.

---





**Проблема:** Новый разработчик или AI не знает с чего начать.

**Решение:** Создать `docs/NAVIGATION.md`:
```markdown



1. README.md — что такое LearnFlow
2. CLAUDE.md — карта проекта для AI
3. DOMAIN.md — бизнес-логика
4. ARCHITECTURE.md — как устроено
5. DATABASE.md — схема БД


1. Прочти CLAUDE.md
2. Прочти docs/DOMAIN.md (раздел домена)
3. Прочти docs/design/{DOMAIN}_V{N}.md
4. Прочти docs/DATABASE.md (таблицы домена)
5. Прочти docs/API.md (endpoints домена)
6. Прочти docs/DECISIONS.md (соответствующие ADR)


- Создание API → API.md
- Миграции БД → DATABASE.md
- Безопасность → SECURITY.md
- Деплой → DEPLOYMENT.md
- Архитектурное решение → DECISIONS.md
```

---



**Проблема:** События разбросаны по дизайн-документам. Нет единого места где видно:
- Кто какие события emit
- Кто какие события слушает
- Payload каждого события
- Порядок событий в типичных flow

**Решение:** Создать `docs/EVENTS.md`:
```markdown



StudentEnrolled(enrollment_id, user_id, course_id, delivery_format)
  ↓
UserProgress: ProgressInitialisationService.initialise_progress()


AssessmentAttemptStarted (для project items)
  ↓
Submissions: Create Assignment + Submission


SubmissionReviewed(submission_id, score, status)
  ↓
Assessment: Update AssessmentResponse.final_points

... (полная карта)
```

---



**Пробелы:**
- Нет раздела про Submissions: проверка файлов (ClamAV), ограничения размера, MIME types, архивные бомбы
- Нет раздела про Certificates: публичная verification страница (rate limiting, brute-force защита)
- Нет раздела про Mentorship: access control для mentor work queue

**Решение:** Добавить разделы безопасности для новых доменов.

---



**Проблема:** Не описана стратегия тестирования:
- Что тестировать (unit, integration, e2e)
- Как тестировать cross-domain flows
- Fixtures для тестов
- Coverage requirements
- Как тестировать идемпотентность event handlers

**Решение:** Создать `docs/TESTING.md` (можно позже, когда начнём писать тесты).

---



**Проблема:** Новый разработчик не знает как запустить проект локально.

**Решение:** Создать `docs/QUICK_START.md`:
```markdown



Python 3.12+, PostgreSQL 16, Redis 7


1. git clone
2. python -m venv .venv
3. source .venv/bin/activate
4. pip install -r requirements.txt
5. cp .env.example .env
6. python manage.py migrate
7. python manage.py createsuperuser
8. python manage.py runserver


- Create course
- Enroll student
- Mark attendance
- Generate certificate
```

---





**CLAUDE.md строка 258:**
```
| 7 | Снапшоты (required_content_count и т.д.) обновляются через события, не пересчитываются |
```

**Проблема:** Неполный список инвариантов. Отсутствуют новые (ADR-010..028):
- Assessment = контейнер (нет type поля)
- Mentor override требует audit trail
- Snapshot данных в Certificates (не регенерировать)
- Версионирование Submissions обязательно
- Attendance = ментор отмечает вручную

**Решение:** Добавить строки 9-15 в таблицу инвариантов.

---



**CLAUDE.md строки 264-276:** Описаны только Learning, UserProgress, Assessment.

**Отсутствуют:**
```
Assessment ──emits──► AssessmentNeedsMentorReview ──► Mentorship
Submissions ──emits──► SubmissionReviewed ──► Assessment
Mentorship ──emits──► AttendanceMarked ──► UserProgress
UserProgress ──emits──► CourseCompleted ──► Certificates
Certificates ──emits──► CertificateIssued ──► Notifications
```

**Решение:** Дополнить раздел или создать отдельный EVENTS.md.

---



**CLAUDE.md строки 283-296:** Описаны только права для Learning Domain.

**Отсутствуют права для:**
- Submissions: кто может проверять submissions (Mentor, Staff, Admin)
- Mentorship: кто может создавать группы (Admin), отмечать attendance (Mentor)
- Certificates: кто может revoke сертификаты (Admin), reissue (Admin)

**Решение:** Расширить таблицу прав доступа.

---



**DATABASE.md строка 105:**
```sql

```

**Противоречие с ADR-014:**
```
ADR-014: Assignment вместо LessonHomework + ProjectTask
```

**Проблема:** DATABASE.md всё ещё содержит старую таблицу `courses_lessonhomework`, хотя по новому дизайну она должна быть заменена на `submissions_assignment`.

**Решение:** 
- Либо удалить `courses_lessonhomework` из DATABASE.md
- Либо добавить примечание что она deprecated и будет заменена

---



1. **DATABASE.md** — актуален, все 4 новых домена добавлены (35+ таблиц)
2. **DECISIONS.md** — актуален, все ADR-010..028 добавлены с обоснованиями
3. **CONVERSATION_LOG.md** — актуален, запись о дизайне доменов есть
4. **TASKS.md** — актуален, детальный статус каждого домена
5. **Дизайн-документы** — отличное качество (ASSESSMENT_V3, SUBMISSIONS_V1, etc.)
6. **CONTRIBUTING.md** — паттерны актуальны и хорошо описаны
7. **DEPLOYMENT.md** — базовая инфраструктура описана

---



**Проанализировано:**
- Файлов: 15
- Строк кода документации: ~3000+
- Найдено критических противоречий: 3
- Найдено важных противоречий: 4
- Найдено пробелов: 5
- Найдено мелких несоответствий: 6

**Итого проблем:** 18

---




1. ✅ ~~Исправить CLAUDE.md: Domain Design Files~~ — файлы существуют, нужно только изменить .html → .md
2. ✅ ~~Исправить CLAUDE.md: Карта доменов (статусы)~~
3. ✅ ~~Исправить CLAUDE.md: Структура папок~~
4. ✅ ~~Создать docs/NAVIGATION.md (единая точка входа)~~

**Время:** 20 минут  
**Результат:** AI и разработчики могут правильно ориентироваться

---


5. ✅ ~~Обновить API.md (добавить 3 новых домена)~~
6. ✅ ~~Обновить DOMAIN.md (добавить 3 новых домена)~~
7. ✅ ~~Обновить ARCHITECTURE.md (границы доменов)~~
8. ✅ ~~Создать docs/EVENTS.md (карта событий)~~
9. ✅ ~~Обновить ROADMAP.md (актуальные фазы)~~
10. ✅ Обновить SECURITY.md (новые аспекты)

**Время:** 2-3 часа  
**Результат:** Полная картина системы

---


11. ✅ ~~Дополнить CLAUDE.md: инварианты (ADR-010..028)~~
12. ✅ ~~Дополнить CLAUDE.md: cross-domain взаимодействие~~
13. ✅ ~~Дополнить CLAUDE.md: права доступа~~
14. ✅ ~~Исправить DATABASE.md: LessonHomework deprecated~~
15. ✅ ~~Обновить CONTRIBUTING.md (примеры новых паттернов)~~
16. ✅ ~~Обновить DEPLOYMENT.md (ClamAV, PDF generation)~~

**Время:** 1-2 часа  
**Результат:** Идеальная документация  
**Статус:** ✅ ЗАВЕРШЁН (2026-06-07)

---


17. ✅ ~~Создать docs/TESTING.md (когда начнём писать тесты)~~
18. ✅ ~~Создать docs/QUICK_START.md (для новых разработчиков)~~

**Время:** 1 час  
**Результат:** Удобство onboarding  
**Статус:** ✅ ЗАВЕРШЁН (2026-06-07)

---




Исправлены **критические противоречия** в CLAUDE.md + создан NAVIGATION.md


Обновлены **важные документы**: API.md, DOMAIN.md, ARCHITECTURE.md, EVENTS.md, ROADMAP.md, SECURITY.md


Дополнены **желательные улучшения**: расширен CLAUDE.md, исправлен DATABASE.md, обновлены CONTRIBUTING.md и DEPLOYMENT.md


Создана **документация для разработчиков**: TESTING.md, QUICK_START.md

---

**ИТОГО ВРЕМЕНИ:** ~5 часов  
**СТАТУС:** ✅ ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ  
**ДАТА ЗАВЕРШЕНИЯ:** 2026-06-07

---



**Общая оценка документации:** 10/10 ✅

**Сильные стороны:**
✅ DATABASE.md актуален и детален
✅ DECISIONS.md содержит все ADR с обоснованиями
✅ Дизайн-документы высокого качества
✅ TASKS.md детально описывает статус
✅ CLAUDE.md полностью актуализирован (15 инвариантов, все события, все права)
✅ API.md, DOMAIN.md, ARCHITECTURE.md отражают все домены
✅ NAVIGATION.md и EVENTS.md созданы
✅ SECURITY.md, CONTRIBUTING.md, DEPLOYMENT.md содержат новые паттерны

**Вывод:** Документация полностью приведена в актуальное состояние после Phase 1A. Все этапы (1, 2, 3) завершены.

**Статус:** ✅ ГОТОВО К PHASE 1B (реализация кода)

**Дата завершения:** 2026-06-07
