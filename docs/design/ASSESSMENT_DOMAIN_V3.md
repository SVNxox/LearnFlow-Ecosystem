

**Дата:** 2026-06-07  
**Статус:** ПРИНЯТО  
**Версия:** 3.0 (полный редизайн)

---





❌ **Отклонено:** `ModuleAssessment.type` (quiz/project/interview/mixed)  
✅ **Решение:** Assessment = набор `AssessmentItem`. Состав определяет "тип" автоматически.

**Примеры:**

```
Python Basics Assessment:
  ├─ 5× single_choice
  ├─ 2× multiple_choice
  ├─ 2× text_answer
  └─ 1× coding

Django Project Assessment:
  └─ 1× project

Career Ready Module Assessment:
  ├─ coding
  ├─ project
  └─ interview
```

Assessment автоматически "mixed" если содержит разные типы.

---



**Структура баллов:**

```sql
AssessmentAttempt:
  max_score DECIMAL(8,2)           -- Максимально возможный балл
  final_score DECIMAL(8,2)         -- Финальный результат
  percentage DECIMAL(5,2)          -- final_score / max_score * 100
  passed BOOLEAN                   -- percentage >= passing_percentage
  
  grading_status VARCHAR(20):
    - pending          -- Только создан
    - auto_graded      -- Авто-оценка завершена (для choice/coding)
    - mentor_review    -- Ожидает проверки ментора
    - finalized        -- Полностью проверен, результат финальный
```

**На уровне вопроса:**

```sql
AssessmentResponse:
  auto_points DECIMAL(6,2)         -- Авто-оценка (NULL если manual-only)
  mentor_points DECIMAL(6,2)       -- Ментор override (NULL если не пересмотрено)
  final_points DECIMAL(6,2)        -- = COALESCE(mentor_points, auto_points)
  
  reviewed_by_id UUID              -- Ментор который пересмотрел
  reviewed_at TIMESTAMPTZ
  review_comment TEXT              -- Почему изменил балл
```

**История изменений:**

```sql
AssessmentReviewLog:
  response_id UUID FK
  old_score DECIMAL(6,2)
  new_score DECIMAL(6,2)
  mentor_id UUID
  reason TEXT
  created_at TIMESTAMPTZ
```

**Зачем:** Через год придут споры "почему система дала 70, а ментор 90?" — история всё покажет.

---



```
single_choice      → Авто-оценка (instantly)
multiple_choice    → Авто-оценка (instantly)
text_answer        → Ментор проверяет
coding             → Авто-оценка (async execution) + ментор может пересмотреть
project            → Submissions Domain → ментор проверяет
interview          → MVP: текстовый ответ + ментор проверяет
                     (Live-интервью — Phase 2)
```

---



**Правило:** Assessment НЕ хранит проектные файлы/код.

**Схема:**

```
AssessmentItem(type=project)
    ↓ создаёт
ProjectTask (в Submissions Domain)
    ↓ студент делает
ProjectSubmission
    ↓ ментор проверяет
SubmissionReviewed (event)
    ↓ Assessment слушает
AssessmentResponse.final_points обновляется
    ↓ если всё проверено
ModuleAssessmentPassed → UserProgress
```

**Важно:** `AssessmentResponse.submission_id` — soft reference (UUID без FK).

---



**Для v1:**
- `interview` тип существует в `AssessmentItem.type`
- Реализация: `mentor_review_required=True`
- Студент отвечает текстом (как `text_answer`)
- Ментор проверяет вручную
- Выставляет баллы

**Для v2 (Phase 2):**
- Отдельная таблица `InterviewSession`
- Live Zoom/Google Meet интегрция
- Scheduled slots
- Recording

**Решение:** MVP killer избежан. Live-интервью позже.

---





| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| module_id | UUID FK UNIQUE | → courses_module |
| title | VARCHAR(255) | |
| instructions | TEXT | |
| passing_percentage | DECIMAL(5,2) | 0–100. Например 70.00 |
| max_attempts | SMALLINT NULLABLE | NULL = unlimited |
| time_limit_minutes | SMALLINT NULLABLE | NULL = без ограничений |
| shuffle_items | BOOLEAN DEFAULT FALSE | |
| is_published | BOOLEAN DEFAULT FALSE | |
| created_by_id | FK → accounts_user | |
| created_at / updated_at | TIMESTAMPTZ | |

**Изменения:**
- ✅ Убрано поле `type` — состав определяется через items
- ✅ `passing_score` → `passing_percentage` (более гибко)

---



| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| assessment_id | FK | |
| type | VARCHAR(20) | single_choice/multiple_choice/text_answer/coding/project/interview |
| order | SMALLINT | |
| title | TEXT | Текст вопроса/задания |
| description | TEXT NULLABLE | Дополнительный контекст |
| max_points | DECIMAL(6,2) | |
| partial_credit_strategy | VARCHAR(20) | all_or_nothing / proportional |
| explanation | TEXT NULLABLE | Показывается после оценки |
| mentor_review_required | BOOLEAN DEFAULT FALSE | TRUE для text_answer/project/interview |
| coding_language | VARCHAR(30) NULLABLE | Только для type=coding |
| starter_code | TEXT NULLABLE | Только для type=coding |
| sample_answer | TEXT NULLABLE | Для ментора (text_answer) |
| min_word_count | SMALLINT NULLABLE | Только для type=text_answer |
| submission_requirements | TEXT NULLABLE | Только для type=project |

**Изменения:**
- ✅ Добавлено `mentor_review_required` — явно маркирует manual grading
- ✅ `type` включает `interview`

---



| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| enrollment_id | FK → courses_courseenrollment | |
| assessment_id | FK → assessment_moduleassessment | |
| user_id | UUID (denorm) | |
| attempt_number | SMALLINT | 1, 2, 3... |
| grading_status | VARCHAR(20) | pending/auto_graded/mentor_review/finalized |
| started_at | TIMESTAMPTZ | |
| submitted_at | TIMESTAMPTZ NULLABLE | |
| graded_at | TIMESTAMPTZ NULLABLE | Когда finalized |
| expires_at | TIMESTAMPTZ NULLABLE | Если time_limit установлен |
| max_score | DECIMAL(8,2) | Snapshot при создании |
| final_score | DECIMAL(8,2) NULLABLE | Сумма final_points из responses |
| percentage | DECIMAL(5,2) NULLABLE | final_score / max_score * 100 |
| passed | BOOLEAN NULLABLE | percentage >= passing_percentage |
| mentor_note | TEXT NULLABLE | Общий комментарий ментора |

**Index:** UNIQUE `(enrollment_id, assessment_id, attempt_number)`

**Изменения:**
- ✅ `status` → `grading_status` (четче)
- ✅ Добавлены статусы: `auto_graded`, `mentor_review`, `finalized`
- ✅ Убрано `graded_by_id` — теперь это в ReviewLog

---



| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| attempt_id | FK → assessment_assessmentattempt | |
| item_id | FK → assessment_assessmentitem | |
| selected_option_ids | UUID[] | Для choice-типов |
| text_response | TEXT NULLABLE | Для text_answer/interview |
| submitted_code | TEXT NULLABLE | Для coding |
| coding_language | VARCHAR(30) NULLABLE | Для coding |
| submission_id | UUID NULLABLE (soft ref) | Для project → Submissions Domain |
| is_graded | BOOLEAN DEFAULT FALSE | |
| auto_points | DECIMAL(6,2) NULLABLE | Авто-оценка |
| mentor_points | DECIMAL(6,2) NULLABLE | Ментор override |
| final_points | DECIMAL(6,2) NULLABLE | COALESCE(mentor_points, auto_points) |
| is_correct | BOOLEAN NULLABLE | Для choice items |
| reviewed_by_id | UUID NULLABLE | Ментор который пересмотрел |
| reviewed_at | TIMESTAMPTZ NULLABLE | |
| review_comment | TEXT NULLABLE | Почему изменил балл |

**Index:** UNIQUE `(attempt_id, item_id)`

**Изменения:**
- ✅ `graded_by` убрано — заменено на `reviewed_by_id`
- ✅ Добавлены: `auto_points`, `mentor_points`, `final_points`
- ✅ Добавлены: `reviewed_by_id`, `reviewed_at`, `review_comment`

---



| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| response_id | FK → assessment_assessmentresponse | |
| attempt_id | UUID (denorm) | Для быстрых запросов |
| old_score | DECIMAL(6,2) | До изменения |
| new_score | DECIMAL(6,2) | После изменения |
| mentor_id | UUID FK → accounts_user | |
| reason | TEXT | Почему изменил |
| created_at | TIMESTAMPTZ | |

**Зачем:** Audit trail для споров. Показывает кто, когда, почему изменил оценку.

---



| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| item_id | FK → assessment_assessmentitem | |
| text | TEXT | |
| is_correct | BOOLEAN | |
| order | SMALLINT | |
| explanation | TEXT NULLABLE | |

---



| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| item_id | FK → assessment_assessmentitem | |
| input | TEXT | stdin или аргументы |
| expected_output | TEXT | |
| points | DECIMAL(5,2) NULLABLE | NULL = equal share |
| time_limit_ms | INT DEFAULT 2000 | |
| memory_limit_mb | INT DEFAULT 128 | |
| is_hidden | BOOLEAN DEFAULT FALSE | Скрыт от студента |
| is_sample | BOOLEAN DEFAULT FALSE | Показывается в условии |
| order | SMALLINT | |

---



| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| response_id | FK → assessment_assessmentresponse | |
| test_case_id | FK → assessment_codingtestcase | |
| passed | BOOLEAN | |
| actual_output | TEXT NULLABLE | |
| execution_time_ms | INT NULLABLE | |
| memory_used_mb | INT NULLABLE | |
| error_message | TEXT NULLABLE | |
| points_earned | DECIMAL(5,2) | |

---





```yaml
Assessment:
  title: "Python Basics — Final Test"
  passing_percentage: 70.00
  max_attempts: 3
  time_limit_minutes: 90
  max_score: 100  

Items:
  1. single_choice (10 pts) — "Что такое list comprehension?"
  2. single_choice (10 pts) — "Какой метод используется для..."
  3. single_choice (10 pts)
  4. single_choice (10 pts)
  5. single_choice (10 pts)
  6. multiple_choice (10 pts) — "Выберите все mutable типы"
  7. multiple_choice (10 pts)
  8. text_answer (15 pts) — "Объясните разницу между list и tuple"
  9. text_answer (15 pts) — "Что такое GIL?"
  10. coding (20 pts) — "Напишите функцию fibonacci(n)"

Total: 100 pts
Pass: 70 pts
```

**Grading flow:**
1. Студент submit → `grading_status=pending`
2. Auto-grade items 1-7, 10 → `auto_points` заполняются
3. `grading_status=mentor_review` (т.к. есть text_answer)
4. Ментор проверяет items 8-9 → `mentor_points`
5. Ментор может пересмотреть item 10 (coding) → `mentor_points` override
6. `grading_status=finalized`, `final_score` подсчитывается
7. Если `passed=True` → событие `ModuleAssessmentPassed`

---



```yaml
Assessment:
  title: "Django Blog API — Final Project"
  passing_percentage: 75.00
  max_attempts: 1
  time_limit_minutes: NULL  

Items:
  1. project (100 pts) — "Создать Blog API"
     Requirements:
       - JWT authentication
       - Posts CRUD
       - Comments
       - Docker setup
       - Tests (>80% coverage)
       - API docs (Swagger)

Total: 100 pts
Pass: 75 pts
```

**Grading flow:**
1. Студент создаёт attempt
2. Item type=project → создаётся `ProjectTask` в Submissions Domain
3. Студент делает `ProjectSubmission` (GitHub repo URL)
4. Ментор проверяет через Submissions Domain
5. Ментор выставляет 85/100
6. Событие `SubmissionReviewed` → Assessment
7. `AssessmentResponse.final_points = 85`
8. `grading_status=finalized`, `passed=True`
9. Событие `ModuleAssessmentPassed` → UserProgress

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



```python

@receiver(submission_reviewed)
def handle_submission_reviewed(sender, event: SubmissionReviewed, **kwargs):
    """
    Обновить AssessmentResponse.final_points
    когда проект проверен в Submissions Domain.
    """
    response = AssessmentResponse.objects.get(submission_id=event.submission_id)
    response.mentor_points = event.score
    response.final_points = event.score
    response.reviewed_by_id = event.mentor_id
    response.reviewed_at = timezone.now()
    response.save()
    
    
    GradingService.check_attempt_completion(response.attempt_id)
```

---





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



**Контекст:** Ментор может пересмотреть авто-оценку. Нужна прозрачность.

**Решение:**
- `AssessmentResponse`: `auto_points`, `mentor_points`, `final_points`
- `AssessmentReviewLog`: audit trail всех изменений

**Причина:** Споры студент/ментор через год. История покажет кто и почему изменил.

**Последствия:** Дополнительная таблица, но критична для доверия к платформе.

---



**Контекст:** Assessment item type=project требует кодовую базу/файлы/GitHub repo.

**Решение:** Assessment НЕ хранит проекты. Создаёт `ProjectTask` в Submissions Domain. Результат возвращается через событие `SubmissionReviewed`.

**Причина:**
- Разделение ответственности: Assessment = оценивание, Submissions = хранение работ
- Submissions может расти независимо (versioning, diff, CI integration)
- Assessment остаётся lightweight

**Последствия:** Cross-domain event dependency. Submissions Domain обязателен для project items.

---



**Контекст:** Нужны интервью с менторами. Live-интервью сложны (scheduling, video, recording).

**Решение для v1:** `interview` тип = текстовый ответ + ментор проверяет (как `text_answer` с другим названием).

**Решение для v2:** Отдельная таблица `InterviewSession`, Zoom integration, scheduling.

**Причина:** MVP killer avoidance. Live-интервью — Phase 2.

**Последствия:** v1 ограничен async интервью. Live появится позже.

---



1. ✅ Дизайн Assessment завершён
2. 🟡 Дизайн Submissions Domain (связь с project items)
3. 🟡 Дизайн Mentorship Domain (ментор как reviewer)
4. 🟡 Дизайн Certificates Domain (после CourseCompleted)
5. ⬜ Обновить `docs/DATABASE.md` с новой схемой
6. ⬜ Добавить ADR-010, ADR-011, ADR-012, ADR-013 в `docs/DECISIONS.md`
7. ⬜ Обновить `docs/CONVERSATION_LOG.md`
8. ⬜ Обновить `CLAUDE.md` (статус Assessment → ДИЗАЙН ГОТОВ)
