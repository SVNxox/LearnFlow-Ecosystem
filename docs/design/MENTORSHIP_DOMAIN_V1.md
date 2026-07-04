

**Дата:** 2026-06-07  
**Статус:** ПРИНЯТО  
**Версия:** 1.0

---





**Решение:** Студент НЕ выбирает ментора.

**Причина:** Выбор ментора студентом почти всегда приводит к проблемам с балансировкой нагрузки:
- Популярные менторы перегружены
- Непопулярные менторы простаивают
- Нужна сложная система ограничения выбора

**Для v1:**
```
Admin создаёт группу:
  Python Backend 
  Mentor: Иван
  Students: User1, User2, User3...
```

**Для v2:** Можно добавить:
```sql
MentorGroup.auto_assign_strategy:
  - round_robin
  - capacity_based
  - manual
```

Но не сейчас.

---



**Решение:** Заложить в дизайн сейчас, даже если не используем в v1.

```sql
accounts_mentorprofile:
  max_students INT DEFAULT 30
  current_students INT DEFAULT 0
```

**Зачем сейчас:** Через год придётся мигрировать данные. Проще добавить поле сразу.

**Использование в v2:** Автоматический capacity-based assignment.

---



**Неправильно:**
```
Module 1: 2026-01-01, 2026-01-03, 2026-01-05
Module 2: 2026-01-08, 2026-01-10, 2026-01-12
```

**Причина:** Реальная жизнь ломает это постоянно:
- Праздники
- Болезнь ментора
- Отключение света
- Экзаменационная неделя

**Правильно:**
```sql
MentorGroup:
  planned_lessons_count INT  -- План: 12 занятий
  started_at TIMESTAMPTZ

OfflineSession:
  group_id UUID
  lesson_id UUID
  scheduled_start TIMESTAMPTZ
  scheduled_end TIMESTAMPTZ
  actual_start TIMESTAMPTZ
  actual_end TIMESTAMPTZ
  status VARCHAR(20)  -- scheduled/completed/cancelled/rescheduled
```

**Пример:**
```
Модуль 1 — План: 12 занятий
Факт:
  Занятие 1 ✓ completed
  Занятие 2 ✓ completed
  Занятие 3 ✓ completed
  Занятие 4 ✗ cancelled
  Занятие 4 (перенос) ✓ completed
  Занятие 5 ✓ completed
```

Это намного реалистичнее.

---



**Решение:** Турникет = подсказка, ментор = источник истины.

**Почему не автоматически через турникет:**

**Проблема 1: Ложные срабатывания**
```
Студент пришёл в центр
  ↓
Сидел в коворкинге
  ↓
На урок НЕ пошёл

Турникет: present ✓
Реальность: absent ✗
```

**Проблема 2: Технические сбои**
```
Face ID не сработал
Турникет сломался
Студент реально сидел весь урок

Турникет: absent ✗
Реальность: present ✓
```

**Для v1 — только ручное:**
```sql
Attendance:
  session_id UUID
  student_id UUID
  status VARCHAR(20)  -- present/absent/late/excused
  marked_by_id UUID   -- Ментор
  marked_at TIMESTAMPTZ
```

**Для v2 — полуавтоматическое:**
1. Ментор открывает урок
2. Система автоматически предлагает (на основе турникета):
   ```
   ☑ Student A (09:02 вход)
   ☑ Student B (09:05 вход)
   ☐ Student C (не зафиксирован)
   ```
3. Ментор быстро исправляет ошибки
4. Нажимает "Save Attendance"

Турникет = подсказка, ментор = финальное решение.

---



**AccessEvent** — факт нахождения в центре:
```sql
access_event:
  student_id UUID
  entered_at TIMESTAMPTZ
  exited_at TIMESTAMPTZ
  source VARCHAR(20)  -- face_id / turnstile / manual
```

**Пример:**
```
09:00 вход
12:00 выход
```

или

```
15:00 вход
15:05 выход (ушёл через 5 минут)
```

**Турникет НЕ знает:**
- На каком уроке студент был
- Пришёл ли он на занятие
- Сидел ли он на уроке

**Использование:** Система показывает ментору при отметке attendance:
```
Студент: Озодбек
Турникет: 09:02 вход, 11:58 выход
Attendance: [не отмечен]
```

Ментор принимает решение.

---



**Важно:** Для offline обучения attendance = lesson completion.

```
Mentor marks attendance
  ↓
AttendanceMarked event
  ↓
UserProgress Domain
  ↓
LessonProgress.completion_source = 'mentor_attendance'
  ↓
LessonProgress.status = 'completed'
```

**НЕ делать:**
```
FaceID → LessonCompleted
```

Это слишком рискованно и будет давать ошибки в прогрессе студентов.

---



**Проблема:**
```
30 студентов × 15 занятий = 450 кликов
```

**Решение:**
```
Session 

☑ User1
☑ User2
☐ User3  (absent)
☑ User4

[Save Attendance]
```

После сохранения:
```python
for student in attended_students:
    dispatch(AttendanceMarked(
        session_id=session.id,
        student_id=student.id,
        status='present',
        ...
    ))
```

---



**Цель:** Ментор видит что нужно проверить.

**Read model или Selector:**
```python
class MentorWorkQueueSelector:
    @staticmethod
    def get_pending_reviews(mentor_id: UUID) -> List[PendingReview]:
        """
        Возвращает список submission/assessment ожидающих проверки.
        Сортировка:
          1. Overdue (deadline passed)
          2. submitted_at ASC (старые выше новых)
        """
```

**UI:**
```
Pending Reviews:

[OVERDUE] Project A — Student X — deadline: 2026-06-05
          Submitted: 2 days ago

[URGENT]  Homework B — Student Y — deadline: today
          Submitted: yesterday

[NORMAL]  Project C — Student Z — deadline: 2026-06-10
          Submitted: 2 hours ago
```

Это намного важнее чатов и комментариев для v1.

---



**Вопрос:** Может ли ментор завершить урок студенту если:
- Студент не сделал домашку
- Не посмотрел видео
- Но присутствовал и ответил устно?

**Ответ:** Да, для offline обучения.

**Решение:**
```sql
LessonProgress.completion_source:
  - student_activity      -- Online: просмотр контента
  - mentor_attendance     -- Offline: посещаемость
  - mentor_override       -- Ментор вручную завершил
  - admin_override        -- Admin вручную завершил
```

**Причина:** Жизнь сложнее правил. Ментор на месте, он знает лучше.

**Пример:**
```
Студент пришёл на урок offline.
Не сделал домашку заранее.
Но выполнил задание в аудитории устно.

Ментор:
  LessonProgress → completed
  completion_source = mentor_override
  override_reason = "Выполнил устно в аудитории"
```

---





**Цель:** Группа студентов с одним ментором для offline обучения.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| mentor_id | UUID FK | → accounts_user |
| course_id | UUID FK | → courses_course |
| name | VARCHAR(255) | "Python Backend 
| planned_lessons_count | SMALLINT | План: 12 занятий |
| max_students | SMALLINT DEFAULT 30 | |
| current_students_count | SMALLINT DEFAULT 0 | F() increment |
| status | VARCHAR(20) | active / completed / archived |
| started_at | TIMESTAMPTZ NULLABLE | |
| completed_at | TIMESTAMPTZ NULLABLE | |
| created_at / updated_at | TIMESTAMPTZ | |

**Constraints:**
- CHECK: `status IN ('active', 'completed', 'archived')`
- CHECK: `current_students_count <= max_students`

**Indexes:**
- `idx_mentorgroup_mentor` ON (mentor_id, status) WHERE status='active'
- `idx_mentorgroup_course` ON (course_id, status)

---



**Цель:** Связь студент ↔ группа (M2M).

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| student_id | UUID FK | → accounts_user |
| group_id | UUID FK | → mentorship_mentorgroup (CASCADE) |
| enrollment_id | UUID FK | → courses_courseenrollment |
| joined_at | TIMESTAMPTZ | |
| left_at | TIMESTAMPTZ NULLABLE | Если студент покинул группу |

**Index:** UNIQUE `(student_id, group_id)`

---



**Цель:** Одно занятие группы.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| group_id | UUID FK | → mentorship_mentorgroup |
| lesson_id | UUID FK NULLABLE | → courses_lesson (SET NULL) |
| module_id | UUID (denorm) | Для группировки |
| title | VARCHAR(255) | "Занятие 5: Django ORM" |
| description | TEXT NULLABLE | |
| scheduled_start | TIMESTAMPTZ | |
| scheduled_end | TIMESTAMPTZ | |
| actual_start | TIMESTAMPTZ NULLABLE | Когда ментор начал занятие |
| actual_end | TIMESTAMPTZ NULLABLE | |
| status | VARCHAR(20) | scheduled / in_progress / completed / cancelled / rescheduled |
| location | VARCHAR(255) NULLABLE | "Room 301" |
| meeting_url | TEXT NULLABLE | Zoom/Google Meet (если hybrid) |
| notes | TEXT NULLABLE | Заметки ментора после занятия |
| created_at / updated_at | TIMESTAMPTZ | |

**Constraints:**
- CHECK: `status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled')`

**Indexes:**
- `idx_session_group_scheduled` ON (group_id, scheduled_start)
- `idx_session_upcoming` ON (scheduled_start) WHERE status='scheduled' AND scheduled_start > NOW()

---



**Цель:** Посещаемость студента на конкретном занятии.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| session_id | UUID FK | → mentorship_offlinesession |
| student_id | UUID FK | → accounts_user |
| status | VARCHAR(20) | present / absent / late / excused |
| marked_by_id | UUID FK | → accounts_user (ментор) |
| marked_at | TIMESTAMPTZ | |
| notes | TEXT NULLABLE | "Пришёл на 15 минут позже" |

**Index:** UNIQUE `(session_id, student_id)`

**Constraints:**
- CHECK: `status IN ('present', 'absent', 'late', 'excused')`

---



**Цель:** Турникет/Face ID события (для аналитики).

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| student_id | UUID FK | → accounts_user |
| entered_at | TIMESTAMPTZ | |
| exited_at | TIMESTAMPTZ NULLABLE | |
| source | VARCHAR(20) | face_id / turnstile / manual |
| device_id | VARCHAR(100) NULLABLE | ID турникета |
| location | VARCHAR(100) NULLABLE | "Main entrance" |
| metadata | JSONB | Доп. данные (фото ID и т.д.) |

**Index:** ON (student_id, entered_at DESC)

---



**Цель:** Очередь работ на проверку для ментора.

**Примечание:** Это может быть материализованное view или обычная таблица, обновляемая через события.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| mentor_id | UUID FK | → accounts_user |
| item_type | VARCHAR(20) | submission / assessment_attempt |
| item_id | UUID | ID submission или attempt |
| student_id | UUID | |
| student_name | VARCHAR(255) (denorm) | |
| title | VARCHAR(255) | "Project: Django Blog API" |
| submitted_at | TIMESTAMPTZ | |
| deadline | TIMESTAMPTZ NULLABLE | |
| is_overdue | BOOLEAN | Вычисляется: deadline < NOW() |
| status | VARCHAR(20) | pending / in_review / completed |
| created_at / updated_at | TIMESTAMPTZ | |

**Indexes:**
- `idx_workreview_mentor_pending` ON (mentor_id, is_overdue DESC, submitted_at ASC) WHERE status='pending'

**Обновление:**
- При `SubmissionSubmitted` → создаётся строка
- При `SubmissionReviewed` → status='completed'
- При `AssessmentNeedsMentorReview` → создаётся строка

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

@dataclass
class OfflineSessionCompleted:
    session_id: UUID
    group_id: UUID
    lesson_id: UUID
    mentor_id: UUID
    attended_students_count: int
    completed_at: datetime

@dataclass
class LessonCompletionOverride:
    enrollment_id: UUID
    lesson_id: UUID
    mentor_id: UUID
    reason: str
    occurred_at: datetime
```



```python

@receiver(submission_submitted)
def handle_submission_submitted(sender, event, **kwargs):
    """
    Добавить в MentorWorkReview очередь работ ментора.
    """
    mentor_id = get_mentor_for_student(event.student_id)
    MentorWorkReview.objects.create(
        mentor_id=mentor_id,
        item_type='submission',
        item_id=event.submission_id,
        student_id=event.student_id,
        submitted_at=event.submitted_at,
        status='pending',
    )


@receiver(assessment_needs_mentor_review)
def handle_assessment_needs_mentor_review(sender, event, **kwargs):
    """
    Добавить assessment attempt в очередь ментора.
    """
    pass
```

---





```
1. Admin создаёт MentorGroup:
   - Python Backend 
   - Mentor: Иван
   - Max students: 25
   - Planned lessons: 12

2. Admin добавляет студентов:
   - StudentMentorGroup (student_id=User1, group_id=...)
   - StudentMentorGroup (student_id=User2, group_id=...)
   - current_students_count инкрементируется (F() expression)

3. Ментор создаёт занятия:
   - OfflineSession 1: 2026-06-10 09:00-12:00 (Module 1, Lesson 1)
   - OfflineSession 2: 2026-06-12 09:00-12:00 (Module 1, Lesson 2)
   - ...
```



```
1. Ментор начинает занятие:
   - OfflineSession.actual_start = NOW()
   - status = 'in_progress'

2. Система показывает список студентов с подсказками турникета:
   ☑ User1 (09:02 вход)
   ☑ User2 (09:05 вход)
   ☐ User3 (не зафиксирован)

3. Ментор корректирует (User3 реально пришёл, но Face ID не сработал):
   ☑ User1
   ☑ User2
   ☑ User3

4. Ментор нажимает "Save Attendance"

5. Для каждого студента:
   - Attendance создаётся (status='present')
   - Событие AttendanceMarked
   - UserProgress слушает → LessonProgress.completed

6. Ментор завершает занятие:
   - OfflineSession.actual_end = NOW()
   - status = 'completed'
   - Событие OfflineSessionCompleted
```



```
Ситуация:
  Студент пришёл на урок.
  Не сделал домашку заранее.
  Но выполнил задание устно в аудитории.

1. Ментор видит LessonProgress:
   - status = 'in_progress'
   - homework_submitted = False

2. Ментор через admin UI:
   - LessonProgressService.override_completion(
       enrollment_id=...,
       lesson_id=...,
       mentor_id=...,
       reason="Выполнил устно в аудитории"
     )

3. LessonProgress обновляется:
   - status = 'completed'
   - completion_source = 'mentor_override'
   - override_by_id = mentor_id
   - override_reason = "..."

4. Событие LessonCompleted → cascade к ModuleProgress
```



```
Ментор открывает страницу "Pending Reviews":

[OVERDUE]
  Project: Django Blog API
  Student: Озодбек
  Deadline: 2026-06-05 (2 days overdue)
  Submitted: 2 days ago
  [Review]

[URGENT]
  Homework: SOLID принципы
  Student: Sardor
  Deadline: today
  Submitted: yesterday
  [Review]

[NORMAL]
  Project: FastAPI TODO
  Student: Javohir
  Deadline: 2026-06-10
  Submitted: 2 hours ago
  [Review]
```

Ментор кликает [Review] → переход на страницу проверки Submission.

---





**Контекст:** Нужна система назначения студентов менторам.

**Отклонённые варианты:**
- Студент выбирает ментора сам — балансировка нагрузки невозможна

**Решение:** Только admin назначает студентов в группы. Один ментор → одна группа → N студентов.

**Причина:** Популярные менторы перегружены, непопулярные простаивают. Нужен контроль.

**Последствия:** В v2 можно добавить авто-распределение (round-robin, capacity-based).

---



**Контекст:** Нужно планировать offline занятия.

**Отклонённые варианты:**
- Привязать Module к датам (Module 1: 2026-01-01, 2026-01-03...) — ломается при переносах

**Решение:** `OfflineSession` — отдельная сущность с `scheduled_start/end`, `status` (scheduled/cancelled/rescheduled).

**Причина:** Реальная жизнь: праздники, болезнь, отключение света. Расписание должно быть гибким.

**Последствия:** Занятия можно отменять, переносить без изменения структуры модуля.

---



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



**Контекст:** Offline обучение не всегда укладывается в правила (контент просмотрен, домашка сдана).

**Решение:** `LessonProgress.completion_source` может быть `mentor_override`.

**Причина:** Ментор на месте, он знает лучше. Студент может выполнить задание устно в аудитории.

**Последствия:** Нужен audit trail: `override_by_id`, `override_reason`, `override_at`.

---



**Контекст:** Ментор должен видеть что нужно проверить.

**Решение:** Read model `MentorWorkReview` — очередь работ с сортировкой (overdue → oldest).

**Причина:** Без этого ментор не знает что проверять первым. Это важнее чатов и комментариев.

**Последствия:** Таблица обновляется через события (SubmissionSubmitted, AssessmentNeedsMentorReview).

---





```python

@receiver(lesson_progress_unlocked)
def handle_lesson_progress_unlocked(sender, event, **kwargs):
    """
    Когда урок разблокирован для offline студента,
    можно автоматически создать OfflineSession (если настроено).
    """
    pass


AttendanceMarked → UserProgress → LessonCompleted
```



```python

SubmissionSubmitted → Mentorship → MentorWorkReview (add to queue)


SubmissionReviewed → Submissions → update status
```



```python

AssessmentNeedsMentorReview → Mentorship → MentorWorkReview (add to queue)


AssessmentResponseGraded → Assessment → update response
```

---



1. ✅ Дизайн Mentorship завершён
2. 🟡 Дизайн Certificates Domain (последний)
3. ⬜ Обновить `docs/DATABASE.md` (все 4 домена)
4. ⬜ Добавить ADR-019..023 в `docs/DECISIONS.md`
5. ⬜ Обновить `docs/CONVERSATION_LOG.md`
6. ⬜ Обновить `CLAUDE.md` и `TASKS.md`
