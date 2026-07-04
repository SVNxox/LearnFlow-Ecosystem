

**Дата:** 2026-06-07  
**Статус:** ПРИНЯТО  
**Версия:** 1.0

---





**Разделение:**

```
Learning Domain:
  Assignment — описание задания (homework/project)

Submissions Domain:
  Submission — попытка студента выполнить задание
  SubmissionRevision — версии попыток (студент пересдаёт)
  SubmissionReview — проверка ментора
```

**Важно:** Одно задание может иметь много submissions (разные студенты), каждый submission может иметь много revisions (пересдачи).

---



**Решение:** Унифицировать в одну сущность `Assignment`.

**Типы:**
- `theory` — текстовые ответы на вопросы
- `coding` — код-задачи (LeetCode-style)
- `project` — полноценный проект

**Связи:**
```
Lesson → Assignment(type=theory/coding)
ModuleAssessment → Assignment(type=project)
```

**Почему не `Project` как название:**
- "Project: Что такое SOLID?" — странно звучит
- Assignment — более общая абстракция

---



```
github_repository  — Backend/Frontend проекты
file_upload        — ZIP, PDF, PPTX, DOCX (дизайн, презентации)
text_answer        — Большие текстовые ответы
external_link      — Vercel, Render, Railway, YouTube, Figma
```

**Хранение:** Не делать отдельные таблицы под каждый тип.

```sql
SubmissionRevision:
  submission_type VARCHAR(20)
  payload JSONB
```

**Примеры payload:**
```json
// github_repository
{
  "github_url": "https://github.com/user/todo-api",
  "live_url": "https://todo-api-demo.vercel.app",
  "notes": "Main branch contains the final version"
}

// file_upload
{
  "file_id": "uuid",
  "file_name": "design.pdf",
  "file_size": 2048576,
  "mime_type": "application/pdf"
}

// external_link
{
  "url": "https://www.figma.com/...",
  "platform": "figma",
  "notes": "Prototype with all interactions"
}
```

---



Студент **почти всегда** пересдаёт работу.

**Схема:**
```
Submission (контейнер)
  └── SubmissionRevision 1 (первая попытка)
  └── SubmissionRevision 2 (после замечаний)
  └── SubmissionRevision 3 (финальная)
```

Ментор всегда проверяет **конкретную ревизию**, не Submission целиком.

---



```
draft              — Студент работает над submission
submitted          — Отправлено на проверку
under_review       — Ментор проверяет
changes_requested  — Ментор вернул на доработку
approved           — Принято
rejected           — Отклонено (не подлежит пересдаче)
```

**Типичный flow:**
```
draft → submitted → under_review → changes_requested
                                      ↓
                              submitted (revision 2)
                                      ↓
                              under_review → approved
```

---



**Для v1:**
```sql
SubmissionReview:
  score DECIMAL(6,2)
  feedback TEXT
  status VARCHAR(20)
```

**Пример:**
```
Score: 8/10
Status: changes_requested

Feedback:
Хорошая работа. Нужно:
- добавить тесты (coverage < 80%)
- исправить Dockerfile (COPY порядок)
- добавить API docs
```

**Построчный code review НЕ делаем сейчас** — это очень дорогая функциональность (file/line/comment). Добавим в v2 если понадобится.

---



**Разделение:**
- `AutoCheck` — автоматические проверки (tests, linting, coverage)
- `SubmissionReview` — ментор проверяет

**Пример:**
```
AutoCheck:
  ✓ Tests passed (12/12)
  ✓ Black formatting passed
  ✗ Coverage 65% (required 80%)
  
SubmissionReview (mentor):
  Score: 8/10
  Status: approved
  Feedback: "Good architecture, improve tests"
```

**Не смешивать** — автопроверки могут быть зелёными, но ментор может поставить низкий балл за архитектуру.

---



**Для v1:** Хранить только результаты проверки.

```sql
AutoCheck:
  status VARCHAR(20)  -- pending/running/passed/failed
  score DECIMAL(6,2)
  report JSONB
```

**Для v2:** Подключить:
- GitHub Actions
- GitLab CI
- Judge0 (для coding)
- Docker Sandbox

Схема БД не изменится — просто добавим воркеры которые запускают проверки и пишут в `AutoCheck`.

---



**Минимум для MVP:**

```
Student upload
    ↓
S3 temp bucket
    ↓
Virus scan (ClamAV)
    ↓
scan_passed → S3 permanent bucket
scan_failed → File rejected
```

**В БД:**
```sql
SubmissionFile:
  scan_status VARCHAR(20)  -- pending/passed/failed
  scan_result JSONB
  scanned_at TIMESTAMPTZ
```

**Дополнительные проверки:**
- **Размер файла:** zip ≤ 100MB, pdf ≤ 20MB
- **MIME type:** Проверять содержимое файла, не доверять расширению
- **Архивные бомбы:** 10KB zip → 100GB unpacked (ограничить `max_uncompressed_size`)

**Никогда не делать:**
```
Student → Upload → Mentor download
```
без сканирования.

---



**Для v1:**
```sql
SubmissionReview:
  submission_id UUID
  mentor_id UUID
  score DECIMAL(6,2)
  feedback TEXT
  status VARCHAR(20)
```

Один review = один ответственный ментор.

**Для v2:** Можно добавить:
```sql
ReviewAssignment:
  submission_id UUID
  mentor_id UUID
  role VARCHAR(20)  -- primary/secondary
```

Но сейчас это только усложнит систему.

---





**Цель:** Унифицированное описание заданий (homework, coding, project).

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| lesson_id | UUID FK NULLABLE | → courses_lesson (SET NULL). NULL если это project из assessment |
| assessment_item_id | UUID NULLABLE | Soft ref на assessment_assessmentitem |
| type | VARCHAR(20) | theory / coding / project |
| title | VARCHAR(255) | |
| description | TEXT | Markdown |
| max_score | DECIMAL(6,2) | |
| deadline_offset_days | SMALLINT NULLABLE | Дней от enrolledAt |
| submission_types_allowed | VARCHAR(100)[] | ['github_repository', 'file_upload'] |
| allowed_file_extensions | VARCHAR(200) NULLABLE | .pdf,.zip,.docx |
| max_file_size_mb | SMALLINT DEFAULT 50 | |
| auto_check_enabled | BOOLEAN DEFAULT FALSE | |
| auto_check_config | JSONB NULLABLE | Конфиг для автопроверки |
| created_by_id | UUID FK | → accounts_user |
| created_at / updated_at | TIMESTAMPTZ | |

**Constraints:**
- CHECK: `type IN ('theory', 'coding', 'project')`
- CHECK: `lesson_id IS NOT NULL OR assessment_item_id IS NOT NULL` (одно из двух обязательно)

**Indexes:**
- `idx_assignment_lesson` ON (lesson_id) WHERE lesson_id IS NOT NULL
- `idx_assignment_assessment` ON (assessment_item_id) WHERE assessment_item_id IS NOT NULL

---



**Цель:** Контейнер для попытки студента выполнить assignment.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| assignment_id | UUID FK | → submissions_assignment |
| enrollment_id | UUID FK | → courses_courseenrollment |
| student_id | UUID (denorm) | |
| status | VARCHAR(20) | draft/submitted/under_review/changes_requested/approved/rejected |
| current_revision_number | SMALLINT DEFAULT 0 | |
| final_score | DECIMAL(6,2) NULLABLE | Финальная оценка после approval |
| created_at | TIMESTAMPTZ | |
| first_submitted_at | TIMESTAMPTZ NULLABLE | Первая отправка на проверку |
| last_submitted_at | TIMESTAMPTZ NULLABLE | Последняя отправка |
| reviewed_at | TIMESTAMPTZ NULLABLE | Когда approved/rejected |
| deadline | TIMESTAMPTZ NULLABLE | Рассчитывается из deadline_offset_days |

**Index:** UNIQUE `(enrollment_id, assignment_id)`

**Constraints:**
- CHECK: `status IN ('draft', 'submitted', 'under_review', 'changes_requested', 'approved', 'rejected')`

---



**Цель:** Версии submission (студент пересдаёт после замечаний).

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| submission_id | UUID FK | → submissions_submission (CASCADE) |
| revision_number | SMALLINT | 1, 2, 3... |
| submission_type | VARCHAR(20) | github_repository / file_upload / text_answer / external_link |
| payload | JSONB | Зависит от submission_type |
| notes | TEXT NULLABLE | Комментарий студента при отправке |
| submitted_at | TIMESTAMPTZ | |

**Index:** UNIQUE `(submission_id, revision_number)`

---



**Цель:** Файлы загруженные студентом (для type=file_upload).

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| revision_id | UUID FK | → submissions_submissionrevision (CASCADE) |
| file_name | VARCHAR(255) | |
| file_size_bytes | BIGINT | |
| mime_type | VARCHAR(100) | |
| storage_path | TEXT | S3 path |
| scan_status | VARCHAR(20) | pending / running / passed / failed |
| scan_result | JSONB NULLABLE | Результат ClamAV |
| scanned_at | TIMESTAMPTZ NULLABLE | |
| uploaded_at | TIMESTAMPTZ | |

**Constraints:**
- CHECK: `scan_status IN ('pending', 'running', 'passed', 'failed')`

**Index:**
- `idx_file_scan_pending` ON (scan_status, uploaded_at) WHERE scan_status IN ('pending', 'running')

---



**Цель:** Автоматические проверки (tests, linting, coverage).

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| revision_id | UUID FK | → submissions_submissionrevision |
| check_type | VARCHAR(30) | tests / linting / coverage / docker_build / etc |
| status | VARCHAR(20) | pending / running / passed / failed / error |
| score | DECIMAL(6,2) NULLABLE | Если применимо |
| report | JSONB | Детальный отчёт |
| started_at | TIMESTAMPTZ NULLABLE | |
| completed_at | TIMESTAMPTZ NULLABLE | |

**Index:** ON (revision_id, check_type)

**Пример report:**
```json
{
  "check_type": "tests",
  "total": 12,
  "passed": 12,
  "failed": 0,
  "duration_ms": 2340
}

{
  "check_type": "coverage",
  "percentage": 65.3,
  "threshold": 80.0,
  "missing_lines": [45, 67, 89]
}
```

---



**Цель:** Проверка ментора.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| submission_id | UUID FK | → submissions_submission |
| revision_id | UUID FK | → submissions_submissionrevision |
| mentor_id | UUID FK | → accounts_user |
| score | DECIMAL(6,2) | |
| max_score | DECIMAL(6,2) | Snapshot из assignment |
| feedback | TEXT | |
| status | VARCHAR(20) | changes_requested / approved / rejected |
| reviewed_at | TIMESTAMPTZ | |

**Index:** UNIQUE `(submission_id, revision_id)`

**Constraints:**
- CHECK: `status IN ('changes_requested', 'approved', 'rejected')`

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

@dataclass
class SubmissionApproved:
    submission_id: UUID
    assignment_id: UUID
    enrollment_id: UUID
    student_id: UUID
    final_score: Decimal
    occurred_at: datetime
```



```python

@receiver(lesson_published)
def handle_lesson_published(sender, event: LessonPublished, **kwargs):
    """
    Если у урока есть assignment, инициализировать Submission
    для всех enrolled студентов (через Celery fan-out).
    """
    pass


@receiver(assessment_attempt_started)
def handle_assessment_attempt_started(sender, event, **kwargs):
    """
    Если assessment содержит project items,
    создать Assignment + Submission для студента.
    """
    pass
```

---





```
1. Lesson published → Assignment created
2. Student enrolled → Submission created (status=draft)
3. Student writes answer → SubmissionRevision 1 created
4. Student clicks "Submit" → status=submitted, SubmissionSubmitted event
5. Mentor reviews → SubmissionReview created (score=8/10, status=approved)
6. status=approved → SubmissionApproved event
7. UserProgress listens → homework_submitted=True → check lesson completion
```



```
1. ModuleAssessment item type=project → Assignment created
2. Student starts attempt → Submission created
3. Student submits GitHub URL → SubmissionRevision 1:
   {
     "github_url": "...",
     "live_url": "...",
     "notes": "..."
   }
4. AutoCheck runs (if enabled):
   - Clone repo
   - Run tests
   - Check coverage
   - Build Docker
   → AutoCheck results stored
5. Mentor reviews:
   - Reads code
   - Checks AutoCheck results
   - Leaves feedback
   → SubmissionReview (score=85/100, status=changes_requested)
6. Student fixes issues → SubmissionRevision 2
7. Mentor approves → status=approved
8. SubmissionReviewed event → Assessment Domain
9. Assessment updates AssessmentResponse.final_points
10. Assessment checks if all items graded → ModuleAssessmentPassed
```



```
1. Student uploads design.pdf
2. File saved to S3 temp → SubmissionFile created (scan_status=pending)
3. Celery task:
   - Download from S3 temp
   - Run ClamAV
   - If passed: move to S3 permanent, scan_status=passed
   - If failed: delete file, scan_status=failed, notify student
4. If passed → SubmissionRevision payload updated with file_id
5. Student can submit → Mentor reviews
```

---





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



**Контекст:** Студент пересдаёт работу после замечаний ментора.

**Решение:** `Submission` (контейнер) + `SubmissionRevision` (версии).

**Причина:** Студент почти всегда пересдаёт. Нужна история изменений.

**Последствия:** Ментор всегда проверяет конкретную ревизию, не Submission целиком.

---



**Контекст:** Разные типы submission хранят разные данные (GitHub URL vs uploaded files vs text).

**Отклонённые варианты:**
- Отдельные таблицы для каждого типа — слишком много таблиц
- Отдельные поля `github_url`, `file_id`, `text_answer` — NULL everywhere

**Решение:** `SubmissionRevision.payload JSONB` с разной структурой по типу.

**Причина:** Гибкость, легко добавлять новые типы без миграций.

**Последствия:** Валидация payload на уровне application logic, не DB constraints.

---



**Контекст:** Нужны и автоматические проверки (tests, linting) и ручная проверка ментора.

**Решение:** `AutoCheck` (автомат) ≠ `SubmissionReview` (ментор). Разные таблицы.

**Причина:**
- Автопроверка может быть зелёной, но ментор поставит низкий балл за архитектуру
- Ментор может одобрить даже если coverage < 80% (есть причины)
- Не смешивать источники оценки

**Последствия:** UI должен показывать оба результата отдельно.

---



**Контекст:** Студенты загружают ZIP, PDF, DOCX — потенциальный вектор атаки.

**Решение:** Все загруженные файлы проходят ClamAV scan перед доступом ментора.

**Причина:** Безопасность. Нельзя давать ментору скачивать непроверенные файлы.

**Последствия:**
- Дополнительная задержка (секунды)
- Celery worker для сканирования
- S3 temp bucket для непроверенных файлов

---



1. ✅ Дизайн Submissions завершён
2. 🟡 Дизайн Mentorship Domain (ментор как reviewer)
3. 🟡 Дизайн Certificates Domain
4. ⬜ Обновить `docs/DATABASE.md`
5. ⬜ Добавить ADR-014..018 в `docs/DECISIONS.md`
