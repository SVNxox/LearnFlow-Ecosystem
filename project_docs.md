

> This file is read by Claude Code at the start of every session.
> It is the single source of truth for how AI should work with this codebase.
> Keep it updated as the project evolves.

---



**LearnFlow** — образовательная платформа.
- Поддерживает **online** (самостоятельное) и **offline** (групповое с ментором) обучение.
- Один курс работает для обоих форматов. Режим хранится в `CourseEnrollment.delivery_format`.
- Роли: `Student`, `Mentor`, `Staff`, `Admin`.

**Стек:** Django monolith · PostgreSQL · Celery · Python 3.12+  
**Архитектура:** Модульный монолит → будущая экстракция в сервисы.

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
- docs/design/learnflow-learning-domain-v2.html

UserProgress Domain:
- docs/design/learnflow-userprogress-review-v2.html

Application Layer:
- docs/design/learnflow-application-layer.html

API:
- docs/design/LearnFlow API.yaml

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



Перед написанием кода кратко опиши:

1. Какие документы были прочитаны.
2. Какие домены затрагиваются.
3. Как ты понимаешь задачу.
4. План реализации на высоком уровне.

Не приступай к написанию кода, пока не сформировано понимание задачи и затронутых доменов.

---



```
learnflow/
├── apps/
│   ├── accounts/          
│   │   └── models.py      
│   │
│   ├── courses/           
│   │   ├── models.py      
│   │   ├── selectors.py   
│   │   ├── services.py    
│   │   └── events.py      
│   │
│   ├── progress/          
│   │   ├── models.py      
│   │   ├── selectors.py   
│   │   ├── services.py    
│   │   └── events.py      
│   │
│   ├── assessment/        
│   │   ├── models.py      
│   │   ├── selectors.py   
│   │   ├── services.py    
│   │   └── events.py      
│   │
│   ├── submissions/       
│   ├── mentorship/        
│   ├── notifications/     
│   ├── analytics/         
│   └── certificates/      
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   └── urls.py
│
├── docs/                  
└── CLAUDE.md              
```

---





```
Views / API → Selector (READ) → Model (только чтение)
Views / API → Service (WRITE) → Model (только запись)
```

- **Selector** — только чтение. Никаких мутаций. Возвращает queryset или dataclass.
- **Service** — только запись. Все бизнес-правила здесь. Всегда `transaction.atomic()`.
- **Views** — никогда не пишут в модели напрямую. Только через Service.



```python

with transaction.atomic():
    
    transaction.on_commit(lambda: dispatch(StudentEnrolled(...)))
```

- События — Django signals в монолите.
- Payload события самодостаточен (потребитель не должен делать дополнительных запросов).
- Обработчики событий должны быть идемпотентны.



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
| 3 | Реальные FK в монолите: `CourseEnrollment → User`, `Course → User (created_by)` |
| 4 | Завершение урока — терминальное состояние. Нельзя откатить без admin override |
| 5 | Fan-out на N студентов — только async (Celery). Никогда синхронно |
| 6 | `completed_at IS NULL OR status = 'completed'` — на всех progress таблицах |
| 7 | Снапшоты (required_content_count и т.д.) обновляются через события, не пересчитываются |
| 8 | Cross-domain writes (напр. `CourseEnrollmentService.complete_enrollment`) — только через `on_commit` |

---



```
Learning Domain ──emits──► StudentEnrolled ──► UserProgress (initialise)
Learning Domain ──emits──► LessonPublished ──► UserProgress (add row)

UserProgress ──emits──► CourseCompleted ──► Learning (EnrollmentCompleted)
UserProgress ──emits──► ModuleAssessmentUnlocked ──► Notifications

Assessment ──emits──► ModuleAssessmentPassed ──► UserProgress (unlock next module)
Assessment ──emits──► ModuleAssessmentFailed ──► Analytics, Notifications

Submissions ──emits──► HomeworkSubmitted ──► UserProgress (homework gate)
Mentorship  ──emits──► AttendanceMarked  ──► UserProgress (offline completion)
```

**Правило:** Домены НЕ импортируют models друг друга напрямую.  
Читают через Selector (одна база), пишут через events или прямой service вызов (задокументированный).

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

`OWN` = только для своих курсов (`course.created_by == request.user`).

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
- ❌ Не пиши в модели напрямую из views — только через Services
- ❌ Не делай синхронный fan-out на N студентов в event handler
- ❌ Не используй `obj.counter += 1; obj.save()` — только `F()` expressions
- ❌ Не создавай отдельные курсы для online/offline — это один курс
- ❌ Не делай FK из `courses` app на `accounts` без документирования в `docs/DECISIONS.md`
- ❌ Не проектируй новый домен без прочтения `docs/CONTRIBUTING.md`

---



| Домен          | Дизайн | Код | Тесты |
|----------------|--------|-----|-------|
| Identity       | ✓      | ✓   | ?     |
| Learning       | ✓      | 40% | —     |
| UserProgress   | ✓      | —   | —     |
| Assessment     | ✓      | —   | —     |
| Submissions    | ✓      | —   | —     |
| Mentorship     | ✓      | —   | —     |
| Notifications  | —      | —   | —     |
| Analytics      | —      | —   | —     |
| Certificates   | ✓      | —   | —     |

**Phase 1A завершён (2026-06-07/08):** Дизайн Assessment v3, Submissions v1, Mentorship v1, Certificates v1 готовы. 19 новых ADR (ADR-010..028).

**Следующий шаг:** Phase 1B — Реализация кода:
1. Починить Learning Domain (`courses/managers.py` → ImportError)
2. Завершить Learning Domain (selectors, services, events, API)
3. Создать UserProgress Domain с нуля
4. Реализовать Assessment Domain (по новому дизайну v3)
5. Реализовать Submissions Domain
6. Реализовать Mentorship Domain




LearnFlow — образовательная экосистема для профессиональных IT-курсов.  
Платформа объединяет структурированный контент, персональных менторов и систему оценки прогресса.

---




- Студент проходит уроки в удобное время
- Ментор назначен, но не проводит живые сессии
- Студент сам открывает контент, просматривает, сдаёт задания
- Прогресс: `completion_source = student_activity`


- Ментор ведёт группу (`MentorGroup`) по расписанию
- Проводятся живые сессии (`OfflineSession`) по конкретным урокам
- Ментор отмечает посещаемость → прогресс студента обновляется
- Прогресс: `completion_source = mentor_attendance`


**Один курс = один набор контента** для обоих форматов.  
"Python Backend" — один курс, разные способы прохождения.

---



```
Студент записывается на курс  (CourseEnrollment)
          ↓
    Изучает уроки               (LessonProgress: unlocked → in_progress → completed)
          ↓
    Просматривает контент       (LessonContentView: content gate)
          ↓
    Сдаёт домашнее задание     (HomeworkSubmission: homework gate)
          ↓
    Урок завершён              (LessonProgress: completed)
          ↓
    Следующий урок разблокирован (автоматически)
          ↓
    Все уроки модуля завершены
          ↓
    Сдаёт итоговый тест модуля  (ModuleAssessment → AssessmentAttempt)
          ↓
    Тест сдан                  (ModuleProgress: completed)
          ↓
    Следующий модуль разблокирован
          ↓
    Все модули завершены
          ↓
    Курс завершён → Сертификат  (Certificate)
```

---



```
Course (курс)
  └── Module (модуль, тематический блок)
       └── Lesson (урок)
            ├── LessonContent (видео, PDF, текст, код, ссылка...)
            ├── LessonHomework (домашнее задание, опционально)
            ├── LessonPractice (практические задачи, опционально)
            └── LessonQuiz (мини-тест, опционально — НЕ блокирует прогресс)
       └── ModuleAssessment (итоговый тест модуля — блокирует следующий модуль)
```

**Важное разграничение:**
- `LessonQuiz` — учебный инструмент внутри урока. Не влияет на разблокировку.
- `ModuleAssessment` — итоговая оценка модуля. Блокирует переход к следующему.

---




- Записывается на курс
- Просматривает контент, сдаёт задания
- Проходит assessments
- Видит только опубликованный контент


- Ведёт offline группы
- Проверяет задания и text_answer в assessments
- Отмечает посещаемость
- Видит прогресс своих студентов
- **Не создаёт курсы**


- Создаёт и редактирует курсы, модули, уроки
- Публикует контент
- Видит черновики **своих** курсов
- **Не архивирует** — только Admin


- Полный доступ ко всему
- Архивирует и удаляет курсы
- Записывает студентов вручную
- Меняет delivery_format для enrolled студентов

---



| 
|---|---------|
| BR-01 | Нельзя записаться на неопубликованный курс |
| BR-02 | Нельзя записаться в offline если `course.supports_offline = FALSE` |
| BR-03 | Один студент — одна активная запись на курс (одновременно) |
| BR-04 | Урок завершён = терминальное состояние (нельзя отменить без admin) |
| BR-05 | Модуль завершён только после прохождения всех уроков И assessment (если есть) |
| BR-06 | Публикация курса требует ≥1 опубликованного модуля с ≥1 опубликованным уроком |
| BR-07 | Удалить курс нельзя если есть хотя бы один enrolled студент (архивировать) |
| BR-08 | Для offline студентов посещаемость = выполнение контента (content gate bypass) |
| BR-09 | Homework gate применяется всегда (и для online, и для offline студентов) |
| BR-10 | Assessment: pass/fail вычисляется только когда ВСЕ вопросы оценены |

---



| Термин              | Определение |
|---------------------|-------------|
| Course              | Учебный курс. Верхний уровень контентной иерархии |
| Module              | Тематический блок внутри курса |
| Lesson              | Отдельный урок. Единица прогресса |
| LessonContent       | Материал урока (видео, PDF, текст и т.д.) |
| CourseEnrollment    | Запись студента на курс с указанием формата |
| delivery_format     | online или offline — способ прохождения курса |
| LessonProgress      | Состояние прогресса студента по уроку |
| ModuleAssessment    | Итоговый тест по модулю |
| AssessmentAttempt   | Одна попытка прохождения assessment |
| MentorGroup         | Группа студентов с одним ментором (offline) |
| OfflineSession      | Одно занятие группы (offline) |
| completion_source   | Источник завершения: student_activity / mentor_attendance / admin_override |
| content gate        | Условие: все required материалы просмотрены |
| homework gate       | Условие: домашнее задание сдано |
| assessment gate     | Условие: итоговый тест модуля сдан |




**Модульный монолит** — единое Django-приложение с чёткими границами между доменами.

Домены изолированы программно (через паттерны Selector/Service/Events), но развёрнуты как единый процесс на одной PostgreSQL базе. Это позволяет в будущем экстрагировать домены в отдельные сервисы с минимальными изменениями.

---



```
learnflow/
├── apps/
│   ├── accounts/      
│   ├── courses/       
│   ├── progress/      
│   ├── assessment/    
│   ├── submissions/   
│   ├── mentorship/    
│   ├── notifications/ 
│   ├── analytics/     
│   └── certificates/  
├── config/
│   ├── settings/
│   ├── urls.py
│   └── celery.py
└── shared/
    ├── events.py      
    ├── selectors.py   
    └── services.py    
```

---



Каждый домен (`apps/*/`) имеет следующую структуру:

```
apps/courses/
├── models.py       
├── selectors.py    
├── services.py     
├── events.py       
├── tasks.py        
├── api/
│   ├── views.py    
│   ├── serializers.py
│   └── urls.py
├── admin.py
├── apps.py
└── tests/
    ├── test_selectors.py
    ├── test_services.py
    └── test_api.py
```

**Правило слоёв:**
```
Request → View → Service (write) / Selector (read) → Model
                     ↓
               transaction.on_commit → Event dispatch → Handlers
```

---




- **Владеет:** User, UserInfo, Role, UserRole, StudentProfile, MentorProfile, UserSettings
- **Предоставляет:** `settings.AUTH_USER_MODEL`, `UserSelector`, аутентификационные endpoints
- **Не трогать:** этот домен решён — расширяй через Profile, не меняй User


- **Владеет:** Course, Module, Lesson, CourseEnrollment, все Lesson* компоненты, CourseCategory
- **Предоставляет:** каталог курсов, структуру обучения, enrollment
- **Потребляет:** `accounts.User` (FK), ничего из других learning-доменов


- **Владеет:** CourseProgress, ModuleProgress, LessonProgress, LessonContentView
- **Предоставляет:** текущий прогресс студента, completion state, next lesson
- **Потребляет:** события от `courses`, `assessment`, `submissions`, `mentorship`


- **Владеет:** ModuleAssessment, AssessmentItem, AssessmentAttempt, AssessmentResponse
- **Предоставляет:** module-level оценки, grading, pass/fail
- **Потребляет:** ссылку на `courses.Module`, `courses.CourseEnrollment`

---





**1. Прямой FK (только внутри монолита, к Identity):**
```python

user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
```

**2. Мягкая ссылка (UUID без FK) — для будущей экстракции:**
```python

lesson_id = models.UUIDField()  
```

**3. Чтение через Selector (cross-domain reads):**
```python

from apps.progress.selectors import ModuleProgressSelector
progress = ModuleProgressSelector.get_module_progress(enrollment_id, module_id)
```

**4. События (основной механизм cross-domain writes):**
```python

@receiver(student_enrolled)
def handle_student_enrolled(sender, enrollment_id, **kwargs):
    ProgressInitialisationService.initialise_progress(enrollment_id)
```

**5. Прямой service call через on_commit (финальный шаг каскада):**
```python

transaction.on_commit(
    lambda: CourseEnrollmentService.complete_enrollment(enrollment_id)
)
```



- ❌ Прямой импорт model из другого домена (кроме accounts → Identity)
- ❌ Синхронный cross-domain write внутри транзакции другого домена
- ❌ Circular event dependencies (A emits → B handles → B emits → A handles)

---



**Celery** используется для:

| Задача                            | Причина                              |
|-----------------------------------|--------------------------------------|
| Fan-out на N студентов            | O(n) DB writes, timeout при sync     |
| Запуск кода (coding assessment)   | Sandboxed execution, секунды/минуты  |
| Отправка уведомлений              | Внешние API, ненужный sync           |
| Генерация сертификатов            | PDF rendering, медленно              |
| Пересчёт analytics                | Heavy queries, только в фоне         |

**Правило:** если операция обновляет строки пропорционально числу enrolled студентов — это Celery task, не inline код.

---



- **PostgreSQL 16** — единая база для всех доменов
- UUID primary keys везде (`gen_random_uuid()`)
- Soft delete через `deleted_at TIMESTAMPTZ` (не hard delete)
- Все timestamps — `TIMESTAMPTZ` (с таймзоной)
- Именование таблиц: `{app}_{model}` → `courses_course`, `progress_lessonprogress`

Подробная схема: [`docs/DATABASE.md`](./DATABASE.md)


**СУБД:** PostgreSQL 16  
**UUID PK:** `gen_random_uuid()` везде  
**Timestamps:** `TIMESTAMPTZ` (всегда с таймзоной)  
**Soft delete:** `deleted_at TIMESTAMPTZ NULLABLE` (не hard delete)

---



```
Таблица:     {app}_{model}            → courses_course
Индекс:      idx_{table}_{fields}     → idx_course_status
Уникальный:  uq_{table}_{fields}      → uq_enrollment_user_course
Constraint:  chk_{table}_{rule}       → chk_course_status
FK:          {field}_id               → enrollment_id, course_id
```

---




| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| name | VARCHAR(100) | Отображаемое название |
| slug | VARCHAR(100) UNIQUE | URL-safe, неизменяемый |
| parent_id | UUID FK NULLABLE | Self-ref. NULL = корневая категория. Max глубина = 2 |
| description | VARCHAR(500) NULLABLE | |
| icon | VARCHAR(50) NULLABLE | Heroicons id или emoji |
| order | SMALLINT DEFAULT 0 | Порядок в списке |
| is_active | BOOLEAN DEFAULT TRUE | |
| created_at / updated_at | TIMESTAMPTZ | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| title | VARCHAR(255) NOT NULL | |
| slug | VARCHAR(255) UNIQUE NOT NULL | Неизменяем после публикации |
| description | TEXT NULLABLE | Markdown |
| short_description | VARCHAR(500) NULLABLE | Для карточек каталога |
| thumbnail_url | TEXT NULLABLE | S3/CDN URL |
| category_id | UUID FK NULLABLE | → courses_coursecategory, SET NULL |
| status | VARCHAR(20) | draft / published / archived |
| supports_online | BOOLEAN DEFAULT TRUE | Курс поддерживает online |
| supports_offline | BOOLEAN DEFAULT FALSE | Курс поддерживает offline |
| language | VARCHAR(10) DEFAULT 'ru' | BCP-47 |
| estimated_weeks | SMALLINT NULLABLE | |
| is_sequential | BOOLEAN DEFAULT TRUE | Модули проходить по порядку |
| created_by_id | FK → accounts_user | SET NULL при удалении |
| created_at / updated_at | TIMESTAMPTZ | |
| deleted_at | TIMESTAMPTZ NULLABLE | Soft delete |

**Constraints:** `supports_online OR supports_offline = TRUE`, status IN (draft/published/archived)


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| course_id | UUID FK NOT NULL | → courses_course, CASCADE |
| title | VARCHAR(255) NOT NULL | |
| description | TEXT NULLABLE | |
| order | SMALLINT NOT NULL | Уникален внутри курса |
| is_published | BOOLEAN DEFAULT FALSE | |
| estimated_hours | SMALLINT NULLABLE | |
| created_at / updated_at | TIMESTAMPTZ | |
| deleted_at | TIMESTAMPTZ NULLABLE | |

**Index:** UNIQUE `(course_id, order)` WHERE deleted_at IS NULL


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| module_id | UUID FK NOT NULL | → courses_module, CASCADE |
| title | VARCHAR(255) NOT NULL | |
| description | TEXT NULLABLE | |
| order | SMALLINT NOT NULL | Уникален внутри модуля |
| is_published | BOOLEAN DEFAULT FALSE | |
| is_free_preview | BOOLEAN DEFAULT FALSE | Доступен без записи |
| estimated_minutes | SMALLINT NULLABLE | |
| created_at / updated_at | TIMESTAMPTZ | |
| deleted_at | TIMESTAMPTZ NULLABLE | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| lesson_id | UUID FK NOT NULL | → courses_lesson, CASCADE |
| type | VARCHAR(20) | video/pdf/slides/text/link/recording/code |
| title | VARCHAR(255) NOT NULL | |
| description | TEXT NULLABLE | |
| url | TEXT NULLABLE | Для video/pdf/slides/link/recording |
| body | TEXT NULLABLE | Для text/code |
| order | SMALLINT NOT NULL | |
| duration_seconds | INT NULLABLE | Только для video/recording |
| file_size_bytes | BIGINT NULLABLE | |
| is_required | BOOLEAN DEFAULT TRUE | Учитывается в content gate |
| is_downloadable | BOOLEAN DEFAULT FALSE | |
| metadata | JSONB DEFAULT '{}' | Доп. данные по типу |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| lesson_id | UUID FK UNIQUE | 1:1 с уроком |
| title | VARCHAR(255) NOT NULL | |
| description | TEXT NOT NULL | |
| max_score | SMALLINT DEFAULT 100 | |
| deadline_offset_days | SMALLINT NULLABLE | Дней от enrolledAt |
| submission_type | VARCHAR(20) | file/text/link/code |
| allowed_file_types | VARCHAR(200) NULLABLE | .pdf,.docx и т.д. |
| created_at / updated_at | TIMESTAMPTZ | |


| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| user_id | FK → accounts_user | PROTECT |
| course_id | FK → courses_course | RESTRICT (не удалить с active enrollments) |
| status | VARCHAR(20) | active / completed / dropped |
| delivery_format | VARCHAR(10) | online / offline |
| enrolled_at | TIMESTAMPTZ NOT NULL | |
| completed_at | TIMESTAMPTZ NULLABLE | |
| dropped_at | TIMESTAMPTZ NULLABLE | |
| enrolled_by_id | FK NULLABLE → accounts_user | SET NULL |

**Index:** UNIQUE `(user_id, course_id)`

---




| Поле | Тип | Описание |
|------|-----|----------|
| enrollment_id | FK UNIQUE | 1:1 с enrollment |
| course_id | UUID (denorm) | Из enrollment |
| user_id | UUID (denorm) | Из enrollment |
| delivery_format | VARCHAR(10) | Snapshot из enrollment |
| is_sequential | BOOLEAN | Snapshot из course |
| status | VARCHAR(20) | not_started / in_progress / completed |
| total_modules_count | SMALLINT | Snapshot |
| completed_modules_count | SMALLINT | Инкрементируется через F() |
| cached_percentage | SMALLINT DEFAULT 0 | Лениво обновляется |
| started_at / completed_at / last_activity_at | TIMESTAMPTZ NULLABLE | |


| Поле | Тип | Описание |
|------|-----|----------|
| enrollment_id | FK | |
| module_id | FK → courses_module | |
| course_id | UUID (denorm) | |
| module_order | SMALLINT | Snapshot |
| status | VARCHAR(25) | locked/unlocked/in_progress/assessment_pending/completed |
| total_lessons_count | SMALLINT | Snapshot |
| completed_lessons_count | SMALLINT | F() increment |
| assessment_required | BOOLEAN | Snapshot из Assessment Domain |
| assessment_passed | BOOLEAN DEFAULT FALSE | |
| assessment_passed_at | TIMESTAMPTZ NULLABLE | |
| is_stale | BOOLEAN DEFAULT FALSE | Модуль удалён |
| unlocked_at / completed_at / last_activity_at | TIMESTAMPTZ NULLABLE | |

### progress_lessonprogress
| Поле | Тип | Описание |
|------|-----|----------|
| enrollment_id | FK | |
| lesson_id | FK → courses_lesson | |
| module_id | UUID (denorm) | |
| course_id | UUID (denorm) | |
| lesson_order | SMALLINT | Snapshot |
| module_order | SMALLINT | Snapshot — критично для get_next_action |
| status | VARCHAR(20) | locked/unlocked/in_progress/completed |
| completion_source | VARCHAR(30) NULLABLE | student_activity/mentor_attendance/admin_override |
| required_content_count | SMALLINT DEFAULT 0 | Snapshot. WHERE status!='completed' при обновлении |
| viewed_required_count | SMALLINT DEFAULT 0 | F() increment only |
| homework_required | BOOLEAN DEFAULT FALSE | Snapshot |
| homework_submitted | BOOLEAN DEFAULT FALSE | |
| homework_submitted_at | TIMESTAMPTZ NULLABLE | |
| is_stale | BOOLEAN DEFAULT FALSE | Урок удалён |
| is_active | BOOLEAN DEFAULT TRUE | FALSE при drop enrollment |
| override_by_id | UUID NULLABLE | Аудит admin override |
| override_reason | TEXT NULLABLE | |
| unlocked_at / started_at / completed_at | TIMESTAMPTZ NULLABLE | |

**Critical index:** `(enrollment_id, module_order, lesson_order)` WHERE status IN ('unlocked','in_progress') AND is_stale=FALSE AND is_active=TRUE

### progress_lessoncontentview
| Поле | Тип | Описание |
|------|-----|----------|
| enrollment_id | FK → courses_courseenrollment | CASCADE |
| content_id | UUID (soft ref, NO FK) | Content может быть удалён |
| lesson_progress_id | FK → progress_lessonprogress | CASCADE |
| is_required | BOOLEAN | Snapshot при просмотре |
| first_viewed_at / last_viewed_at | TIMESTAMPTZ | |
| view_count | SMALLINT DEFAULT 1 | |
| last_position_seconds | INT NULLABLE | Для video resume |
| total_duration_seconds | INT NULLABLE | Snapshot для watch threshold |

**Index:** UNIQUE `(enrollment_id, content_id)`

---

## Assessment Domain (`assessment` app) — v3

**Изменения:** Assessment = контейнер без поля type. Состав определяется через items. Добавлен type=interview. Mentor override с историей изменений.

### assessment_moduleassessment
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| module_id | UUID FK → courses_module | UNIQUE — один assessment на модуль |
| title | VARCHAR(255) NOT NULL | |
| instructions | TEXT NULLABLE | |
| passing_percentage | DECIMAL(5,2) | 0–100. Процент для зачёта (было passing_score) |
| max_attempts | SMALLINT NULLABLE | NULL = unlimited |
| time_limit_minutes | SMALLINT NULLABLE | NULL = без ограничений |
| shuffle_items | BOOLEAN DEFAULT FALSE | |
| is_published | BOOLEAN DEFAULT FALSE | |
| created_by_id | FK → accounts_user | |
| created_at / updated_at | TIMESTAMPTZ | |

### assessment_assessmentitem
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| assessment_id | FK | |
| type | VARCHAR(20) | single_choice/multiple_choice/text_answer/coding/project/interview |
| order | SMALLINT | |
| title | TEXT NOT NULL | Текст вопроса/задания |
| description | TEXT NULLABLE | Дополнительный контекст |
| max_points | DECIMAL(6,2) | |
| partial_credit_strategy | VARCHAR(20) DEFAULT 'all_or_nothing' | all_or_nothing / proportional |
| explanation | TEXT NULLABLE | Показывается после оценки |
| mentor_review_required | BOOLEAN DEFAULT FALSE | TRUE для text_answer/project/interview |
| coding_language | VARCHAR(30) NULLABLE | Только для type=coding |
| starter_code | TEXT NULLABLE | Только для type=coding |
| sample_answer | TEXT NULLABLE | Для ментора (text_answer) |
| min_word_count | SMALLINT NULLABLE | Только для type=text_answer |
| submission_requirements | TEXT NULLABLE | Только для type=project |

### assessment_assessmentoption
| Поле | Тип | Описание |
|------|-----|----------|
| item_id | FK → assessment_assessmentitem | |
| text | TEXT NOT NULL | |
| is_correct | BOOLEAN NOT NULL | |
| order | SMALLINT | |
| explanation | TEXT NULLABLE | Per-option объяснение |

### assessment_codingtestcase
| Поле | Тип | Описание |
|------|-----|----------|
| item_id | FK → assessment_assessmentitem | |
| input | TEXT NOT NULL | stdin или аргументы |
| expected_output | TEXT NOT NULL | |
| points | DECIMAL(5,2) NULLABLE | NULL = equal share of item's max_points |
| time_limit_ms | INT DEFAULT 2000 | |
| memory_limit_mb | INT DEFAULT 128 | |
| is_hidden | BOOLEAN DEFAULT FALSE | Скрыт от студента |
| is_sample | BOOLEAN DEFAULT FALSE | Показывается в условии |
| order | SMALLINT | |

### assessment_assessmentattempt
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
| expires_at | TIMESTAMPTZ NULLABLE | |
| max_score | DECIMAL(8,2) | Snapshot при создании |
| final_score | DECIMAL(8,2) NULLABLE | Сумма final_points из responses |
| percentage | DECIMAL(5,2) NULLABLE | final_score / max_score * 100 |
| passed | BOOLEAN NULLABLE | percentage >= passing_percentage |
| mentor_note | TEXT NULLABLE | Общий комментарий ментора |

**Index:** UNIQUE `(enrollment_id, assessment_id, attempt_number)`

### assessment_assessmentresponse
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
| reviewed_by_id | UUID FK NULLABLE | → accounts_user (ментор) |
| reviewed_at | TIMESTAMPTZ NULLABLE | |
| review_comment | TEXT NULLABLE | Почему изменил балл |

**Index:** UNIQUE `(attempt_id, item_id)`

### assessment_codingtestcaseresult
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| response_id | FK → assessment_assessmentresponse | |
| test_case_id | FK → assessment_codingtestcase | |
| passed | BOOLEAN NOT NULL | |
| actual_output | TEXT NULLABLE | |
| execution_time_ms | INT NULLABLE | |
| memory_used_mb | INT NULLABLE | |
| error_message | TEXT NULLABLE | |
| points_earned | DECIMAL(5,2) | |

### assessment_assessmentreviewlog
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

---

## Submissions Domain (`submissions` app) — v1

**Концепция:** Assignment (описание задания) отделено от Submission (попытка выполнения). Версионирование через SubmissionRevision.

### submissions_assignment
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| lesson_id | UUID FK NULLABLE | → courses_lesson (SET NULL) |
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
| created_by_id | UUID FK → accounts_user | |
| created_at / updated_at | TIMESTAMPTZ | |

**Constraints:** CHECK `type IN ('theory', 'coding', 'project')`, CHECK `lesson_id IS NOT NULL OR assessment_item_id IS NOT NULL`

### submissions_submission
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| assignment_id | UUID FK → submissions_assignment | |
| enrollment_id | UUID FK → courses_courseenrollment | |
| student_id | UUID (denorm) | |
| status | VARCHAR(20) | draft/submitted/under_review/changes_requested/approved/rejected |
| current_revision_number | SMALLINT DEFAULT 0 | |
| final_score | DECIMAL(6,2) NULLABLE | Финальная оценка |
| created_at | TIMESTAMPTZ | |
| first_submitted_at | TIMESTAMPTZ NULLABLE | |
| last_submitted_at | TIMESTAMPTZ NULLABLE | |
| reviewed_at | TIMESTAMPTZ NULLABLE | |
| deadline | TIMESTAMPTZ NULLABLE | |

**Index:** UNIQUE `(enrollment_id, assignment_id)`

### submissions_submissionrevision
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| submission_id | UUID FK → submissions_submission (CASCADE) | |
| revision_number | SMALLINT | 1, 2, 3... |
| submission_type | VARCHAR(20) | github_repository/file_upload/text_answer/external_link |
| payload | JSONB | Зависит от submission_type |
| notes | TEXT NULLABLE | Комментарий студента |
| submitted_at | TIMESTAMPTZ | |

**Index:** UNIQUE `(submission_id, revision_number)`

### submissions_submissionfile
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| revision_id | UUID FK → submissions_submissionrevision (CASCADE) | |
| file_name | VARCHAR(255) | |
| file_size_bytes | BIGINT | |
| mime_type | VARCHAR(100) | |
| storage_path | TEXT | S3 path |
| scan_status | VARCHAR(20) | pending/running/passed/failed |
| scan_result | JSONB NULLABLE | Результат ClamAV |
| scanned_at | TIMESTAMPTZ NULLABLE | |
| uploaded_at | TIMESTAMPTZ | |

**Constraints:** CHECK `scan_status IN ('pending', 'running', 'passed', 'failed')`

### submissions_autocheck
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| revision_id | UUID FK → submissions_submissionrevision | |
| check_type | VARCHAR(30) | tests/linting/coverage/docker_build |
| status | VARCHAR(20) | pending/running/passed/failed/error |
| score | DECIMAL(6,2) NULLABLE | |
| report | JSONB | Детальный отчёт |
| started_at | TIMESTAMPTZ NULLABLE | |
| completed_at | TIMESTAMPTZ NULLABLE | |

### submissions_submissionreview
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| submission_id | UUID FK → submissions_submission | |
| revision_id | UUID FK → submissions_submissionrevision | |
| mentor_id | UUID FK → accounts_user | |
| score | DECIMAL(6,2) | |
| max_score | DECIMAL(6,2) | Snapshot |
| feedback | TEXT | |
| status | VARCHAR(20) | changes_requested/approved/rejected |
| reviewed_at | TIMESTAMPTZ | |

**Index:** UNIQUE `(submission_id, revision_id)`

---

## Mentorship Domain (`mentorship` app) — v1

**Концепция:** Группы студентов с ментором. Offline занятия с гибким расписанием. Attendance отмечается ментором вручную.

### mentorship_mentorgroup
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| mentor_id | UUID FK → accounts_user | |
| course_id | UUID FK → courses_course | |
| name | VARCHAR(255) | "Python Backend #12" |
| planned_lessons_count | SMALLINT | План: 12 занятий |
| max_students | SMALLINT DEFAULT 30 | |
| current_students_count | SMALLINT DEFAULT 0 | F() increment |
| status | VARCHAR(20) | active/completed/archived |
| started_at | TIMESTAMPTZ NULLABLE | |
| completed_at | TIMESTAMPTZ NULLABLE | |
| created_at / updated_at | TIMESTAMPTZ | |

**Constraints:** CHECK `status IN ('active', 'completed', 'archived')`, CHECK `current_students_count <= max_students`

### mentorship_studentmentorgroup
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| student_id | UUID FK → accounts_user | |
| group_id | UUID FK → mentorship_mentorgroup (CASCADE) | |
| enrollment_id | UUID FK → courses_courseenrollment | |
| joined_at | TIMESTAMPTZ | |
| left_at | TIMESTAMPTZ NULLABLE | |

**Index:** UNIQUE `(student_id, group_id)`

### mentorship_offlinesession
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| group_id | UUID FK → mentorship_mentorgroup | |
| lesson_id | UUID FK NULLABLE → courses_lesson (SET NULL) | |
| module_id | UUID (denorm) | |
| title | VARCHAR(255) | "Занятие 5: Django ORM" |
| description | TEXT NULLABLE | |
| scheduled_start | TIMESTAMPTZ | |
| scheduled_end | TIMESTAMPTZ | |
| actual_start | TIMESTAMPTZ NULLABLE | |
| actual_end | TIMESTAMPTZ NULLABLE | |
| status | VARCHAR(20) | scheduled/in_progress/completed/cancelled/rescheduled |
| location | VARCHAR(255) NULLABLE | "Room 301" |
| meeting_url | TEXT NULLABLE | Zoom/Google Meet |
| notes | TEXT NULLABLE | Заметки ментора |
| created_at / updated_at | TIMESTAMPTZ | |

**Constraints:** CHECK `status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled')`

### mentorship_attendance
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| session_id | UUID FK → mentorship_offlinesession | |
| student_id | UUID FK → accounts_user | |
| status | VARCHAR(20) | present/absent/late/excused |
| marked_by_id | UUID FK → accounts_user | Ментор |
| marked_at | TIMESTAMPTZ | |
| notes | TEXT NULLABLE | |

**Index:** UNIQUE `(session_id, student_id)`  
**Constraints:** CHECK `status IN ('present', 'absent', 'late', 'excused')`

### mentorship_accessevent
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| student_id | UUID FK → accounts_user | |
| entered_at | TIMESTAMPTZ | |
| exited_at | TIMESTAMPTZ NULLABLE | |
| source | VARCHAR(20) | face_id/turnstile/manual |
| device_id | VARCHAR(100) NULLABLE | |
| location | VARCHAR(100) NULLABLE | |
| metadata | JSONB | |

### mentorship_mentorworkreview
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| mentor_id | UUID FK → accounts_user | |
| item_type | VARCHAR(20) | submission/assessment_attempt |
| item_id | UUID | ID submission или attempt |
| student_id | UUID | |
| student_name | VARCHAR(255) (denorm) | |
| title | VARCHAR(255) | |
| submitted_at | TIMESTAMPTZ | |
| deadline | TIMESTAMPTZ NULLABLE | |
| is_overdue | BOOLEAN | |
| status | VARCHAR(20) | pending/in_review/completed |
| created_at / updated_at | TIMESTAMPTZ | |

---

## Certificates Domain (`certificates` app) — v1

**Концепция:** Сертификат = snapshot данных на момент выдачи. PDF генерируется async. Публичная верификация через verification_code.

### certificates_certificatetemplate
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| name | VARCHAR(255) | "Backend Certificate Template" |
| description | TEXT NULLABLE | |
| background_image | TEXT | S3 URL |
| pdf_template | TEXT | Path к Jinja2 template |
| font_config | JSONB | Шрифты, размеры, цвета |
| layout_config | JSONB | Позиции элементов |
| is_active | BOOLEAN DEFAULT TRUE | |
| created_by_id | UUID FK → accounts_user | |
| created_at / updated_at | TIMESTAMPTZ | |

### certificates_certificate
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| user_id | UUID FK → accounts_user (PROTECT) | |
| enrollment_id | UUID FK → courses_courseenrollment | |
| course_id | UUID (denorm) | |
| template_id | UUID FK → certificates_certificatetemplate | |
| certificate_number | VARCHAR(50) UNIQUE | "LF-2026-8AF3D2" |
| verification_code | VARCHAR(50) UNIQUE | То же что certificate_number |
| student_full_name_snapshot | VARCHAR(255) | Snapshot |
| course_name_snapshot | VARCHAR(255) | Snapshot |
| course_description_snapshot | TEXT NULLABLE | Snapshot |
| final_score | DECIMAL(6,2) NULLABLE | |
| completion_date | DATE | |
| issued_at | TIMESTAMPTZ | |
| pdf_url | TEXT NULLABLE | S3 URL |
| pdf_generated_at | TIMESTAMPTZ NULLABLE | |
| status | VARCHAR(20) | pending/issued/revoked |
| revoked_at | TIMESTAMPTZ NULLABLE | |
| revoked_by_id | UUID FK NULLABLE → accounts_user | |
| revoked_reason | TEXT NULLABLE | |
| metadata | JSONB | |

**Constraints:** CHECK `status IN ('pending', 'issued', 'revoked')`

### certificates_certificatereissuerequest
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| certificate_id | UUID FK → certificates_certificate | |
| reason | TEXT | |
| requested_by_id | UUID FK → accounts_user | |
| requested_at | TIMESTAMPTZ | |
| status | VARCHAR(20) | pending/approved/rejected |
| reviewed_by_id | UUID FK NULLABLE → accounts_user | |
| reviewed_at | TIMESTAMPTZ NULLABLE | |
| new_certificate_id | UUID FK NULLABLE → certificates_certificate | |

**Constraints:** CHECK `status IN ('pending', 'approved', 'rejected')`

### certificates_certificateauditlog
| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| certificate_id | UUID FK → certificates_certificate | |
| action | VARCHAR(50) | created/issued/revoked/reissued/downloaded |
| actor_id | UUID FK NULLABLE → accounts_user | |
| details | JSONB | |
| ip_address | INET NULLABLE | |
| created_at | TIMESTAMPTZ | |

---

## Принципы целостности данных

1. **UUID везде** — никаких serial/integer PK
2. **Soft delete** — `deleted_at` вместо DELETE для Course, Module, Lesson
3. **Snapshot denormalization** — progress domain хранит снапшоты order/count из Learning
4. **NO DB FK через домены** — кроме `→ accounts_user` и внутри домена
5. **F() expressions** — все инкременты счётчиков
6. **Partial indexes** — `WHERE deleted_at IS NULL`, `WHERE status != 'completed'`
# API Documentation

## Соглашения

| Параметр | Значение |
|----------|----------|
| Base URL | `/api/v1/` |
| Auth | `Authorization: Bearer <JWT>` |
| Format | JSON |
| Pagination | `{ count, next, previous, results }` |
| Errors | `{ error, code, detail }` |
| IDs | UUID везде |
| Timestamps | ISO 8601 с таймзоной |

---

## Аутентификация

```
POST /api/auth/token/          # Получить JWT (login)
POST /api/auth/token/refresh/  # Обновить access token
POST /api/auth/register/       # Регистрация
POST /api/auth/logout/         # Инвалидировать refresh token
```

---

## Learning Domain

### Catalog (публичный)
```
GET  /api/v1/learning/courses/              # Список опубликованных курсов
GET  /api/v1/learning/courses/{slug}/       # Детали курса
GET  /api/v1/learning/categories/           # Все категории (дерево)
```

### Course Management (Staff/Admin)
```
POST   /api/v1/learning/courses/                    # Создать курс
PATCH  /api/v1/learning/courses/{id}/               # Редактировать
POST   /api/v1/learning/courses/{id}/publish/       # Опубликовать
POST   /api/v1/learning/courses/{id}/archive/       # Архивировать

POST   /api/v1/learning/courses/{id}/modules/       # Создать модуль
PATCH  /api/v1/learning/modules/{id}/               # Редактировать модуль
POST   /api/v1/learning/courses/{id}/modules/reorder/  # Изменить порядок

POST   /api/v1/learning/modules/{id}/lessons/       # Создать урок
PATCH  /api/v1/learning/lessons/{id}/               # Редактировать урок
POST   /api/v1/learning/modules/{id}/lessons/reorder/  # Изменить порядок

POST   /api/v1/learning/lessons/{id}/content/       # Добавить контент
PATCH  /api/v1/learning/content/{id}/               # Редактировать контент
DELETE /api/v1/learning/content/{id}/               # Удалить контент
POST   /api/v1/learning/lessons/{id}/content/reorder/

POST   /api/v1/learning/lessons/{id}/homework/      # Создать/обновить ДЗ
DELETE /api/v1/learning/lessons/{id}/homework/      # Удалить ДЗ

POST   /api/v1/learning/lessons/{id}/quiz/          # Создать quiz
POST   /api/v1/learning/quizzes/{id}/questions/     # Добавить вопрос
```

### Lesson View (Student — enrolled)
```
GET  /api/v1/learning/modules/{id}/lessons/{id}/    # Контент урока (без ответов)
```

### Enrollment
```
POST /api/v1/learning/enrollments/                  # Записаться на курс
GET  /api/v1/learning/enrollments/me/               # Мои записи
POST /api/v1/learning/enrollments/{id}/drop/        # Отписаться
GET  /api/v1/learning/courses/{id}/enrollments/     # Все студенты (Staff)
```

---

## UserProgress Domain

```
GET  /api/v1/progress/me/                           # Dashboard: все курсы + %
GET  /api/v1/progress/courses/{course_id}/          # Полный прогресс по курсу
GET  /api/v1/progress/courses/{course_id}/next/     # Следующее действие (next_action)
GET  /api/v1/progress/lessons/{lesson_id}/          # Прогресс по уроку + viewed content

POST /api/v1/progress/lessons/{id}/content/{id}/view/  # Отметить контент просмотренным
                                                        # Body: { position_seconds? }
                                                        # Response: { lesson_just_completed }

POST /api/v1/progress/enrollments/{id}/lessons/{id}/complete/  # Admin override
GET  /api/v1/progress/courses/{id}/students/        # Прогресс всех студентов (Staff/Mentor)
GET  /api/v1/progress/students/{id}/courses/{id}/   # Прогресс студента (Staff/Mentor)
```

### GET /api/v1/progress/courses/{course_id}/next/ — Response

```json
{
  "type": "lesson",
  "lesson_id": "uuid",
  "lesson_title": "Введение в Django ORM",
  "module_title": "Модуль 2: База данных"
}
```

```json
{
  "type": "take_module_assessment",
  "module_id": "uuid",
  "module_title": "Модуль 1: Python основы",
  "assessment_title": "Итоговый тест"
}
```

```json
{ "type": "course_complete" }
```

---

## Assessment Domain

### Student
```
GET  /api/v1/assessments/modules/{module_id}/           # Описание assessment
POST /api/v1/assessments/modules/{module_id}/attempts/  # Начать попытку
GET  /api/v1/assessments/attempts/{id}/                 # Текущее состояние
PATCH /api/v1/assessments/attempts/{id}/responses/{item_id}/  # Сохранить ответ (auto-save)
POST /api/v1/assessments/attempts/{id}/submit/          # Сдать
GET  /api/v1/assessments/attempts/{id}/result/          # Результат (после grading)
```

### Mentor (grading)
```
GET  /api/v1/assessments/pending-review/                # Очередь на проверку
GET  /api/v1/assessments/attempts/{id}/grade/           # Страница проверки
POST /api/v1/assessments/attempts/{id}/responses/{item_id}/grade/  # Оценить пункт
POST /api/v1/assessments/attempts/{id}/complete-grading/            # Завершить проверку
```

### Staff/Admin
```
POST  /api/v1/assessments/modules/{id}/                 # Создать assessment
PATCH /api/v1/assessments/{id}/                         # Редактировать
POST  /api/v1/assessments/{id}/items/                   # Добавить вопрос
POST  /api/v1/assessments/items/{id}/options/           # Добавить вариант ответа
POST  /api/v1/assessments/items/{id}/test-cases/        # Добавить тест-кейс
POST  /api/v1/assessments/{id}/publish/                 # Опубликовать
```

---

## Общие коды ошибок

| Code | HTTP | Описание |
|------|------|----------|
| `not_enrolled` | 403 | Студент не записан на курс |
| `lesson_locked` | 403 | Урок заблокирован |
| `course_not_published` | 400 | Курс ещё не опубликован |
| `duplicate_enrollment` | 409 | Уже записан на этот курс |
| `max_attempts_reached` | 400 | Превышено число попыток |
| `attempt_expired` | 400 | Время истекло |
| `publish_not_ready` | 400 | Курс не готов к публикации |
| `quiz_exists` | 409 | Уже есть quiz для этого урока |
| `has_active_enrollments` | 400 | Нельзя выполнить действие |
# Security

## Аутентификация

**JWT** через `djangorestframework-simplejwt`.

```
Access token:  15 минут
Refresh token: 7 дней (ротация при каждом использовании)
```

Refresh tokens хранятся в `accounts_refreshtoken` (БД), могут быть отозваны.

## Авторизация

**Role-based** через `accounts_userrole`. Роли: Student, Mentor, Staff, Admin.

Каждый View проверяет роль через permission class:

```python
class IsMentorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.roles.filter(
            name__in=['mentor', 'staff', 'admin']
        ).exists()
```

**OWN permission** — Staff видит только свои курсы (`course.created_by == request.user`).

## Данные студентов

- Прогресс студента доступен только самому студенту, его ментору и Staff/Admin
- Email не раскрывается через API (только для auth)
- `user_id` в events — UUID, не email

## Coding Execution

Студенческий код запускается в **изолированном sandbox**:
- Отдельный Docker контейнер
- Ограничения: CPU, RAM, время, сеть (отключена)
- Нет доступа к файловой системе хоста
- Нет доступа к БД или другим сервисам

Код студента **никогда** не выполняется в основном Django процессе.

## GDPR / Данные

- Soft delete везде — данные не удаляются физически
- При запросе на удаление аккаунта: анонимизация (email → deleted@..., имя → Deleted User)
- `progress_courseprogress.user_id` — денормализованный FK, каскадно зануляется

## Secrets

```
SECRET_KEY         → Environment variable (никогда в коде)
DATABASE_URL       → Environment variable
CELERY_BROKER_URL  → Environment variable
JWT_SECRET         → Environment variable
```

`.env` файл не коммитится в git (добавлен в `.gitignore`).

## Что НЕ делать

- ❌ Не логировать пароли, токены, персональные данные
- ❌ Не возвращать `is_correct` для quiz options студенту до завершения
- ❌ Не раскрывать `sample_answer` ментора студенту
- ❌ Не раскрывать hidden test cases студенту
- ❌ Не выполнять код студента вне sandbox
# Deployment

## Переменные окружения

```bash
# Django
DJANGO_SECRET_KEY=
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=learnflow.uz,www.learnflow.uz

# Database
DATABASE_URL=postgresql://user:password@host:5432/learnflow

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Storage (S3-compatible)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=

# Email
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Sentry
SENTRY_DSN=
```

## Docker Compose (разработка)

```yaml
services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes: [.:/app]
    env_file: .env
    depends_on: [db, redis]

  celery:
    build: .
    command: celery -A config worker -l info -Q default,fan_out,coding
    env_file: .env
    depends_on: [db, redis]

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: learnflow
      POSTGRES_USER: learnflow
      POSTGRES_PASSWORD: password

  redis:
    image: redis:7-alpine
```

## Celery Queues

| Очередь | Назначение | Workers |
|---------|------------|---------|
| `default` | Уведомления, email | 2 |
| `fan_out` | Fan-out на N студентов | 4 |
| `coding` | Execution sandbox | 8 (изолированные) |

## Миграции

```bash
# Всегда перед деплоем
python manage.py migrate --check  # проверить без выполнения
python manage.py migrate          # применить
```

Миграции применяются атомарно. Откат — отдельная миграция, не `migrate --fake`.

## Мониторинг

- **Sentry** — ошибки Django и Celery
- **Flower** — мониторинг Celery tasks (`celery -A config flower`)
- **pgBadger** или **pg_stat_statements** — медленные запросы PostgreSQL
# Contributing Guide

## Как добавить новый домен

### Шаг 1: Задокументируй дизайн

Перед написанием кода — задокументируй в `docs/`:
1. Обнови `docs/DATABASE.md` — добавь таблицы нового домена
2. Добавь ADR в `docs/DECISIONS.md` для каждого нетривиального решения
3. Обнови `docs/ARCHITECTURE.md` — секция Boundaries
4. Обнови `CLAUDE.md` — карта доменов (статус → СПРОЕКТИРОВАН)

### Шаг 2: Создай структуру

```bash
mkdir -p apps/{domain_name}/api
mkdir -p apps/{domain_name}/tests
touch apps/{domain_name}/{__init__,apps,models,selectors,services,events,tasks,admin}.py
touch apps/{domain_name}/api/{__init__,views,serializers,urls}.py
touch apps/{domain_name}/tests/{__init__,test_selectors,test_services,test_api}.py
```

### Шаг 3: Реализуй в порядке

```
models.py → migrations → selectors.py → services.py → events.py → api/ → tests/
```

---

## Паттерн: Selector (READ)

```python
# apps/learning/selectors.py
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

## Паттерн: Service (WRITE)

```python
# apps/learning/services.py
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

            # Бизнес-правило BR-06
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

## Паттерн: Domain Event

```python
# apps/learning/events.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from django.dispatch import Signal

# Сигнал
course_published = Signal()

# Payload — dataclass
@dataclass(frozen=True)
class CoursePublished:
    course_id: UUID
    title: str
    slug: str
    published_by_id: UUID
    occurred_at: datetime = field(default_factory=datetime.utcnow)

def dispatch(event: CoursePublished):
    course_published.send(sender=CoursePublished, event=event)

# В handlers.py другого домена:
@receiver(course_published)
def handle_course_published(sender, event: CoursePublished, **kwargs):
    # Идемпотентно! Если вызвать дважды — результат тот же
    SearchIndexService.index_course(event.course_id)
```

---

## Паттерн: Async Fan-out (Celery)

```python
# apps/learning/tasks.py
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
        status__ne='completed',  # ADR-005: не трогать completed
        is_active=True,
    ).only('id', 'viewed_required_count')

    # Обрабатываем батчами
    batch = list(islice(qs.iterator(), BATCH_SIZE))
    while batch:
        ids = [lp.id for lp in batch]
        LessonProgress.objects.filter(id__in=ids).update(
            required_content_count=F('required_content_count') - 1
        )
        # Проверяем completion для затронутых строк
        for lp in batch:
            _check_lesson_completion_safe(lp.enrollment_id, lp.lesson_id)
        batch = list(islice(qs.iterator(), BATCH_SIZE))
```

---

## Паттерн: Completion Cascade с блокировками

```python
# apps/progress/services.py — шаблон для cascade методов
def _check_module_completion(enrollment_id: UUID, module_id: UUID):
    with transaction.atomic():
        # ОБЯЗАТЕЛЬНО: select_for_update (ADR-007)
        mp = ModuleProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id,
            module_id=module_id,
        )

        if mp.status == 'completed':
            return  # идемпотентная защита

        # Атомарный инкремент (ADR-005)
        ModuleProgress.objects.filter(pk=mp.pk).update(
            completed_lessons_count=F('completed_lessons_count') + 1
        )
        mp.refresh_from_db()

        if mp.completed_lessons_count < mp.total_lessons_count:
            return

        # ... далее логика completion
```

---

## Тестирование

### Структура тестов

```python
# tests/test_services.py
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

### Что тестировать обязательно

- ✅ Каждое бизнес-правило (BR-*) — негативный тест
- ✅ Идемпотентность event handlers
- ✅ Каскад completion (lesson → module → course)
- ✅ Race condition защита (можно с `threading` или `pytest-xdist`)
- ✅ Permission checks (каждая роль для каждого эндпоинта)
- ✅ Event payload корректность

---

## Code Review чеклист

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
# Architecture Decision Records (ADR)

Все важные архитектурные решения задокументированы здесь.
Перед добавлением нового — прочти существующие. Не отменяй ADR без обсуждения.

Формат: **Контекст → Решение → Причина → Последствия**

---

## ADR-001: Модульный монолит, не микросервисы

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

## ADR-002: delivery_format живёт в CourseEnrollment, не в Course

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

## ADR-003: Реальные FK к Identity Domain пока монолит

**Статус:** Принято  
**Дата:** Дизайн Learning Domain

**Контекст:** Как ссылаться на `User` из Learning/Progress доменов?

**Отклонённые варианты:**
- `user_id = UUIDField()` без FK → нет DB integrity, нет ORM `select_related`, каскады вручную

**Решение:** `ForeignKey(settings.AUTH_USER_MODEL)` с реальными DB constraints.

**Причина:** Оба домена в одной БД. Real FK даёт: PROTECT/CASCADE семантику, `select_related`, DB integrity. При выделении в микросервисы — убирается одной миграцией.

**Последствия:** Зависимость на уровне схемы. Задокументирована, управляема.

---

## ADR-004: Синхронный каскад completion, не event-driven

**Статус:** Принято  
**Дата:** Дизайн UserProgress Domain

**Контекст:** Как реализовать lesson → module → course completion chain?

**Отклонённые варианты:**
- Event-driven (каждый шаг через event) → гонки, сложность отладки, нет гарантий порядка

**Решение:** Вся цепочка `_check_lesson → _check_module → _check_course` — один `transaction.atomic()` с `select_for_update()` на каждом уровне. Внешние events (Notifications, Analytics) — через `transaction.on_commit()`.

**Причина:** Единая транзакция = атомарность. Трейсить один call stack, не event chain. Параллелизм решён row-level locks.

**Последствия:** Требует `select_for_update()` на всех progress моделях в cascade chain.

---

## ADR-005: Snapshot counters с F() expressions

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

## ADR-006: CourseCategory — один FK, не junction table

**Статус:** Принято  
**Дата:** Дизайн Learning Domain v2

**Контекст:** Как связать курсы с категориями?

**Решение:** `Course.category_id → CourseCategory` — nullable FK. Один курс, одна категория.

**Причина:** Junction table нужна только если курс принадлежит нескольким категориям одновременно. Для LearnFlow это edge case, который пока не нужен. Добавить junction при необходимости без breaking changes.

**Последствия:** Если нужны мультикатегории — добавить `CourseCategoryAssignment` без изменения существующих данных.

---

## ADR-007: SELECT FOR UPDATE во всём cascade chain

**Статус:** Принято  
**Дата:** Review UserProgress Domain (F18)

**Контекст:** Bulk offline attendance (5 уроков одновременно) создаёт race condition на `completed_lessons_count`.

**Решение:** `select_for_update()` на `ModuleProgress` и `CourseProgress` в начале каждого completion check.

**Причина:** Без locks concurrent workers читают одно значение, пишут одно значение — теряют инкремент. Студент застревает навсегда.

**Последствия:** Row-level locking = serialization на уровне enrollment. Deadlock теоретически возможен — порядок lock acquisition должен быть lesson → module → course (всегда снизу вверх).

---

## ADR-008: Fan-out операции — только async (Celery)

**Статус:** Принято  
**Дата:** Review UserProgress Domain (F1)

**Контекст:** Event handlers обновляли N строк синхронно, где N = кол-во enrolled студентов.

**Решение:** Все операции вида "обновить X у всех студентов на курсе" → Celery task + batch processing (500 строк/батч).

**Триггеры для async:** LessonPublished, LessonDeleted, LessonContentAdded, LessonContentDeleted, ModulePublished, AssessmentAdded.

**Последствия:** Краткая eventual consistency. Студент может не сразу увидеть новый урок (секунды, не минуты). Acceptable.

---

## ADR-009: Оценка assessment — смешанная (auto + manual)

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

## ADR-010: Assessment — контейнер, не тип

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

## ADR-011: Mentor override с историей изменений

**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Ментор может пересмотреть авто-оценку. Нужна прозрачность.

**Решение:**
- `AssessmentResponse`: `auto_points`, `mentor_points`, `final_points`
- `AssessmentReviewLog`: audit trail всех изменений

**Причина:** Споры студент/ментор через год. История покажет кто и почему изменил.

**Последствия:** Дополнительная таблица, но критична для доверия к платформе.

---

## ADR-012: Project submissions через Submissions Domain

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

## ADR-013: Interview type — MVP подход

**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужны интервью с менторами. Live-интервью сложны (scheduling, video, recording).

**Решение для v1:** `interview` тип = текстовый ответ + ментор проверяет (как `text_answer` с другим названием).

**Решение для v2:** Отдельная таблица `InterviewSession`, Zoom integration, scheduling.

**Причина:** MVP killer avoidance. Live-интервью — Phase 2.

**Последствия:** v1 ограничен async интервью. Live появится позже.

---

## ADR-014: Assignment вместо отдельных LessonHomework и ProjectTask

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

## ADR-015: Версионирование через SubmissionRevision

**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Студент пересдаёт работу после замечаний ментора.

**Решение:** `Submission` (контейнер) + `SubmissionRevision` (версии).

**Причина:** Студент почти всегда пересдаёт. Нужна история изменений.

**Последствия:** Ментор всегда проверяет конкретную ревизию, не Submission целиком.

---

## ADR-016: Payload JSONB для разных типов submission

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

## ADR-017: Автопроверки отдельно от mentor review

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

## ADR-018: Обязательная проверка файлов на вирусы

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

## ADR-019: Студент НЕ выбирает ментора (v1)

**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужна система назначения студентов менторам.

**Отклонённые варианты:**
- Студент выбирает ментора сам — балансировка нагрузки невозможна

**Решение:** Только admin назначает студентов в группы. Один ментор → одна группа → N студентов.

**Причина:** Популярные менторы перегружены, непопулярные простаивают. Нужен контроль.

**Последствия:** В v2 можно добавить авто-распределение (round-robin, capacity-based).

---

## ADR-020: Расписание — динамическое, не жёсткое

**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Нужно планировать offline занятия.

**Отклонённые варианты:**
- Привязать Module к датам (Module 1: 2026-01-01, 2026-01-03...) — ломается при переносах

**Решение:** `OfflineSession` — отдельная сущность с `scheduled_start/end`, `status` (scheduled/cancelled/rescheduled).

**Причина:** Реальная жизнь: праздники, болезнь, отключение света. Расписание должно быть гибким.

**Последствия:** Занятия можно отменять, переносить без изменения структуры модуля.

---

## ADR-021: Attendance — ментор отмечает вручную, турникет = подсказка

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

## ADR-022: Mentor override для lesson completion

**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Offline обучение не всегда укладывается в правила (контент просмотрен, домашка сдана).

**Решение:** `LessonProgress.completion_source` может быть `mentor_override`.

**Причина:** Ментор на месте, он знает лучше. Студент может выполнить задание устно в аудитории.

**Последствия:** Нужен audit trail: `override_by_id`, `override_reason`, `override_at`.

---

## ADR-023: Mentor work queue — критичная функция для v1

**Статус:** Принято  
**Дата:** 2026-06-07

**Контекст:** Ментор должен видеть что нужно проверить.

**Решение:** Read model `MentorWorkReview` — очередь работ с сортировкой (overdue → oldest).

**Причина:** Без этого ментор не знает что проверять первым. Это важнее чатов и комментариев.

**Последствия:** Таблица обновляется через события (SubmissionSubmitted, AssessmentNeedsMentorReview).

---

## ADR-024: Certificate template system

**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** Разные курсы требуют разные дизайны сертификатов.

**Решение:** `CertificateTemplate` таблица с конфигурацией layout/fonts. `Course → template_id`.

**Причина:** Один шаблон для всех курсов — плохой UX. Backend и Design курсы требуют разные визуалы.

**Последствия:** Admin может создавать новые шаблоны без кода.

---

## ADR-025: Snapshot данных при выдаче сертификата

**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** Студент может изменить имя в профиле после получения сертификата.

**Решение:** `student_full_name_snapshot`, `course_name_snapshot` — копии на момент выдачи.

**Причина:** Сертификат — юридический документ. Нельзя автоматически обновлять.

**Последствия:** Если нужно переиздать — через `CertificateReissueRequest`.

---

## ADR-026: PDF generation — только async

**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** Генерация PDF занимает 5-15 секунд.

**Отклонённые варианты:**
- Синхронная генерация в `CourseCompleted` handler — блокирует UserProgress

**Решение:** Celery task `generate_certificate.delay()`.

**Причина:** Не блокировать завершение курса.

**Последствия:** Сертификат доступен не мгновенно (статус `pending` → `issued`).

---

## ADR-027: Сохранять PDF, не генерировать каждый раз

**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** 10,000 скачиваний = 10,000 генераций?

**Решение:** `Certificate.pdf_url` — сохраняем PDF в S3 один раз.

**Причина:** Генерация дорогая (CPU, время). Бессмысленно повторять.

**Последствия:** S3 storage cost (минимальный).

---

## ADR-028: Revoke механизм для сертификатов

**Статус:** Принято  
**Дата:** 2026-06-08

**Контекст:** Нужна возможность отозвать сертификат (списывание, ошибка выдачи).

**Решение:** `Certificate.status = 'revoked'` + `revoked_at`, `revoked_by_id`, `revoked_reason`.

**Причина:** Сертификаты могут быть выданы ошибочно или нечестно получены.

**Последствия:** Публичная страница показывает "Certificate Revoked" с причиной.

---

## Шаблон для нового ADR

```markdown
## ADR-XXX: [Краткое название решения]

**Статус:** Принято / Отклонено / Устарело  
**Дата:** YYYY-MM-DD

**Контекст:** Что происходит? Какая проблема?

**Отклонённые варианты:** Что рассматривалось и почему не выбрано?

**Решение:** Что именно решили сделать.

**Причина:** Почему именно так.

**Последствия:** Что меняется, что усложняется, что упрощается.
```
# Assessment Domain — Design v3

**Дата:** 2026-06-07  
**Статус:** ПРИНЯТО  
**Версия:** 3.0 (полный редизайн)

---

## Ключевые решения

### 1. Assessment — это контейнер, не тип

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

### 2. Оценивание в баллах с mentor override

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

### 3. Типы AssessmentItem

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

### 4. Связь Assessment ↔ Submissions

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

### 5. Interview type (MVP подход)

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

## Схема БД (обновлённая)

### assessment_moduleassessment

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

### assessment_assessmentitem

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

### assessment_assessmentattempt

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

### assessment_assessmentresponse

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

### assessment_assessmentreviewlog (НОВАЯ)

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

### assessment_assessmentoption (без изменений)

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| item_id | FK → assessment_assessmentitem | |
| text | TEXT | |
| is_correct | BOOLEAN | |
| order | SMALLINT | |
| explanation | TEXT NULLABLE | |

---

### assessment_codingtestcase (без изменений)

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

### assessment_codingtestcaseresult (без изменений)

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

## Примеры

### Пример 1: Python Basics Assessment

```yaml
Assessment:
  title: "Python Basics — Final Test"
  passing_percentage: 70.00
  max_attempts: 3
  time_limit_minutes: 90
  max_score: 100  # автоматически считается из items

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

### Пример 2: Django Project Assessment

```yaml
Assessment:
  title: "Django Blog API — Final Project"
  passing_percentage: 75.00
  max_attempts: 1
  time_limit_minutes: NULL  # нет лимита

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

## События

### Исходящие (из Assessment Domain)

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

### Входящие (от других доменов)

```python
# От Submissions Domain
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
    
    # Проверить не завершён ли весь attempt
    GradingService.check_attempt_completion(response.attempt_id)
```

---

## ADR (новые решения)

### ADR-010: Assessment — контейнер, не тип

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

### ADR-011: Mentor override с историей изменений

**Контекст:** Ментор может пересмотреть авто-оценку. Нужна прозрачность.

**Решение:**
- `AssessmentResponse`: `auto_points`, `mentor_points`, `final_points`
- `AssessmentReviewLog`: audit trail всех изменений

**Причина:** Споры студент/ментор через год. История покажет кто и почему изменил.

**Последствия:** Дополнительная таблица, но критична для доверия к платформе.

---

### ADR-012: Project submissions через Submissions Domain

**Контекст:** Assessment item type=project требует кодовую базу/файлы/GitHub repo.

**Решение:** Assessment НЕ хранит проекты. Создаёт `ProjectTask` в Submissions Domain. Результат возвращается через событие `SubmissionReviewed`.

**Причина:**
- Разделение ответственности: Assessment = оценивание, Submissions = хранение работ
- Submissions может расти независимо (versioning, diff, CI integration)
- Assessment остаётся lightweight

**Последствия:** Cross-domain event dependency. Submissions Domain обязателен для project items.

---

### ADR-013: Interview type — MVP подход

**Контекст:** Нужны интервью с менторами. Live-интервью сложны (scheduling, video, recording).

**Решение для v1:** `interview` тип = текстовый ответ + ментор проверяет (как `text_answer` с другим названием).

**Решение для v2:** Отдельная таблица `InterviewSession`, Zoom integration, scheduling.

**Причина:** MVP killer avoidance. Live-интервью — Phase 2.

**Последствия:** v1 ограничен async интервью. Live появится позже.

---

## Что дальше

1. ✅ Дизайн Assessment завершён
2. 🟡 Дизайн Submissions Domain (связь с project items)
3. 🟡 Дизайн Mentorship Domain (ментор как reviewer)
4. 🟡 Дизайн Certificates Domain (после CourseCompleted)
5. ⬜ Обновить `docs/DATABASE.md` с новой схемой
6. ⬜ Добавить ADR-010, ADR-011, ADR-012, ADR-013 в `docs/DECISIONS.md`
7. ⬜ Обновить `docs/CONVERSATION_LOG.md`
8. ⬜ Обновить `CLAUDE.md` (статус Assessment → ДИЗАЙН ГОТОВ)
# Certificates Domain — Design v1

**Дата:** 2026-06-08  
**Статус:** ПРИНЯТО  
**Версия:** 1.0

---

## Ключевые решения

### 1. Template system — разные шаблоны для разных курсов

**Решение:** НЕ привязывать сертификат к одному PDF-шаблону.

**Причина:**
```
Сейчас:
  Python Backend
  Frontend React
  DevOps

Через год:
  English
  UI/UX Design
  Soft Skills
```

Разные курсы требуют разные дизайны сертификатов.

**Схема:**
```sql
CertificateTemplate:
  id UUID
  name VARCHAR(255)
  background_image TEXT
  pdf_template TEXT
  is_active BOOLEAN

Course:
  certificate_template_id UUID FK
```

**Пример:**
```
Python Backend → Backend Template
English → Language Template
UI/UX Design → Design Template (с другим background)
```

---

### 2. Verification — публичная страница обязательна

**Решение:** Каждый сертификат имеет `verification_code` — уникальный публичный идентификатор.

**Формат:** `LF-{YEAR}-{RANDOM_6_CHARS}`

**Пример:** `LF-2026-8AF3D2`

**Публичная страница:**
```
/certificates/verify/{verification_code}

Показывает:
  ✓ Valid Certificate
  
  Student Name: Ozodbek Xasanov
  Course: Python Backend Development
  Issue Date: 2026-06-08
  Certificate Number: LF-2026-8AF3D2
  
  Issued by: LearnFlow Academy
```

**Зачем:** Работодатели проверяют подлинность сертификатов.

**Примеры:** Coursera, Udemy, LinkedIn Learning — все имеют verification.

---

### 3. Snapshot данных — НЕ регенерировать при изменении профиля

**Решение:** Сертификат — юридический снимок на момент выдачи.

**Snapshot полей:**
```sql
Certificate:
  student_full_name_snapshot VARCHAR(255)
  course_name_snapshot VARCHAR(255)
  course_description_snapshot TEXT
  issued_at TIMESTAMPTZ
```

**Пример:**
```
2026-01-10 — сертификат выдан:
  Student: Ozodbek Xasanov

2026-02-15 — профиль изменился:
  Student: Ozodbek Khasanov

Старый сертификат остаётся старым.
```

**Если нужно переиздать:**
```sql
CertificateReissueRequest:
  certificate_id UUID
  reason TEXT
  requested_by_id UUID
  requested_at TIMESTAMPTZ
```

Через админа.

---

### 4. PDF generation — только async через Celery

**Решение:** НИКОГДА синхронно.

**Причина:**
```
CourseCompleted event
  ↓
Generate PDF (5-15 секунд)
  ↓
Upload S3
  ↓
Send notification
```

Если делать синхронно:
```
UserProgress → CourseCompleted → PDF generation
```

можно **заблокировать завершение курса**.

**Правильный flow:**
```python
CourseCompleted event
    ↓
CertificateService.request_certificate(enrollment_id)
    ↓
Certificate created (status='pending')
    ↓
Celery task: generate_certificate.delay(certificate_id)
    ↓
PDF generated → Upload S3 → status='issued'
    ↓
CertificateIssued event → Notifications
```

---

### 5. Сохранять PDF, не генерировать каждый раз

**Решение:**
```sql
Certificate:
  pdf_url TEXT  -- S3 URL
```

**Зачем:**
```
10,000 скачиваний = 10,000 генераций PDF
```

Это бессмысленно.

**Правильно:**
```
Generate once → Save to S3 → Return URL
```

**Если нужно переиздать:**
- Создать новый `Certificate` с новым `verification_code`
- Старый сертификат → `status='revoked'`

---

### 6. Статусы сертификата

```
pending   — Создан, PDF генерируется
issued    — Выдан, PDF доступен
revoked   — Отозван (нарушение правил, переиздан новый)
```

**Пример revoke:**
```
Студент списал на assessment.
После проверки обнаружено нарушение.

Admin:
  Certificate.status = 'revoked'
  revoked_at = NOW()
  revoked_by_id = admin_id
  revoked_reason = "Academic dishonesty detected"
```

Публичная страница `/certificates/verify/{code}`:
```
✗ Certificate Revoked

This certificate was revoked on 2026-06-15.
Reason: Academic dishonesty detected.
```

---

## Схема БД

### certificates_certificatetemplate

**Цель:** Шаблоны PDF для разных курсов.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| name | VARCHAR(255) | "Backend Certificate Template" |
| description | TEXT NULLABLE | |
| background_image | TEXT | S3 URL для фона |
| pdf_template | TEXT | Path к Jinja2 template или HTML |
| font_config | JSONB | Шрифты, размеры, цвета |
| layout_config | JSONB | Позиции элементов (name, course, date) |
| is_active | BOOLEAN DEFAULT TRUE | |
| created_by_id | UUID FK | → accounts_user |
| created_at / updated_at | TIMESTAMPTZ | |

**Пример font_config:**
```json
{
  "student_name": {
    "font": "Montserrat-Bold",
    "size": 36,
    "color": "#1a1a1a",
    "position": {"x": 400, "y": 300}
  },
  "course_name": {
    "font": "Montserrat-Regular",
    "size": 24,
    "color": "#4a4a4a",
    "position": {"x": 400, "y": 350}
  }
}
```

---

### certificates_certificate

**Цель:** Выданный сертификат студенту.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| user_id | UUID FK | → accounts_user (PROTECT) |
| enrollment_id | UUID FK | → courses_courseenrollment |
| course_id | UUID (denorm) | |
| template_id | UUID FK | → certificates_certificatetemplate |
| certificate_number | VARCHAR(50) UNIQUE | "LF-2026-8AF3D2" |
| verification_code | VARCHAR(50) UNIQUE | То же что certificate_number (для URL) |
| student_full_name_snapshot | VARCHAR(255) | Snapshot на момент выдачи |
| course_name_snapshot | VARCHAR(255) | Snapshot |
| course_description_snapshot | TEXT NULLABLE | Snapshot |
| final_score | DECIMAL(6,2) NULLABLE | Финальный результат курса (если есть) |
| completion_date | DATE | Дата завершения курса |
| issued_at | TIMESTAMPTZ | Когда сертификат выдан |
| pdf_url | TEXT NULLABLE | S3 URL к PDF файлу |
| pdf_generated_at | TIMESTAMPTZ NULLABLE | |
| status | VARCHAR(20) | pending / issued / revoked |
| revoked_at | TIMESTAMPTZ NULLABLE | |
| revoked_by_id | UUID FK NULLABLE | → accounts_user |
| revoked_reason | TEXT NULLABLE | |
| metadata | JSONB | Доп. данные (signature URL, QR code, etc.) |

**Indexes:**
- UNIQUE `certificate_number`
- UNIQUE `verification_code`
- ON `(user_id, course_id)` — один студент, один курс, один сертификат (актуальный)
- ON `(status, issued_at DESC)` WHERE status='issued'

**Constraints:**
- CHECK: `status IN ('pending', 'issued', 'revoked')`

---

### certificates_certificatereissuerequest

**Цель:** Запросы на переиздание сертификата.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| certificate_id | UUID FK | → certificates_certificate |
| reason | TEXT | "Name change in profile", "Lost original" |
| requested_by_id | UUID FK | → accounts_user (student or admin) |
| requested_at | TIMESTAMPTZ | |
| status | VARCHAR(20) | pending / approved / rejected |
| reviewed_by_id | UUID FK NULLABLE | → accounts_user (admin) |
| reviewed_at | TIMESTAMPTZ NULLABLE | |
| new_certificate_id | UUID FK NULLABLE | → certificates_certificate (если одобрено) |

**Constraints:**
- CHECK: `status IN ('pending', 'approved', 'rejected')`

---

### certificates_certificateauditlog

**Цель:** История изменений сертификата.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| certificate_id | UUID FK | → certificates_certificate |
| action | VARCHAR(50) | created / issued / revoked / reissued / downloaded |
| actor_id | UUID FK NULLABLE | → accounts_user |
| details | JSONB | Доп. информация |
| ip_address | INET NULLABLE | |
| created_at | TIMESTAMPTZ | |

**Пример:**
```json
{
  "action": "revoked",
  "actor_id": "admin-uuid",
  "details": {
    "reason": "Academic dishonesty",
    "old_status": "issued",
    "new_status": "revoked"
  },
  "ip_address": "192.168.1.1",
  "created_at": "2026-06-08T12:00:00Z"
}
```

---

## События

### Исходящие (из Certificates Domain)

```python
@dataclass
class CertificateRequested:
    certificate_id: UUID
    enrollment_id: UUID
    user_id: UUID
    course_id: UUID
    occurred_at: datetime

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

@dataclass
class CertificateRevoked:
    certificate_id: UUID
    user_id: UUID
    course_id: UUID
    revoked_by_id: UUID
    reason: str
    revoked_at: datetime
```

### Входящие (от других доменов)

```python
# От UserProgress Domain
@receiver(course_completed)
def handle_course_completed(sender, event: CourseCompleted, **kwargs):
    """
    Запросить генерацию сертификата.
    """
    certificate = CertificateService.request_certificate(
        enrollment_id=event.enrollment_id,
        user_id=event.user_id,
        course_id=event.course_id,
        completion_date=event.completed_at.date(),
    )
    
    # Async generation
    tasks.generate_certificate.delay(certificate.id)
```

---

## Примеры flow

### Пример 1: Выдача сертификата после завершения курса

```
1. UserProgress → CourseCompleted event

2. Certificates слушает:
   - CertificateService.request_certificate()
   - Certificate created (status='pending')
   - CertificateRequested event

3. Celery task: generate_certificate.delay(certificate_id)
   - Fetch Certificate + Template
   - Snapshot данных (student name, course name)
   - Render PDF (Jinja2 + WeasyPrint или ReportLab)
   - Upload to S3
   - Certificate.pdf_url = s3_url
   - Certificate.status = 'issued'
   - Certificate.issued_at = NOW()

4. CertificateIssued event

5. Notifications слушает:
   - Send email to student:
     "Congratulations! Your certificate is ready."
     Link: /certificates/{verification_code}
```

### Пример 2: Проверка сертификата работодателем

```
1. Работодатель получает от кандидата:
   Certificate Number: LF-2026-8AF3D2

2. Переходит: /certificates/verify/LF-2026-8AF3D2

3. Система показывает:
   
   ✓ Valid Certificate
   
   Student Name: Ozodbek Xasanov
   Course: Python Backend Development
   Completion Date: 2026-06-08
   Certificate Number: LF-2026-8AF3D2
   
   Issued by: LearnFlow Academy
   
   [Download PDF]

4. Работодатель уверен в подлинности.
```

### Пример 3: Revoke сертификата

```
Ситуация: Обнаружено списывание на assessment.

1. Admin открывает Certificate:
   - status = 'issued'
   - pdf_url = "https://..."

2. Admin нажимает "Revoke Certificate":
   - CertificateService.revoke(
       certificate_id=...,
       revoked_by_id=admin_id,
       reason="Academic dishonesty detected"
     )

3. Certificate обновляется:
   - status = 'revoked'
   - revoked_at = NOW()
   - revoked_by_id = admin_id
   - revoked_reason = "..."

4. CertificateAuditLog:
   - action = 'revoked'
   - details = {...}

5. CertificateRevoked event → Notifications

6. Публичная страница /certificates/verify/{code}:
   
   ✗ Certificate Revoked
   
   This certificate was revoked on 2026-06-08.
   Reason: Academic dishonesty detected.
```

### Пример 4: Переиздание сертификата

```
Ситуация: Студент изменил имя в профиле.

1. Student создаёт CertificateReissueRequest:
   - reason = "Name change: Ozodbek Xasanov → Ozodbek Khasanov"
   - status = 'pending'

2. Admin проверяет:
   - Reason valid?
   - Profile change confirmed?

3. Admin approves:
   - CertificateReissueRequest.status = 'approved'
   - reviewed_by_id = admin_id

4. Система автоматически:
   - Старый Certificate → status='revoked', revoked_reason="Reissued"
   - Новый Certificate создаётся (новый verification_code)
   - Celery task генерирует новый PDF
   - CertificateReissueRequest.new_certificate_id = new_cert_id

5. Student получает уведомление:
   "Your certificate has been reissued."
   New verification code: LF-2026-9D2F7A
```

---

## Технические детали

### PDF Generation

**Библиотеки (выбрать одну):**

1. **WeasyPrint** (HTML → PDF)
   - Pros: HTML/CSS template, легко дизайн
   - Cons: Медленно для сложных layout

2. **ReportLab** (Python → PDF)
   - Pros: Быстро, полный контроль
   - Cons: Код сложнее, нет HTML

3. **wkhtmltopdf** (HTML → PDF via webkit)
   - Pros: Хороший рендеринг HTML/CSS
   - Cons: External binary, сложность деплоя

**Рекомендация для v1:** WeasyPrint (проще дизайн через HTML/CSS).

**Celery task:**
```python
@shared_task(bind=True, max_retries=3)
def generate_certificate(self, certificate_id: str):
    try:
        cert = Certificate.objects.get(pk=certificate_id)
        template = cert.template
        
        # Render HTML
        html = render_certificate_html(cert, template)
        
        # Generate PDF
        pdf_bytes = HTML(string=html).write_pdf()
        
        # Upload to S3
        s3_key = f"certificates/{cert.certificate_number}.pdf"
        pdf_url = upload_to_s3(pdf_bytes, s3_key)
        
        # Update Certificate
        cert.pdf_url = pdf_url
        cert.pdf_generated_at = timezone.now()
        cert.status = 'issued'
        cert.issued_at = timezone.now()
        cert.save()
        
        # Dispatch event
        dispatch(CertificateIssued(...))
        
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

---

### Verification Code Generation

**Формат:** `LF-{YEAR}-{RANDOM_6_CHARS}`

**Алгоритм:**
```python
import secrets
import string
from datetime import datetime

def generate_verification_code() -> str:
    year = datetime.now().year
    random_part = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(6)
    )
    return f"LF-{year}-{random_part}"
```

**Collision handling:**
```python
while True:
    code = generate_verification_code()
    if not Certificate.objects.filter(verification_code=code).exists():
        return code
```

---

### Security

**Публичная страница `/certificates/verify/{code}`:**
- НЕ требует авторизации
- Показывает только публичную информацию:
  - Student name
  - Course name
  - Issue date
  - Status (valid/revoked)
- НЕ показывает:
  - Email студента
  - Enrollment details
  - Internal IDs

**Rate limiting:**
```python
# 100 requests per hour per IP
@ratelimit(key='ip', rate='100/h', method='GET')
def verify_certificate(request, verification_code):
    ...
```

**Предотвращение brute-force:**
- Verification code — 6 символов (A-Z, 0-9) = 36^6 = ~2 миллиарда комбинаций
- Rate limiting блокирует перебор

---

## ADR (новые решения)

### ADR-024: Certificate template system

**Контекст:** Разные курсы требуют разные дизайны сертификатов.

**Решение:** `CertificateTemplate` таблица с конфигурацией layout/fonts. `Course → template_id`.

**Причина:** Один шаблон для всех курсов — плохой UX. Backend и Design курсы требуют разные визуалы.

**Последствия:** Admin может создавать новые шаблоны без кода.

---

### ADR-025: Snapshot данных при выдаче сертификата

**Контекст:** Студент может изменить имя в профиле после получения сертификата.

**Решение:** `student_full_name_snapshot`, `course_name_snapshot` — копии на момент выдачи.

**Причина:** Сертификат — юридический документ. Нельзя автоматически обновлять.

**Последствия:** Если нужно переиздать — через `CertificateReissueRequest`.

---

### ADR-026: PDF generation — только async

**Контекст:** Генерация PDF занимает 5-15 секунд.

**Отклонённые варианты:**
- Синхронная генерация в `CourseCompleted` handler — блокирует UserProgress

**Решение:** Celery task `generate_certificate.delay()`.

**Причина:** Не блокировать завершение курса.

**Последствия:** Сертификат доступен не мгновенно (статус `pending` → `issued`).

---

### ADR-027: Сохранять PDF, не генерировать каждый раз

**Контекст:** 10,000 скачиваний = 10,000 генераций?

**Решение:** `Certificate.pdf_url` — сохраняем PDF в S3 один раз.

**Причина:** Генерация дорогая (CPU, время). Бессмысленно повторять.

**Последствия:** S3 storage cost (минимальный).

---

### ADR-028: Revoke механизм для сертификатов

**Контекст:** Нужна возможность отозвать сертификат (списывание, ошибка выдачи).

**Решение:** `Certificate.status = 'revoked'` + `revoked_at`, `revoked_by_id`, `revoked_reason`.

**Причина:** Сертификаты могут быть выданы ошибочно или нечестно получены.

**Последствия:** Публичная страница показывает "Certificate Revoked" с причиной.

---

## Интеграция с другими доменами

### UserProgress Domain

```python
# UserProgress emit
CourseCompleted → Certificates → request_certificate()

# Certificates emit
CertificateIssued → Notifications → send email
```

### Notifications Domain

```python
@receiver(certificate_issued)
def handle_certificate_issued(sender, event, **kwargs):
    NotificationService.send_email(
        user_id=event.user_id,
        template='certificate_ready',
        context={
            'certificate_number': event.certificate_number,
            'verification_url': f'/certificates/verify/{event.verification_code}',
        }
    )
```

---

## Что дальше

1. ✅ Дизайн Certificates завершён
2. ✅ Все 4 домена спроектированы (Assessment, Submissions, Mentorship, Certificates)
3. ⬜ Обновить `docs/DATABASE.md` (добавить все 4 домена)
4. ⬜ Добавить ADR-024..028 в `docs/DECISIONS.md`
5. ⬜ Обновить `docs/CONVERSATION_LOG.md`
6. ⬜ Обновить `CLAUDE.md` (статусы доменов → ДИЗАЙН ГОТОВ)
7. ⬜ Обновить `TASKS.md` (обновить Phase 1A → завершено)
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LearnFlow — Application Layer Design</title>
<style>
  :root {
    --accent: #534AB7;
    --accent-light: #EEEDFE;
    --accent-mid: #AFA9EC;
    --teal: #0F6E56;
    --teal-light: #E1F5EE;
    --coral: #993C1D;
    --coral-light: #FAECE7;
    --amber: #854F0B;
    --amber-light: #FAEEDA;
    --sky: #0C5E8A;
    --sky-light: #E0F2FE;
    --gray: #444441;
    --gray-light: #F1EFE8;
    --text: #1a1a18;
    --text-muted: #5F5E5A;
    --border: #D3D1C7;
    --bg: #ffffff;
    --bg-page: #f7f6f2;
    --code-bg: #F1EFE8;
    --green: #166534;
    --green-light: #dcfce7;
    --red: #991b1b;
    --red-light: #fee2e2;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system,'Segoe UI',Arial,sans-serif; font-size:15px; line-height:1.7; color:var(--text); background:var(--bg-page); }
  .layout { display:flex; min-height:100vh; }

  nav {
    width:264px; min-width:264px; background:var(--bg);
    border-right:1px solid var(--border); padding:24px 0;
    position:sticky; top:0; height:100vh; overflow-y:auto;
  }
  nav .logo { padding:0 20px 20px; border-bottom:1px solid var(--border); margin-bottom:12px; }
  nav .logo h1 { font-size:15px; font-weight:600; color:var(--accent); }
  nav .logo p { font-size:11px; color:var(--text-muted); margin-top:2px; }
  nav a { display:block; padding:7px 20px; font-size:13px; color:var(--text-muted); text-decoration:none; border-left:2px solid transparent; transition:all 0.15s; }
  nav a:hover { color:var(--accent); background:var(--accent-light); border-left-color:var(--accent); }
  nav .section-label { padding:14px 20px 4px; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); }
  nav a.sub { padding-left:32px; font-size:12px; }

  main { flex:1; padding:48px 56px; max-width:1040px; }
  section { margin-bottom:64px; }

  h2 { font-size:26px; font-weight:600; color:var(--text); margin-bottom:8px; padding-bottom:12px; border-bottom:2px solid var(--accent-light); }
  h2 .tag { display:inline-block; font-size:11px; font-weight:500; background:var(--accent-light); color:var(--accent); padding:2px 8px; border-radius:4px; margin-left:10px; vertical-align:middle; letter-spacing:0.05em; }
  h3 { font-size:17px; font-weight:600; color:var(--text); margin:28px 0 12px; }
  h4 { font-size:14px; font-weight:600; color:var(--text); margin:16px 0 6px; }
  p { margin-bottom:12px; color:var(--text-muted); font-size:14px; }

  pre { background:var(--code-bg); border:1px solid var(--border); border-radius:8px; padding:16px 18px; font-family:'SF Mono','Fira Code','Cascadia Code',monospace; font-size:12.5px; line-height:1.65; overflow-x:auto; margin:12px 0; color:var(--text); }
  code { background:var(--code-bg); font-family:'SF Mono','Fira Code',monospace; font-size:12px; padding:1px 5px; border-radius:3px; color:var(--accent); }

  table { width:100%; border-collapse:collapse; margin:14px 0; font-size:13px; }
  th { background:var(--gray-light); font-weight:600; text-align:left; padding:9px 13px; border-bottom:2px solid var(--border); font-size:11px; text-transform:uppercase; letter-spacing:0.04em; }
  td { padding:8px 13px; border-bottom:1px solid var(--border); vertical-align:top; font-size:13px; }
  tr:last-child td { border-bottom:none; }
  td code { font-size:11.5px; }

  .callout { border-left:3px solid var(--accent); background:var(--accent-light); border-radius:0 8px 8px 0; padding:13px 16px; margin:14px 0; font-size:13.5px; color:var(--text); }
  .callout.warning { border-color:var(--amber); background:var(--amber-light); }
  .callout.success { border-color:var(--teal); background:var(--teal-light); }
  .callout.sky { border-color:var(--sky); background:var(--sky-light); }
  .callout.coral { border-color:var(--coral); background:var(--coral-light); }

  .badge { display:inline-block; font-size:10px; font-weight:700; padding:2px 7px; border-radius:3px; letter-spacing:0.05em; text-transform:uppercase; }
  .badge-get    { background:#dbeafe; color:#1e40af; }
  .badge-post   { background:var(--teal-light); color:var(--teal); }
  .badge-patch  { background:var(--amber-light); color:var(--amber); }
  .badge-delete { background:var(--coral-light); color:var(--coral); }
  .badge-yes    { background:var(--green-light); color:var(--green); }
  .badge-no     { background:var(--red-light); color:var(--red); }
  .badge-own    { background:var(--amber-light); color:var(--amber); }
  .badge-tag    { background:var(--accent-light); color:var(--accent); }

  /* Use case grid */
  .uc-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin:16px 0; }
  .uc-group { background:var(--bg); border:1px solid var(--border); border-radius:8px; overflow:hidden; }
  .uc-group-header { padding:8px 14px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; }
  .uc-group-header.accent { background:var(--accent); color:white; }
  .uc-group-header.teal   { background:var(--teal);   color:white; }
  .uc-group-header.sky    { background:var(--sky);    color:white; }
  .uc-group-header.amber  { background:var(--amber);  color:white; }
  .uc-group-header.coral  { background:var(--coral);  color:white; }
  .uc-group-header.gray   { background:var(--gray);   color:white; }
  .uc-item { padding:6px 14px; font-size:12.5px; color:var(--text-muted); border-bottom:1px dashed #e8e6e0; display:flex; align-items:center; gap:6px; }
  .uc-item:last-child { border-bottom:none; }
  .uc-num { font-size:10px; color:var(--text-muted); background:var(--gray-light); border-radius:3px; padding:1px 5px; font-family:monospace; min-width:28px; text-align:center; }

  /* Selector / Service blocks */
  .service-block { background:var(--bg); border:1px solid var(--border); border-radius:10px; margin-bottom:20px; overflow:hidden; }
  .service-header { padding:11px 18px; display:flex; align-items:center; justify-content:space-between; }
  .service-header.accent { background:var(--accent); }
  .service-header.teal   { background:var(--teal); }
  .service-header.sky    { background:var(--sky); }
  .service-header.amber  { background:var(--amber); }
  .service-header.coral  { background:var(--coral); }
  .service-header.gray   { background:var(--gray); }
  .service-header h4 { margin:0; font-size:14px; font-weight:700; color:white; font-family:'SF Mono',monospace; }
  .service-header span { font-size:11px; color:rgba(255,255,255,0.7); }
  .service-body { padding:16px 18px; }
  .service-body h5 { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:var(--text-muted); margin:14px 0 6px; }
  .service-body h5:first-child { margin-top:0; }
  .method-row { display:flex; gap:8px; align-items:flex-start; padding:6px 0; border-bottom:1px dashed #e8e6e0; font-size:13px; }
  .method-row:last-child { border-bottom:none; }
  .method-name { font-family:'SF Mono',monospace; font-size:12px; font-weight:600; color:var(--accent); min-width:220px; white-space:nowrap; }
  .method-desc { color:var(--text-muted); font-size:12.5px; }

  /* API endpoint blocks */
  .endpoint-block { background:var(--bg); border:1px solid var(--border); border-radius:10px; margin-bottom:16px; overflow:hidden; }
  .endpoint-header { padding:10px 16px; display:flex; align-items:center; gap:10px; border-bottom:1px solid var(--border); background:var(--gray-light); }
  .endpoint-path { font-family:'SF Mono',monospace; font-size:13px; font-weight:600; color:var(--text); }
  .endpoint-body { padding:14px 16px; display:grid; grid-template-columns:1fr 1fr; gap:16px; font-size:12.5px; }
  .endpoint-col h6 { font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:var(--text-muted); margin-bottom:6px; }
  .endpoint-col pre { margin:0; font-size:11.5px; }

  /* Permissions matrix */
  .perm-table th { font-size:11px; }
  .perm-table td { text-align:center; vertical-align:middle; }
  .perm-table td:first-child { text-align:left; font-size:12.5px; }
  .perm-yes    { color:var(--green); font-size:16px; }
  .perm-no     { color:#ccc; font-size:14px; }
  .perm-own    { color:var(--amber); font-size:13px; font-weight:700; }
  .perm-review { color:var(--sky); font-size:13px; font-weight:700; }

  /* Domain events */
  .event-block { background:var(--bg); border:1px solid var(--border); border-radius:10px; margin-bottom:14px; overflow:hidden; }
  .event-header { background:var(--accent); padding:9px 16px; display:flex; align-items:center; justify-content:space-between; }
  .event-header.teal  { background:var(--teal); }
  .event-header.sky   { background:var(--sky); }
  .event-header.amber { background:var(--amber); }
  .event-header.coral { background:var(--coral); }
  .event-header.gray  { background:var(--gray); }
  .event-header h4 { margin:0; font-size:13px; font-weight:700; color:white; font-family:'SF Mono',monospace; }
  .event-header span { font-size:11px; color:rgba(255,255,255,0.7); }
  .event-body { display:grid; grid-template-columns:1.4fr 1fr 1fr; gap:0; }
  .event-col { padding:12px 14px; border-right:1px solid var(--border); font-size:12.5px; }
  .event-col:last-child { border-right:none; }
  .event-col h6 { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:var(--text-muted); margin-bottom:6px; }
  .event-col ul { list-style:none; padding:0; }
  .event-col ul li { color:var(--text-muted); padding:2px 0; font-size:12px; }
  .event-col ul li::before { content:"→ "; color:var(--accent); }

  /* Dependency cards */
  .dep-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:16px 0; }
  .dep-card { background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:14px 16px; border-left:4px solid var(--accent); }
  .dep-card.blocking { border-left-color:var(--coral); }
  .dep-card.advisory { border-left-color:var(--amber); }
  .dep-card.design   { border-left-color:var(--sky); }
  .dep-card h4 { margin-top:0; font-size:13px; }
  .dep-card.blocking h4 { color:var(--coral); }
  .dep-card.advisory h4 { color:var(--amber); }
  .dep-card.design h4   { color:var(--sky); }
  .dep-card p { font-size:12px; margin-bottom:0; }

  hr { border:none; border-top:1px solid var(--border); margin:28px 0; }

  @media (max-width:1100px) { nav { display:none; } main { padding:24px 20px; } }
  @media (max-width:800px) { .uc-grid { grid-template-columns:1fr 1fr; } .event-body { grid-template-columns:1fr; } .endpoint-body { grid-template-columns:1fr; } .dep-grid { grid-template-columns:1fr; } }
  @media (max-width:600px) { .uc-grid { grid-template-columns:1fr; } }
</style>
</head>
<body>
<div class="layout">

<!-- SIDEBAR -->
<nav>
  <div class="logo">
    <h1>Application Layer</h1>
    <p>LearnFlow — Learning Domain v1.0</p>
  </div>
  <div class="section-label">Overview</div>
  <a href="#usecases">Use Cases</a>
  <div class="section-label">Read Layer</div>
  <a href="#selectors">Selectors Overview</a>
  <a class="sub" href="#sel-catalog">CourseCatalogSelector</a>
  <a class="sub" href="#sel-course">CourseDetailSelector</a>
  <a class="sub" href="#sel-lesson">LessonSelector</a>
  <a class="sub" href="#sel-enrollment">EnrollmentSelector</a>
  <a class="sub" href="#sel-quiz">QuizSelector</a>
  <div class="section-label">Write Layer</div>
  <a href="#services">Services Overview</a>
  <a class="sub" href="#svc-category">CourseCategoryService</a>
  <a class="sub" href="#svc-course">CourseService</a>
  <a class="sub" href="#svc-module">ModuleService</a>
  <a class="sub" href="#svc-lesson">LessonService</a>
  <a class="sub" href="#svc-content">LessonContentService</a>
  <a class="sub" href="#svc-homework">LessonHomeworkService</a>
  <a class="sub" href="#svc-practice">LessonPracticeService</a>
  <a class="sub" href="#svc-quiz">LessonQuizService</a>
  <a class="sub" href="#svc-enrollment">CourseEnrollmentService</a>
  <div class="section-label">API</div>
  <a href="#api">API Contracts</a>
  <a class="sub" href="#api-catalog">Catalog</a>
  <a class="sub" href="#api-course-mgmt">Course Management</a>
  <a class="sub" href="#api-structure">Course Structure</a>
  <a class="sub" href="#api-lesson">Lesson Components</a>
  <a class="sub" href="#api-enrollment">Enrollment</a>
  <div class="section-label">Governance</div>
  <a href="#permissions">Permissions Matrix</a>
  <a href="#events">Domain Events</a>
  <a href="#dependencies">UserProgress Dependencies</a>
</nav>

<main>

<!-- =================== USE CASES =================== -->
<section id="usecases">
  <h2>Use Cases <span class="tag">SECTION 1</span></h2>
  <p>All business actions the Learning Domain must support, grouped by actor and concern. These drive every selector, service, and API endpoint in this document.</p>

  <div class="uc-grid">

    <div class="uc-group">
      <div class="uc-group-header accent">🏷 Catalog (Public)</div>
      <div class="uc-item"><span class="uc-num">UC-01</span> List all published courses</div>
      <div class="uc-item"><span class="uc-num">UC-02</span> Filter courses by category</div>
      <div class="uc-item"><span class="uc-num">UC-03</span> Filter courses by delivery format</div>
      <div class="uc-item"><span class="uc-num">UC-04</span> View course detail (public)</div>
      <div class="uc-item"><span class="uc-num">UC-05</span> View free-preview lesson</div>
      <div class="uc-item"><span class="uc-num">UC-06</span> List all categories</div>
      <div class="uc-item"><span class="uc-num">UC-07</span> Search courses by keyword</div>
    </div>

    <div class="uc-group">
      <div class="uc-group-header sky">🎓 Student Learning</div>
      <div class="uc-item"><span class="uc-num">UC-08</span> Enroll in a course</div>
      <div class="uc-item"><span class="uc-num">UC-09</span> View my enrolled courses</div>
      <div class="uc-item"><span class="uc-num">UC-10</span> View course curriculum</div>
      <div class="uc-item"><span class="uc-num">UC-11</span> View lesson content</div>
      <div class="uc-item"><span class="uc-num">UC-12</span> View lesson homework definition</div>
      <div class="uc-item"><span class="uc-num">UC-13</span> View practice exercises</div>
      <div class="uc-item"><span class="uc-num">UC-14</span> View lesson quiz definition</div>
      <div class="uc-item"><span class="uc-num">UC-15</span> Drop a course</div>
    </div>

    <div class="uc-group">
      <div class="uc-group-header teal">📦 Course Authoring</div>
      <div class="uc-item"><span class="uc-num">UC-16</span> Create a course</div>
      <div class="uc-item"><span class="uc-num">UC-17</span> Edit course metadata</div>
      <div class="uc-item"><span class="uc-num">UC-18</span> Publish a course</div>
      <div class="uc-item"><span class="uc-num">UC-19</span> Archive a course</div>
      <div class="uc-item"><span class="uc-num">UC-20</span> Delete a course (soft)</div>
      <div class="uc-item"><span class="uc-num">UC-21</span> Create a module</div>
      <div class="uc-item"><span class="uc-num">UC-22</span> Edit module metadata</div>
      <div class="uc-item"><span class="uc-num">UC-23</span> Publish / unpublish module</div>
      <div class="uc-item"><span class="uc-num">UC-24</span> Reorder modules</div>
      <div class="uc-item"><span class="uc-num">UC-25</span> Delete module (soft)</div>
    </div>

    <div class="uc-group">
      <div class="uc-group-header amber">📝 Lesson Authoring</div>
      <div class="uc-item"><span class="uc-num">UC-26</span> Create a lesson</div>
      <div class="uc-item"><span class="uc-num">UC-27</span> Edit lesson metadata</div>
      <div class="uc-item"><span class="uc-num">UC-28</span> Publish / unpublish lesson</div>
      <div class="uc-item"><span class="uc-num">UC-29</span> Reorder lessons within a module</div>
      <div class="uc-item"><span class="uc-num">UC-30</span> Delete lesson (soft)</div>
      <div class="uc-item"><span class="uc-num">UC-31</span> Add content item to lesson</div>
      <div class="uc-item"><span class="uc-num">UC-32</span> Edit content item</div>
      <div class="uc-item"><span class="uc-num">UC-33</span> Reorder content items</div>
      <div class="uc-item"><span class="uc-num">UC-34</span> Delete content item</div>
      <div class="uc-item"><span class="uc-num">UC-35</span> Set / replace lesson homework</div>
      <div class="uc-item"><span class="uc-num">UC-36</span> Edit homework definition</div>
      <div class="uc-item"><span class="uc-num">UC-37</span> Remove homework from lesson</div>
    </div>

    <div class="uc-group">
      <div class="uc-group-header coral">✅ Quiz &amp; Practice</div>
      <div class="uc-item"><span class="uc-num">UC-38</span> Add practice item to lesson</div>
      <div class="uc-item"><span class="uc-num">UC-39</span> Edit practice item</div>
      <div class="uc-item"><span class="uc-num">UC-40</span> Reorder practice items</div>
      <div class="uc-item"><span class="uc-num">UC-41</span> Delete practice item</div>
      <div class="uc-item"><span class="uc-num">UC-42</span> Create lesson quiz</div>
      <div class="uc-item"><span class="uc-num">UC-43</span> Edit quiz settings</div>
      <div class="uc-item"><span class="uc-num">UC-44</span> Add question to quiz</div>
      <div class="uc-item"><span class="uc-num">UC-45</span> Edit question</div>
      <div class="uc-item"><span class="uc-num">UC-46</span> Reorder questions</div>
      <div class="uc-item"><span class="uc-num">UC-47</span> Add option to question</div>
      <div class="uc-item"><span class="uc-num">UC-48</span> Delete quiz</div>
    </div>

    <div class="uc-group">
      <div class="uc-group-header gray">⚙️ Admin &amp; Ops</div>
      <div class="uc-item"><span class="uc-num">UC-49</span> Create course category</div>
      <div class="uc-item"><span class="uc-num">UC-50</span> Edit / reorder category</div>
      <div class="uc-item"><span class="uc-num">UC-51</span> Deactivate category</div>
      <div class="uc-item"><span class="uc-num">UC-52</span> Enroll student (admin)</div>
      <div class="uc-item"><span class="uc-num">UC-53</span> Change student delivery format</div>
      <div class="uc-item"><span class="uc-num">UC-54</span> View all enrollments (course)</div>
      <div class="uc-item"><span class="uc-num">UC-55</span> Force-drop student enrollment</div>
      <div class="uc-item"><span class="uc-num">UC-56</span> View unpublished draft content</div>
    </div>

  </div>

  <div class="callout sky">
    <strong>Scope boundary:</strong> These use cases cover <em>content definition and enrollment creation only</em>. Tracking progress (UC-11 only returns the lesson definition, not the student's position), submitting homework, attempting quizzes, and issuing certificates are handled by separate domains that consume Learning Domain IDs.
  </div>
</section>

<!-- =================== SELECTORS =================== -->
<section id="selectors">
  <h2>Selectors — Read Layer <span class="tag">SECTION 2</span></h2>
  <p>Selectors are the <strong>only</strong> sanctioned way to read Learning Domain data. They own query optimisation (select_related, prefetch_related, annotations), caching strategy, and visibility rules. Views and other services never query models directly.</p>

  <div class="callout">
    <strong>Design rule:</strong> Selectors return querysets or plain Python objects (dataclasses / dicts). They never mutate data. They accept <code>user</code> as a parameter and apply visibility filters internally — callers never pass <code>is_published=True</code> themselves.
  </div>

  <hr>

  <h3 id="sel-catalog">CourseCatalogSelector</h3>
  <p>Handles all public-facing catalog queries. The hot read path — must be cheap and cacheable.</p>
  <div class="service-block">
    <div class="service-header teal">
      <h4>CourseCatalogSelector</h4>
      <span>Public catalog · fast, filterable, cacheable</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row">
        <span class="method-name">get_published_courses(filters, user)</span>
        <span class="method-desc">Returns published, non-deleted courses. Applies category/format filters. Annotates with <code>enrolled_count</code>, <code>module_count</code>. Respects <code>supports_online</code>/<code>supports_offline</code> filter if requested.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_course_card(slug)</span>
        <span class="method-desc">Lightweight single-course read for catalog card. Returns title, short_description, thumbnail, category, estimated_weeks, supports_* flags.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_all_categories()</span>
        <span class="method-desc">Returns active categories ordered by parent/order. Includes <code>course_count</code> annotation per category.</span>
      </div>
      <div class="method-row">
        <span class="method-name">search_courses(query, user)</span>
        <span class="method-desc">Full-text search on title + description. Returns published courses only. In Phase 1: icontains. Phase 2: pg_search / trigram index.</span>
      </div>
      <h5>Inputs</h5>
      <div class="method-row">
        <span class="method-name">filters</span>
        <span class="method-desc"><code>category_slug</code>, <code>delivery_format</code> (<code>online|offline</code>), <code>language</code>, <code>page</code>, <code>page_size</code></span>
      </div>
      <h5>Outputs</h5>
      <div class="method-row">
        <span class="method-name">Queryset / list</span>
        <span class="method-desc">Annotated Course queryset. Never exposes <code>deleted_at</code>, draft courses, or unpublished modules to unauthenticated callers.</span>
      </div>
    </div>
  </div>

  <hr>

  <h3 id="sel-course">CourseDetailSelector</h3>
  <p>Full course detail reads used by enrolled students, staff, and course authors. Visibility rules are stricter than the catalog.</p>
  <div class="service-block">
    <div class="service-header accent">
      <h4>CourseDetailSelector</h4>
      <span>Full course structure · visibility-aware</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row">
        <span class="method-name">get_course_detail(course_id, user)</span>
        <span class="method-desc">Returns full course + modules + lessons (metadata only, no content). Staff/author sees unpublished. Student sees published-only. Raises <code>NotFound</code> if deleted.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_course_for_author(course_id, user)</span>
        <span class="method-desc">Admin/Staff view. Returns all drafts and unpublished items. Raises <code>PermissionDenied</code> if user is not staff or <code>created_by</code>.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_modules_for_course(course_id, user)</span>
        <span class="method-desc">Returns ordered, visible modules for a course. Applies published filter based on role.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_course_by_slug(slug, user)</span>
        <span class="method-desc">Slug-based lookup used by public URLs. Raises <code>NotFound</code> for unpublished (unless staff).</span>
      </div>
      <h5>Visibility Rules</h5>
      <div class="method-row">
        <span class="method-name">Unauthenticated</span>
        <span class="method-desc">Published courses only. Free-preview lessons only.</span>
      </div>
      <div class="method-row">
        <span class="method-name">Student (enrolled)</span>
        <span class="method-desc">Published content only. No drafts.</span>
      </div>
      <div class="method-row">
        <span class="method-name">Staff / Admin</span>
        <span class="method-desc">All statuses including draft and unpublished.</span>
      </div>
    </div>
  </div>

  <hr>

  <h3 id="sel-lesson">LessonSelector</h3>
  <p>Lesson-level reads including all child components. Used when a student opens a lesson or a staff member edits it.</p>
  <div class="service-block">
    <div class="service-header amber">
      <h4>LessonSelector</h4>
      <span>Lesson + content + homework + practice + quiz</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row">
        <span class="method-name">get_lesson_detail(lesson_id, user)</span>
        <span class="method-desc">Returns lesson + all components. Checks enrollment or staff status. Raises <code>PermissionDenied</code> if not enrolled (unless free_preview).</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_lesson_content(lesson_id, user)</span>
        <span class="method-desc">Returns ordered <code>LessonContent</code> items. Enforces enrollment check. Used by UserProgress domain to build the completion checklist.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_lesson_homework(lesson_id, user)</span>
        <span class="method-desc">Returns <code>LessonHomework</code> definition or <code>None</code>. Submissions domain calls this to get deadline_offset_days, max_score, allowed_file_types.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_lesson_practice(lesson_id, user)</span>
        <span class="method-desc">Returns ordered <code>LessonPractice</code> items. Assessment domain calls this to seed attempt context.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_lessons_for_module(module_id, user)</span>
        <span class="method-desc">Ordered lesson list for a module. Excludes soft-deleted. Applies published filter by role.</span>
      </div>
    </div>
  </div>

  <hr>

  <h3 id="sel-enrollment">EnrollmentSelector</h3>
  <p>Enrollment reads used by both the Learning domain itself and by UserProgress/Analytics domains.</p>
  <div class="service-block">
    <div class="service-header sky">
      <h4>EnrollmentSelector</h4>
      <span>Enrollment state reads</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row">
        <span class="method-name">get_enrollment(user_id, course_id)</span>
        <span class="method-desc">Returns single <code>CourseEnrollment</code> or <code>None</code>. Core existence check used by permission guards and other domains.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_enrollments_for_user(user_id, status)</span>
        <span class="method-desc">All enrollments for a student. Optional status filter. Returns with course title + thumbnail for dashboard rendering.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_enrollments_for_course(course_id, status)</span>
        <span class="method-desc">All student enrollments in a course. Used by mentor/admin views. Paginated.</span>
      </div>
      <div class="method-row">
        <span class="method-name">is_enrolled(user_id, course_id)</span>
        <span class="method-desc">Fast boolean check. Returns <code>True</code> only for <code>status=active</code>. Used in permission guards throughout. Cached per request.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_active_enrollment_count(course_id)</span>
        <span class="method-desc">Integer count for course detail display. Cached with short TTL.</span>
      </div>
    </div>
  </div>

  <hr>

  <h3 id="sel-quiz">QuizSelector</h3>
  <p>Quiz structure reads used by the Assessment domain when creating attempts. The Learning domain only defines the quiz; Assessment records attempts.</p>
  <div class="service-block">
    <div class="service-header coral">
      <h4>QuizSelector</h4>
      <span>Quiz definition reads · consumed by Assessment domain</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row">
        <span class="method-name">get_quiz_with_questions(quiz_id)</span>
        <span class="method-desc">Returns <code>LessonQuiz</code> + ordered <code>QuizQuestion</code> list + <code>QuizOption</code> per question. Used by Assessment when seeding an attempt. Options are NOT marked correct — Assessment uses separate read.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_quiz_answer_key(quiz_id)</span>
        <span class="method-desc">Returns <code>QuizOption.is_correct</code> per question. Restricted: Assessment domain only, never exposed to students directly. Permission check required.</span>
      </div>
      <div class="method-row">
        <span class="method-name">get_quiz_config(quiz_id)</span>
        <span class="method-desc">Returns <code>pass_score</code>, <code>max_attempts</code>, <code>time_limit_minutes</code>, <code>shuffle_*</code> flags. Assessment reads these when initialising attempt rules.</span>
      </div>
    </div>
  </div>

</section>

<!-- =================== SERVICES =================== -->
<section id="services">
  <h2>Services — Write Layer <span class="tag">SECTION 3</span></h2>
  <p>Services own all state mutations. Each service encapsulates one aggregate's business rules. <strong>No view or task should write to models directly</strong> — all writes go through a service method. Services emit domain events after successful commits.</p>

  <div class="callout warning">
    <strong>Transaction rule:</strong> Every service method that mutates data runs inside <code>transaction.atomic()</code>. Domain events are dispatched <em>after</em> the transaction commits — never inside it (to avoid consumers reading partially-committed state).
  </div>

  <hr>

  <div id="svc-category" class="service-block">
    <div class="service-header gray">
      <h4>CourseCategoryService</h4>
      <span>Catalog taxonomy management</span>
    </div>
    <div class="service-body">
      <h5>Purpose</h5>
      <p style="margin:0 0 10px">Manages the course category hierarchy. Admin-only. Validates hierarchy depth and slug uniqueness.</p>
      <h5>Methods</h5>
      <div class="method-row"><span class="method-name">create_category(data, actor)</span><span class="method-desc">Creates root or subcategory. Validates: parent exists if given; parent is not itself a subcategory (max depth=2); slug is globally unique.</span></div>
      <div class="method-row"><span class="method-name">update_category(category_id, data, actor)</span><span class="method-desc">Updates name, description, icon, order, is_active. Slug is immutable after creation.</span></div>
      <div class="method-row"><span class="method-name">deactivate_category(category_id, actor)</span><span class="method-desc">Sets <code>is_active=False</code>. Courses keep their <code>category_id</code> — they are not orphaned.</span></div>
      <h5>Business Rules</h5>
      <div class="method-row"><span class="method-name">BR-CAT-01</span><span class="method-desc">Max 2 hierarchy levels. If <code>parent_id</code> is provided, parent must have <code>parent_id=NULL</code>.</span></div>
      <div class="method-row"><span class="method-name">BR-CAT-02</span><span class="method-desc">Slug is immutable once created. Changing it would break URLs and cached references.</span></div>
      <div class="method-row"><span class="method-name">BR-CAT-03</span><span class="method-desc">Deactivating a category with active children deactivates children too.</span></div>
      <h5>Events Produced</h5>
      <div class="method-row"><span class="method-name">CategoryCreated</span><span class="method-desc">category_id, slug, name</span></div>
    </div>
  </div>

  <div id="svc-course" class="service-block">
    <div class="service-header accent">
      <h4>CourseService</h4>
      <span>Course lifecycle · the most critical service in the domain</span>
    </div>
    <div class="service-body">
      <h5>Purpose</h5>
      <p style="margin:0 0 10px">Manages the full Course lifecycle: create → draft → publish → archive → delete. Enforces all invariants on the Course aggregate.</p>
      <h5>Methods</h5>
      <div class="method-row"><span class="method-name">create_course(data, actor)</span><span class="method-desc">Creates draft course. Auto-generates slug from title. Validates: supports_online OR supports_offline must be true.</span></div>
      <div class="method-row"><span class="method-name">update_course(course_id, data, actor)</span><span class="method-desc">Updates metadata. Slug is read-only after publish. Mode flags can be changed only if no active enrollments exist for the affected format.</span></div>
      <div class="method-row"><span class="method-name">publish_course(course_id, actor)</span><span class="method-desc">Transitions <code>draft → published</code>. Validates publish readiness (see BR below). Emits <code>CoursePublished</code>.</span></div>
      <div class="method-row"><span class="method-name">unpublish_course(course_id, actor)</span><span class="method-desc">Transitions <code>published → draft</code>. Blocked if active enrollments exist.</span></div>
      <div class="method-row"><span class="method-name">archive_course(course_id, actor)</span><span class="method-desc">Transitions to <code>archived</code>. No new enrollments possible. Existing students retain access.</span></div>
      <div class="method-row"><span class="method-name">delete_course(course_id, actor)</span><span class="method-desc">Soft-delete. Sets <code>deleted_at</code>. Blocked if any <code>active</code> enrollment exists.</span></div>
      <h5>Business Rules</h5>
      <div class="method-row"><span class="method-name">BR-CRS-01</span><span class="method-desc"><strong>Publish readiness:</strong> Course must have ≥1 published module, each published module must have ≥1 published lesson.</span></div>
      <div class="method-row"><span class="method-name">BR-CRS-02</span><span class="method-desc">Slug is immutable once status is <code>published</code>. Pre-publish it may be updated.</span></div>
      <div class="method-row"><span class="method-name">BR-CRS-03</span><span class="method-desc">Cannot remove <code>supports_offline=True</code> if active offline enrollments exist.</span></div>
      <div class="method-row"><span class="method-name">BR-CRS-04</span><span class="method-desc">Cannot delete a course with any enrollment (regardless of status). Archive instead.</span></div>
      <h5>Events Produced</h5>
      <div class="method-row"><span class="method-name">CourseCreated</span><span class="method-desc">course_id, title, slug, created_by</span></div>
      <div class="method-row"><span class="method-name">CoursePublished</span><span class="method-desc">course_id, title, slug, supports_online, supports_offline</span></div>
      <div class="method-row"><span class="method-name">CourseArchived</span><span class="method-desc">course_id, title</span></div>
    </div>
  </div>

  <div id="svc-module" class="service-block">
    <div class="service-header teal">
      <h4>ModuleService</h4>
      <span>Module lifecycle within a course</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row"><span class="method-name">create_module(course_id, data, actor)</span><span class="method-desc">Creates module. Appends to end of course order by default. Course must not be deleted.</span></div>
      <div class="method-row"><span class="method-name">update_module(module_id, data, actor)</span><span class="method-desc">Updates title, description, estimated_hours, is_published.</span></div>
      <div class="method-row"><span class="method-name">reorder_modules(course_id, ordered_ids, actor)</span><span class="method-desc">Accepts list of module UUIDs in desired order. Validates: all IDs belong to course; no IDs missing. Runs in single transaction using temporary order displacement.</span></div>
      <div class="method-row"><span class="method-name">delete_module(module_id, actor)</span><span class="method-desc">Soft-delete. Cascades visibility (students can no longer see lessons). Does not delete LessonProgress records in UserProgress domain.</span></div>
      <h5>Business Rules</h5>
      <div class="method-row"><span class="method-name">BR-MOD-01</span><span class="method-desc">Cannot publish a module with zero published lessons.</span></div>
      <div class="method-row"><span class="method-name">BR-MOD-02</span><span class="method-desc">Reorder list must contain exactly all non-deleted module IDs for the course — no partial reorders.</span></div>
      <h5>Events Produced</h5>
      <div class="method-row"><span class="method-name">ModuleCreated</span><span class="method-desc">module_id, course_id, title, order</span></div>
      <div class="method-row"><span class="method-name">ModulePublished</span><span class="method-desc">module_id, course_id</span></div>
    </div>
  </div>

  <div id="svc-lesson" class="service-block">
    <div class="service-header amber">
      <h4>LessonService</h4>
      <span>Lesson lifecycle within a module</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row"><span class="method-name">create_lesson(module_id, data, actor)</span><span class="method-desc">Creates lesson at end of module order. Module must exist and not be deleted.</span></div>
      <div class="method-row"><span class="method-name">update_lesson(lesson_id, data, actor)</span><span class="method-desc">Updates title, description, estimated_minutes, is_free_preview.</span></div>
      <div class="method-row"><span class="method-name">publish_lesson(lesson_id, actor)</span><span class="method-desc">Sets <code>is_published=True</code>. Lesson must have ≥1 content item OR ≥1 component (homework/practice/quiz).</span></div>
      <div class="method-row"><span class="method-name">unpublish_lesson(lesson_id, actor)</span><span class="method-desc">Sets <code>is_published=False</code>. Checks if parent module will become empty — if so, unpublishes module and warns.</span></div>
      <div class="method-row"><span class="method-name">reorder_lessons(module_id, ordered_ids, actor)</span><span class="method-desc">Same pattern as ModuleService.reorder_modules. All non-deleted lesson IDs required.</span></div>
      <div class="method-row"><span class="method-name">delete_lesson(lesson_id, actor)</span><span class="method-desc">Soft-delete. Blocked if UserProgress domain has <code>completed</code> records for this lesson (checked via service call). Staff can force-delete.</span></div>
      <h5>Business Rules</h5>
      <div class="method-row"><span class="method-name">BR-LES-01</span><span class="method-desc">Cannot publish an empty lesson (no content and no components).</span></div>
      <div class="method-row"><span class="method-name">BR-LES-02</span><span class="method-desc">Soft-deleting a lesson does not delete UserProgress records — those are preserved for analytics.</span></div>
      <h5>Events Produced</h5>
      <div class="method-row"><span class="method-name">LessonCreated</span><span class="method-desc">lesson_id, module_id, course_id, title</span></div>
      <div class="method-row"><span class="method-name">LessonPublished</span><span class="method-desc">lesson_id, module_id, course_id</span></div>
      <div class="method-row"><span class="method-name">LessonDeleted</span><span class="method-desc">lesson_id, module_id, course_id</span></div>
    </div>
  </div>

  <div id="svc-content" class="service-block">
    <div class="service-header teal">
      <h4>LessonContentService</h4>
      <span>Content items within a lesson</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row"><span class="method-name">add_content(lesson_id, data, actor)</span><span class="method-desc">Appends content item. Validates type-specific required fields (e.g. url required for video; body required for text). Appends to current max order + 1.</span></div>
      <div class="method-row"><span class="method-name">update_content(content_id, data, actor)</span><span class="method-desc">Updates fields. Type is immutable after creation — content must be deleted and re-added to change type.</span></div>
      <div class="method-row"><span class="method-name">reorder_content(lesson_id, ordered_ids, actor)</span><span class="method-desc">Standard reorder pattern.</span></div>
      <div class="method-row"><span class="method-name">delete_content(content_id, actor)</span><span class="method-desc">Hard delete (content items are replaced, not archived). If UserProgress has viewed this item, those records are preserved but the content_id becomes a dangling reference — acceptable.</span></div>
      <h5>Business Rules</h5>
      <div class="method-row"><span class="method-name">BR-CNT-01</span><span class="method-desc">At least one of <code>url</code> or <code>body</code> must be present. Enforced at service + DB level.</span></div>
      <div class="method-row"><span class="method-name">BR-CNT-02</span><span class="method-desc">Content type is immutable after creation.</span></div>
    </div>
  </div>

  <div id="svc-homework" class="service-block">
    <div class="service-header amber">
      <h4>LessonHomeworkService</h4>
      <span>1:1 homework definition per lesson</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row"><span class="method-name">set_homework(lesson_id, data, actor)</span><span class="method-desc">Creates or replaces homework definition. Upsert pattern — if homework exists, update it; if not, create it.</span></div>
      <div class="method-row"><span class="method-name">remove_homework(lesson_id, actor)</span><span class="method-desc">Hard-deletes homework definition. Blocked if Submissions domain has any submission against this homework_id. Returns error with submission count.</span></div>
      <h5>Business Rules</h5>
      <div class="method-row"><span class="method-name">BR-HW-01</span><span class="method-desc">Only one homework per lesson. Enforced at DB (UNIQUE) and service layer.</span></div>
      <div class="method-row"><span class="method-name">BR-HW-02</span><span class="method-desc">Cannot remove homework with existing student submissions. Submissions domain must be consulted.</span></div>
    </div>
  </div>

  <div id="svc-practice" class="service-block">
    <div class="service-header amber">
      <h4>LessonPracticeService</h4>
      <span>Ordered practice exercises within a lesson</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row"><span class="method-name">add_practice(lesson_id, data, actor)</span><span class="method-desc">Appends practice item. Validates type (coding/written/interactive) and required fields per type.</span></div>
      <div class="method-row"><span class="method-name">update_practice(practice_id, data, actor)</span><span class="method-desc">Updates instructions, hints, max_score, time_limit_minutes. Type is immutable.</span></div>
      <div class="method-row"><span class="method-name">reorder_practice(lesson_id, ordered_ids, actor)</span><span class="method-desc">Standard reorder pattern.</span></div>
      <div class="method-row"><span class="method-name">delete_practice(practice_id, actor)</span><span class="method-desc">Hard delete. Blocked if Assessment domain has attempts against this practice_id.</span></div>
    </div>
  </div>

  <div id="svc-quiz" class="service-block">
    <div class="service-header coral">
      <h4>LessonQuizService</h4>
      <span>Quiz definition: settings, questions, options</span>
    </div>
    <div class="service-body">
      <h5>Methods</h5>
      <div class="method-row"><span class="method-name">create_quiz(lesson_id, data, actor)</span><span class="method-desc">Creates quiz for lesson. Blocked if quiz already exists (1:1 enforced).</span></div>
      <div class="method-row"><span class="method-name">update_quiz_settings(quiz_id, data, actor)</span><span class="method-desc">Updates pass_score, max_attempts, time_limit, shuffle flags, show_correct_after_attempt.</span></div>
      <div class="method-row"><span class="method-name">add_question(quiz_id, data, actor)</span><span class="method-desc">Appends question. Validates type. For single_choice, at least one correct option required. For short_text, no options needed.</span></div>
      <div class="method-row"><span class="method-name">update_question(question_id, data, actor)</span><span class="method-desc">Updates body, explanation, points. Type is immutable after creation.</span></div>
      <div class="method-row"><span class="method-name">reorder_questions(quiz_id, ordered_ids, actor)</span><span class="method-desc">Standard reorder pattern.</span></div>
      <div class="method-row"><span class="method-name">add_option(question_id, data, actor)</span><span class="method-desc">Adds answer option. Validates: for single_choice, only one option may be marked correct.</span></div>
      <div class="method-row"><span class="method-name">delete_quiz(quiz_id, actor)</span><span class="method-desc">Hard-deletes quiz + questions + options. Blocked if Assessment domain has attempts. Staff can force-delete.</span></div>
      <h5>Business Rules</h5>
      <div class="method-row"><span class="method-name">BR-QZ-01</span><span class="method-desc"><code>pass_score</code> must be 0–100 inclusive.</span></div>
      <div class="method-row"><span class="method-name">BR-QZ-02</span><span class="method-desc"><code>single_choice</code> question must have exactly one correct option.</span></div>
      <div class="method-row"><span class="method-name">BR-QZ-03</span><span class="method-desc"><code>multiple_choice</code> question must have ≥2 options with ≥1 correct.</span></div>
      <div class="method-row"><span class="method-name">BR-QZ-04</span><span class="method-desc">Question type is immutable — delete and recreate if type change needed.</span></div>
      <h5>Events Produced</h5>
      <div class="method-row"><span class="method-name">QuizCreated</span><span class="method-desc">quiz_id, lesson_id, course_id</span></div>
    </div>
  </div>

  <div id="svc-enrollment" class="service-block">
    <div class="service-header sky">
      <h4>CourseEnrollmentService</h4>
      <span>Enrollment lifecycle — the cross-domain write boundary</span>
    </div>
    <div class="service-body">
      <h5>Purpose</h5>
      <p style="margin:0 0 10px">Manages enrollment creation, status transitions, and delivery format. This service is called by students (self-enroll), admins (bulk enroll), and the future Mentorship domain (offline group enroll).</p>
      <h5>Methods</h5>
      <div class="method-row"><span class="method-name">enroll_student(user_id, course_id, delivery_format, actor)</span><span class="method-desc">Creates <code>CourseEnrollment</code>. Validates course is published; validates delivery_format against course.supports_*; checks no duplicate enrollment exists.</span></div>
      <div class="method-row"><span class="method-name">drop_enrollment(enrollment_id, actor)</span><span class="method-desc">Sets <code>status=dropped</code>, stamps <code>dropped_at</code>. Actor must be the student or staff.</span></div>
      <div class="method-row"><span class="method-name">complete_enrollment(enrollment_id, actor)</span><span class="method-desc">Sets <code>status=completed</code>, stamps <code>completed_at</code>. Called by UserProgress domain when all module assessments pass. Actor must be system or staff.</span></div>
      <div class="method-row"><span class="method-name">change_delivery_format(enrollment_id, new_format, actor)</span><span class="method-desc">Changes online↔offline. Restricted to staff/admin. Validates new format is supported by course. Emits <code>EnrollmentDeliveryFormatChanged</code>.</span></div>
      <h5>Business Rules</h5>
      <div class="method-row"><span class="method-name">BR-ENR-01</span><span class="method-desc">Cannot enroll in a draft or archived course.</span></div>
      <div class="method-row"><span class="method-name">BR-ENR-02</span><span class="method-desc">Cannot enroll with <code>delivery_format=offline</code> if <code>course.supports_offline=False</code>.</span></div>
      <div class="method-row"><span class="method-name">BR-ENR-03</span><span class="method-desc">Duplicate enrollment (same user+course) is rejected. Return existing enrollment if status=dropped.</span></div>
      <div class="method-row"><span class="method-name">BR-ENR-04</span><span class="method-desc">Only <code>active</code> enrollment can be completed or dropped. Already-completed enrollments are immutable.</span></div>
      <h5>Events Produced</h5>
      <div class="method-row"><span class="method-name">StudentEnrolled</span><span class="method-desc">enrollment_id, user_id, course_id, delivery_format, enrolled_at</span></div>
      <div class="method-row"><span class="method-name">EnrollmentDropped</span><span class="method-desc">enrollment_id, user_id, course_id, dropped_at</span></div>
      <div class="method-row"><span class="method-name">EnrollmentCompleted</span><span class="method-desc">enrollment_id, user_id, course_id, completed_at</span></div>
    </div>
  </div>

</section>

<!-- =================== API CONTRACTS =================== -->
<section id="api">
  <h2>API Contracts <span class="tag">SECTION 4</span></h2>
  <p>All endpoints use JSON. Auth via Bearer token (JWT). Pagination uses <code>{ count, next, previous, results }</code>. Errors use <code>{ error, code, detail }</code>. UUIDs in all ID fields.</p>

  <div class="callout sky">
    <strong>URL namespace:</strong> All Learning Domain endpoints live under <code>/api/v1/</code>. The prefix <code>learning/</code> is used in this document for clarity but may be omitted in the final router if there is no namespace collision.
  </div>

  <!-- CATALOG -->
  <h3 id="api-catalog">Catalog Endpoints</h3>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-get">GET</span>
      <span class="endpoint-path">/learning/courses/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Public · UC-01 UC-02 UC-03 UC-07</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Query Params</h6>
        <pre>category_slug: string (optional)
delivery_format: online|offline (optional)
language: string (optional)
search: string (optional)
page: int (default 1)
page_size: int (default 20, max 100)</pre>
      </div>
      <div class="endpoint-col">
        <h6>Response 200</h6>
        <pre>{ count, next, previous,
  results: [{
    id, title, slug,
    short_description,
    thumbnail_url,
    category: { id, name, slug },
    supports_online, supports_offline,
    estimated_weeks, language,
    module_count, enrolled_count
  }]
}</pre>
      </div>
    </div>
    <div style="padding:0 16px 12px;font-size:12px;color:var(--text-muted)"><strong>Permissions:</strong> Public (no auth required)</div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-get">GET</span>
      <span class="endpoint-path">/learning/courses/{slug}/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Public · UC-04 UC-10</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Path Params</h6>
        <pre>slug: string</pre>
        <h6>Notes</h6>
        <pre>Staff see draft content.
Students see published only.
Unauthenticated: published only.</pre>
      </div>
      <div class="endpoint-col">
        <h6>Response 200</h6>
        <pre>{ id, title, slug, description,
  short_description, thumbnail_url,
  status, supports_online, supports_offline,
  language, estimated_weeks, is_sequential,
  category: { id, name, slug },
  created_by: { id, full_name },
  modules: [{
    id, title, description, order,
    is_published, estimated_hours,
    lesson_count
  }]
}</pre>
      </div>
    </div>
    <div style="padding:0 16px 12px;font-size:12px;color:var(--text-muted)"><strong>Permissions:</strong> Public for published. Staff/Admin see drafts.</div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-get">GET</span>
      <span class="endpoint-path">/learning/categories/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Public · UC-06</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Response 200</h6>
        <pre>[{ id, name, slug, description,
   icon, order, course_count,
   children: [{ id, name, slug,
     icon, order, course_count }]
}]</pre>
      </div>
      <div class="endpoint-col">
        <h6>Notes</h6>
        <pre>Returns active categories only.
Nested children in response.
No pagination (expected &lt; 50 categories).
Cacheable (TTL: 5 min).</pre>
      </div>
    </div>
  </div>

  <!-- COURSE MANAGEMENT -->
  <h3 id="api-course-mgmt">Course Management</h3>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/courses/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Staff/Admin · UC-16</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Request Body</h6>
        <pre>{ title: string (required),
  description: string,
  short_description: string,
  thumbnail_url: string,
  category_id: uuid,
  supports_online: bool (default true),
  supports_offline: bool (default false),
  language: string (default "ru"),
  estimated_weeks: int,
  is_sequential: bool (default true)
}</pre>
      </div>
      <div class="endpoint-col">
        <h6>Response 201</h6>
        <pre>{ id, title, slug, status: "draft",
  supports_online, supports_offline,
  created_at, created_by: { id, full_name }
}</pre>
        <h6>Errors</h6>
        <pre>400: neither supports_online nor
     supports_offline is true
400: category_id not found</pre>
      </div>
    </div>
    <div style="padding:0 16px 12px;font-size:12px;color:var(--text-muted)"><strong>Permissions:</strong> Staff, Admin</div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-patch">PATCH</span>
      <span class="endpoint-path">/learning/courses/{id}/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Staff/Admin · UC-17</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Request Body (partial)</h6>
        <pre>{ title, description,
  short_description, thumbnail_url,
  category_id, supports_online,
  supports_offline, language,
  estimated_weeks, is_sequential }</pre>
      </div>
      <div class="endpoint-col">
        <h6>Notes</h6>
        <pre>slug: immutable once published.
supports_offline: cannot set to false
  if active offline enrollments exist.
Response: full course object.</pre>
      </div>
    </div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/courses/{id}/publish/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Staff/Admin · UC-18</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col"><h6>Request Body</h6><pre>{ } (empty)</pre></div>
      <div class="endpoint-col">
        <h6>Response 200 / Errors</h6>
        <pre>200: { id, status: "published", ... }
400: { code: "publish_not_ready",
  detail: "Course has no published modules" }
400: { code: "publish_not_ready",
  detail: "Module X has no published lessons" }</pre>
      </div>
    </div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/courses/{id}/archive/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Admin · UC-19</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col"><h6>Request Body</h6><pre>{ } (empty)</pre></div>
      <div class="endpoint-col"><h6>Response 200</h6><pre>{ id, status: "archived" }</pre></div>
    </div>
    <div style="padding:0 16px 12px;font-size:12px;color:var(--text-muted)"><strong>Permissions:</strong> Admin only</div>
  </div>

  <!-- COURSE STRUCTURE -->
  <h3 id="api-structure">Course Structure (Modules &amp; Lessons)</h3>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/courses/{course_id}/modules/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Staff/Admin · UC-21</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Request Body</h6>
        <pre>{ title: string (required),
  description: string,
  estimated_hours: int }</pre>
      </div>
      <div class="endpoint-col">
        <h6>Response 201</h6>
        <pre>{ id, title, description, order,
  is_published: false,
  estimated_hours, created_at }</pre>
      </div>
    </div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/courses/{course_id}/modules/reorder/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Staff/Admin · UC-24</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col"><h6>Request Body</h6><pre>{ ordered_ids: [uuid, uuid, ...] }</pre></div>
      <div class="endpoint-col"><h6>Response 200 / Errors</h6><pre>200: [{ id, order }, ...]
400: "ordered_ids must include all
  non-deleted modules for this course"</pre></div>
    </div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/modules/{module_id}/lessons/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Staff/Admin · UC-26</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Request Body</h6>
        <pre>{ title: string (required),
  description: string,
  estimated_minutes: int,
  is_free_preview: bool (default false) }</pre>
      </div>
      <div class="endpoint-col">
        <h6>Response 201</h6>
        <pre>{ id, title, description, order,
  is_published: false,
  is_free_preview, estimated_minutes }</pre>
      </div>
    </div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-get">GET</span>
      <span class="endpoint-path">/learning/modules/{module_id}/lessons/{lesson_id}/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Enrolled Student / Staff · UC-11</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Response 200</h6>
        <pre>{ id, title, description, order,
  is_published, is_free_preview,
  estimated_minutes,
  content: [{ id, type, title,
    url, body, order, duration_seconds,
    is_required, is_downloadable,
    metadata }],
  homework: { id, title, description,
    max_score, deadline_offset_days,
    submission_type } | null,
  practice: [{ id, title, type,
    instructions, order }],
  quiz: { id, title, pass_score,
    max_attempts, time_limit_minutes,
    question_count } | null
}</pre>
      </div>
      <div class="endpoint-col">
        <h6>Notes</h6>
        <pre>Quiz questions NOT included here.
QuizSelector.get_quiz_with_questions
is called by Assessment domain only.

is_correct NOT exposed to students.

Unauthenticated may view if
is_free_preview = true.</pre>
      </div>
    </div>
    <div style="padding:0 16px 12px;font-size:12px;color:var(--text-muted)"><strong>Permissions:</strong> Enrolled student, Staff, Admin. Unauthenticated if <code>is_free_preview=true</code>.</div>
  </div>

  <!-- LESSON COMPONENTS -->
  <h3 id="api-lesson">Lesson Components</h3>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/lessons/{lesson_id}/content/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Staff/Admin · UC-31</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Request Body</h6>
        <pre>{ type: video|pdf|slides|text|
        link|recording|code (required),
  title: string (required),
  description: string,
  url: string (required for video/
    pdf/slides/link/recording),
  body: string (required for text/code),
  duration_seconds: int,
  file_size_bytes: int,
  is_required: bool (default true),
  is_downloadable: bool,
  metadata: object }</pre>
      </div>
      <div class="endpoint-col">
        <h6>Response 201 / Errors</h6>
        <pre>201: { id, type, title, order, ... }

400: { code: "missing_url",
  detail: "url required for type=video" }
400: { code: "missing_body",
  detail: "body required for type=text" }</pre>
      </div>
    </div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/lessons/{lesson_id}/quiz/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Staff/Admin · UC-42</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Request Body</h6>
        <pre>{ title: string (required),
  instructions: string,
  time_limit_minutes: int,
  pass_score: int (0-100, default 70),
  max_attempts: int | null,
  shuffle_questions: bool,
  shuffle_options: bool,
  show_correct_after_attempt: bool }</pre>
      </div>
      <div class="endpoint-col">
        <h6>Response 201 / Errors</h6>
        <pre>201: { id, title, pass_score, ... }

409: { code: "quiz_exists",
  detail: "Lesson already has a quiz.
  Update it via PATCH /quiz/{id}/" }</pre>
      </div>
    </div>
  </div>

  <!-- ENROLLMENT -->
  <h3 id="api-enrollment">Enrollment</h3>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/enrollments/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Student / Admin · UC-08 UC-52</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col">
        <h6>Request Body</h6>
        <pre>{ course_id: uuid (required),
  delivery_format: online|offline
    (required),
  user_id: uuid (admin-only field;
    omit for self-enrollment) }</pre>
      </div>
      <div class="endpoint-col">
        <h6>Response 201 / Errors</h6>
        <pre>201: { id, course_id, user_id,
  delivery_format, status: "active",
  enrolled_at }

400: "Course does not support offline"
400: "Course is not published"
409: "Student already enrolled"</pre>
      </div>
    </div>
    <div style="padding:0 16px 12px;font-size:12px;color:var(--text-muted)"><strong>Permissions:</strong> Authenticated student (self-enroll), Admin (any user)</div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-get">GET</span>
      <span class="endpoint-path">/learning/enrollments/me/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Student · UC-09</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col"><h6>Query Params</h6><pre>status: active|completed|dropped (optional)</pre></div>
      <div class="endpoint-col">
        <h6>Response 200</h6>
        <pre>{ results: [{
  id, delivery_format, status,
  enrolled_at, completed_at,
  course: { id, title, slug,
    thumbnail_url, module_count }
}] }</pre>
      </div>
    </div>
  </div>

  <div class="endpoint-block">
    <div class="endpoint-header">
      <span class="badge badge-post">POST</span>
      <span class="endpoint-path">/learning/enrollments/{id}/drop/</span>
      <span style="margin-left:auto;font-size:12px;color:var(--text-muted)">Student / Admin · UC-15</span>
    </div>
    <div class="endpoint-body">
      <div class="endpoint-col"><h6>Request Body</h6><pre>{ } (empty)</pre></div>
      <div class="endpoint-col"><h6>Response 200 / Errors</h6><pre>200: { id, status: "dropped", dropped_at }
400: "Enrollment already completed"</pre></div>
    </div>
  </div>

</section>

<!-- =================== PERMISSIONS =================== -->
<section id="permissions">
  <h2>Permissions Matrix <span class="tag">SECTION 5</span></h2>
  <p>Roles: <strong>Student</strong> — enrolled learner. <strong>Mentor</strong> — leads offline groups, reviews homework. <strong>Staff</strong> — course authors, can create and edit but not archive. <strong>Admin</strong> — full access.</p>

  <div class="callout warning">
    <strong>OWN</strong> = only for courses/content the user created. Mentors have read-only access to enrolled students' course structure; they cannot author courses.
  </div>

  <table class="perm-table">
    <thead>
      <tr>
        <th style="min-width:220px">Action</th>
        <th>Student</th>
        <th>Mentor</th>
        <th>Staff</th>
        <th>Admin</th>
      </tr>
    </thead>
    <tbody>
      <tr><td colspan="5" style="background:var(--accent-light);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--accent)">Catalog</td></tr>
      <tr><td>List published courses</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td></tr>
      <tr><td>View published course detail</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td></tr>
      <tr><td>View free-preview lesson</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td></tr>
      <tr><td>View draft / unpublished course</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>View unpublished lesson content</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>

      <tr><td colspan="5" style="background:var(--sky-light);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--sky)">Enrollment</td></tr>
      <tr><td>Enroll self in course (online)</td><td class="perm-yes">✓</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>Enroll self in course (offline)</td><td class="perm-yes">✓</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>Enroll any student (admin)</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>Drop own enrollment</td><td class="perm-yes">✓</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>Force-drop student enrollment</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>Change delivery format</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>View all enrollments for course</td><td class="perm-no">—</td><td class="perm-review">📋 own groups</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td></tr>

      <tr><td colspan="5" style="background:var(--teal-light);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--teal)">Course Authoring</td></tr>
      <tr><td>Create course</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td><td class="perm-yes">✓</td></tr>
      <tr><td>Edit course metadata</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Publish course</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Unpublish course</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Archive course</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>Delete course (soft)</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>

      <tr><td colspan="5" style="background:var(--amber-light);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--amber)">Module &amp; Lesson Authoring</td></tr>
      <tr><td>Create / edit module</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Publish / unpublish module</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Reorder modules</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Create / edit lesson</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Publish / unpublish lesson</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Reorder lessons</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Delete module / lesson</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>

      <tr><td colspan="5" style="background:var(--coral-light);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--coral)">Content &amp; Quiz Authoring</td></tr>
      <tr><td>Add / edit / reorder content</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Delete content item</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Set / edit homework definition</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Remove homework definition</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>Add / edit / delete practice</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Create / edit quiz + questions</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
      <tr><td>Delete quiz</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>

      <tr><td colspan="5" style="background:var(--gray-light);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--gray)">Admin</td></tr>
      <tr><td>Create / edit category</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>Deactivate category</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-yes">✓</td></tr>
      <tr><td>View quiz answer key</td><td class="perm-no">—</td><td class="perm-no">—</td><td class="perm-own">OWN</td><td class="perm-yes">✓</td></tr>
    </tbody>
  </table>

  <div class="callout success" style="margin-top:16px">
    <strong>OWN scope resolution:</strong> "OWN" checks <code>course.created_by == request.user</code>. In future, when co-authoring (<code>CourseAuthor</code> junction) is added, OWN expands to "member of course author list." No permission code changes — just the predicate function.
  </div>
</section>

<!-- =================== DOMAIN EVENTS =================== -->
<section id="events">
  <h2>Domain Events <span class="tag">SECTION 6</span></h2>
  <p>Events are dispatched after successful DB commits. In the monolith, Django signals serve as the event bus. In a future service architecture, these map 1:1 to message queue topics. Each event payload is designed to be self-contained — consumers never need to query back into the Learning domain to process the event.</p>

  <div class="callout">
    <strong>Naming convention:</strong> <code>[Entity][PastTense]</code>. All events carry <code>occurred_at: TIMESTAMPTZ</code> and <code>actor_id: UUID</code> (who triggered the action).
  </div>

  <h3>Enrollment Events</h3>

  <div class="event-block">
    <div class="event-header sky">
      <h4>StudentEnrolled</h4>
      <span>Produced by: CourseEnrollmentService.enroll_student</span>
    </div>
    <div class="event-body">
      <div class="event-col">
        <h6>Payload</h6>
        <pre style="font-size:11.5px;margin:0">enrollment_id: UUID
user_id: UUID
course_id: UUID
course_title: str
delivery_format: str
enrolled_at: TIMESTAMPTZ
enrolled_by_id: UUID | null</pre>
      </div>
      <div class="event-col">
        <h6>Consumers</h6>
        <ul>
          <li>UserProgress — initialise progress record for the course</li>
          <li>Notifications — send welcome / enrollment confirmation</li>
          <li>Analytics — update enrollment metrics</li>
          <li>Mentorship — if offline, trigger group assignment flow</li>
        </ul>
      </div>
      <div class="event-col">
        <h6>Criticality</h6>
        <p style="font-size:12px;color:var(--text-muted)">HIGH — UserProgress must receive this to initialise student state. If missed, student cannot track progress.</p>
      </div>
    </div>
  </div>

  <div class="event-block">
    <div class="event-header sky">
      <h4>EnrollmentDropped</h4>
      <span>Produced by: CourseEnrollmentService.drop_enrollment</span>
    </div>
    <div class="event-body">
      <div class="event-col">
        <h6>Payload</h6>
        <pre style="font-size:11.5px;margin:0">enrollment_id: UUID
user_id: UUID
course_id: UUID
dropped_at: TIMESTAMPTZ
dropped_by_id: UUID</pre>
      </div>
      <div class="event-col">
        <h6>Consumers</h6>
        <ul>
          <li>UserProgress — mark progress as inactive</li>
          <li>Notifications — send drop confirmation</li>
          <li>Mentorship — remove from offline group if assigned</li>
          <li>Analytics — update churn metrics</li>
        </ul>
      </div>
      <div class="event-col">
        <h6>Criticality</h6>
        <p style="font-size:12px;color:var(--text-muted)">MEDIUM — Analytics and Mentorship may handle async. UserProgress should deactivate synchronously.</p>
      </div>
    </div>
  </div>

  <div class="event-block">
    <div class="event-header sky">
      <h4>EnrollmentCompleted</h4>
      <span>Produced by: CourseEnrollmentService.complete_enrollment</span>
    </div>
    <div class="event-body">
      <div class="event-col">
        <h6>Payload</h6>
        <pre style="font-size:11.5px;margin:0">enrollment_id: UUID
user_id: UUID
course_id: UUID
completed_at: TIMESTAMPTZ</pre>
      </div>
      <div class="event-col">
        <h6>Consumers</h6>
        <ul>
          <li>Certification — trigger certificate generation</li>
          <li>Notifications — send completion congratulations</li>
          <li>Analytics — update completion rate</li>
        </ul>
      </div>
      <div class="event-col">
        <h6>Criticality</h6>
        <p style="font-size:12px;color:var(--text-muted)">HIGH — Certification domain listens to this event. If missed, certificate is not issued.</p>
      </div>
    </div>
  </div>

  <h3>Course Lifecycle Events</h3>

  <div class="event-block">
    <div class="event-header accent">
      <h4>CoursePublished</h4>
      <span>Produced by: CourseService.publish_course</span>
    </div>
    <div class="event-body">
      <div class="event-col">
        <h6>Payload</h6>
        <pre style="font-size:11.5px;margin:0">course_id: UUID
title: str
slug: str
category_id: UUID | null
supports_online: bool
supports_offline: bool
language: str
published_at: TIMESTAMPTZ
published_by_id: UUID</pre>
      </div>
      <div class="event-col">
        <h6>Consumers</h6>
        <ul>
          <li>Search index — index course for discovery</li>
          <li>Notifications — alert staff/students who saved course</li>
          <li>Analytics — add to published course metrics</li>
        </ul>
      </div>
      <div class="event-col">
        <h6>Criticality</h6>
        <p style="font-size:12px;color:var(--text-muted)">MEDIUM — Search indexing can be async. Course is live regardless of search index state.</p>
      </div>
    </div>
  </div>

  <div class="event-block">
    <div class="event-header gray">
      <h4>CourseArchived</h4>
      <span>Produced by: CourseService.archive_course</span>
    </div>
    <div class="event-body">
      <div class="event-col">
        <h6>Payload</h6>
        <pre style="font-size:11.5px;margin:0">course_id: UUID
title: str
archived_at: TIMESTAMPTZ
archived_by_id: UUID</pre>
      </div>
      <div class="event-col">
        <h6>Consumers</h6>
        <ul>
          <li>Search index — remove from discovery</li>
          <li>Notifications — notify enrolled students</li>
        </ul>
      </div>
      <div class="event-col">
        <h6>Criticality</h6>
        <p style="font-size:12px;color:var(--text-muted)">LOW — Enrolled students retain access. Notification is advisory.</p>
      </div>
    </div>
  </div>

  <h3>Content Events</h3>

  <div class="event-block">
    <div class="event-header teal">
      <h4>LessonPublished</h4>
      <span>Produced by: LessonService.publish_lesson</span>
    </div>
    <div class="event-body">
      <div class="event-col">
        <h6>Payload</h6>
        <pre style="font-size:11.5px;margin:0">lesson_id: UUID
module_id: UUID
course_id: UUID
title: str
order: int
published_at: TIMESTAMPTZ</pre>
      </div>
      <div class="event-col">
        <h6>Consumers</h6>
        <ul>
          <li>UserProgress — unlock lesson for enrolled students if sequential rules allow</li>
          <li>Notifications — alert enrolled students of new lesson</li>
        </ul>
      </div>
      <div class="event-col">
        <h6>Criticality</h6>
        <p style="font-size:12px;color:var(--text-muted)">MEDIUM — UserProgress must know about new lessons to track completion correctly.</p>
      </div>
    </div>
  </div>

  <div class="event-block">
    <div class="event-header amber">
      <h4>LessonDeleted</h4>
      <span>Produced by: LessonService.delete_lesson</span>
    </div>
    <div class="event-body">
      <div class="event-col">
        <h6>Payload</h6>
        <pre style="font-size:11.5px;margin:0">lesson_id: UUID
module_id: UUID
course_id: UUID
deleted_at: TIMESTAMPTZ</pre>
      </div>
      <div class="event-col">
        <h6>Consumers</h6>
        <ul>
          <li>UserProgress — mark existing progress entries as stale</li>
          <li>Submissions — orphan check on homework submissions</li>
          <li>Assessment — orphan check on quiz/practice attempts</li>
        </ul>
      </div>
      <div class="event-col">
        <h6>Criticality</h6>
        <p style="font-size:12px;color:var(--text-muted)">HIGH — Other domains must handle stale references. Blocked by BR-LES-02 if completed progress exists without staff override.</p>
      </div>
    </div>
  </div>

  <div class="event-block">
    <div class="event-header coral">
      <h4>QuizCreated</h4>
      <span>Produced by: LessonQuizService.create_quiz</span>
    </div>
    <div class="event-body">
      <div class="event-col">
        <h6>Payload</h6>
        <pre style="font-size:11.5px;margin:0">quiz_id: UUID
lesson_id: UUID
course_id: UUID
pass_score: int
max_attempts: int | null</pre>
      </div>
      <div class="event-col">
        <h6>Consumers</h6>
        <ul>
          <li>Assessment — register quiz as available for attempts</li>
          <li>UserProgress — note that lesson now has a quiz component</li>
        </ul>
      </div>
      <div class="event-col">
        <h6>Criticality</h6>
        <p style="font-size:12px;color:var(--text-muted)">LOW — Assessment discovers quizzes on-demand via QuizSelector. Event is advisory.</p>
      </div>
    </div>
  </div>

</section>

<!-- =================== DEPENDENCIES =================== -->
<section id="dependencies">
  <h2>UserProgress Domain Dependencies <span class="tag">SECTION 7</span></h2>
  <p>Before designing the UserProgress domain, these questions must be answered. They are not optional assumptions — each one changes the data model, the event contracts, or both.</p>

  <div class="callout coral">
    <strong>Blocking decisions</strong> must be resolved before any UserProgress table is designed. Advisory decisions can be deferred to the first implementation sprint but should be decided before writing service code.
  </div>

  <div class="dep-grid">

    <div class="dep-card blocking">
      <h4>🔴 What is the unit of progress?</h4>
      <p>Does the student complete a <strong>Lesson</strong> as a whole, or are individual <strong>LessonContent items</strong> tracked? If content-level: <code>LessonContentProgress(enrollment_id, content_id, viewed_at)</code>. If lesson-level: <code>LessonProgress(enrollment_id, lesson_id, status)</code>. This determines the primary key structure of the entire UserProgress domain and what <code>LessonContent.is_required</code> means at runtime.</p>
    </div>

    <div class="dep-card blocking">
      <h4>🔴 What unlocks the next lesson?</h4>
      <p>Options: (A) Student views all <code>is_required</code> content items → auto-unlock. (B) Student submits homework → unlock after mentor approval. (C) Student passes lesson quiz → auto-unlock. (D) Mentor manually unlocks. This decision defines whether <code>LessonHomework</code> and <code>LessonQuiz</code> are gates or just activities. If (B) or (C): UserProgress needs to listen to Submissions and Assessment events respectively.</p>
    </div>

    <div class="dep-card blocking">
      <h4>🔴 What unlocks the next module?</h4>
      <p>Is it: (A) All lessons in the module completed? (B) A separate end-of-module assessment passed? (C) Both? Currently the design brief says "module assessment" but that lives in the Assessment domain. UserProgress must know whether to wait for an <code>AssessmentPassed</code> event or compute completion from lesson states alone.</p>
    </div>

    <div class="dep-card blocking">
      <h4>🔴 Does online progress === offline progress?</h4>
      <p>Online students self-pace through lessons. Offline students attend scheduled sessions. Does a student's <code>LessonProgress</code> get set by (A) the student opening the lesson, or (B) the mentor marking attendance for a session that covered that lesson? If (B), UserProgress depends on an <code>AttendanceMarked</code> event from the Mentorship domain. These are two fundamentally different progress architectures.</p>
    </div>

    <div class="dep-card advisory">
      <h4>🟡 Can a student reset progress?</h4>
      <p>If a student re-enrolls (was dropped, then re-enrolled), does previous progress carry over or reset? This affects whether <code>LessonProgress</code> is keyed by <code>enrollment_id</code> (reset on re-enroll) or <code>user_id + lesson_id</code> (persists across enrollments). The <code>CourseEnrollmentService</code> handles the re-enrollment scenario (BR-ENR-03) but does not yet define what happens to prior progress.</p>
    </div>

    <div class="dep-card advisory">
      <h4>🟡 Who triggers EnrollmentCompleted?</h4>
      <p>The Learning Domain's <code>CourseEnrollmentService.complete_enrollment</code> exists, but who calls it? UserProgress (when all modules pass)? Assessment (when final exam passes)? This needs a defined orchestrator. Recommendation: UserProgress domain owns course completion logic and calls <code>CourseEnrollmentService.complete_enrollment</code> as an internal service call. But this must be confirmed before UserProgress is designed.</p>
    </div>

    <div class="dep-card design">
      <h4>🔵 Progress granularity for Analytics</h4>
      <p>Analytics domain will want time-series data: when did the student start each lesson? How long did they spend? Are these timestamps stored in UserProgress, or does Analytics maintain its own event log? Decide whether UserProgress is the system of record for timing data or just for completion state. This affects how many columns are on <code>LessonProgress</code>.</p>
    </div>

    <div class="dep-card design">
      <h4>🔵 Handling deleted lessons in active courses</h4>
      <p>If a staff member soft-deletes a lesson that an enrolled student has already completed, what happens to their progress? Options: (A) Progress records preserved, lesson shown as "removed" in UI. (B) Lesson deleted + progress records deleted, completion percentage recalculated. The <code>LessonDeleted</code> event is already defined — UserProgress must declare its handler strategy before its schema is finalised.</p>
    </div>

  </div>

  <div class="callout success" style="margin-top:24px">
    <strong>What the Learning Domain already provides to UserProgress:</strong>
    <br><br>
    ✓ <code>StudentEnrolled</code> event — UserProgress initialises on this<br>
    ✓ <code>LessonPublished</code> event — new lesson becomes trackable<br>
    ✓ <code>LessonDeleted</code> event — UserProgress must handle stale references<br>
    ✓ <code>EnrollmentDropped</code> event — UserProgress deactivates on this<br>
    ✓ <code>EnrollmentSelector.is_enrolled()</code> — UserProgress uses this as a gate check<br>
    ✓ <code>LessonSelector.get_lesson_content()</code> — source of truth for what must be completed<br>
    ✓ <code>CourseEnrollmentService.complete_enrollment()</code> — UserProgress calls this when done<br>
    ✓ <code>Course.is_sequential</code> — UserProgress reads this to decide unlock order
  </div>
</section>

</main>
</div>
</body>
</html>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LearnFlow — Learning Domain Design v2.0</title>
<style>
  :root {
    --accent: #534AB7;
    --accent-light: #EEEDFE;
    --accent-mid: #AFA9EC;
    --teal: #0F6E56;
    --teal-light: #E1F5EE;
    --coral: #993C1D;
    --coral-light: #FAECE7;
    --amber: #854F0B;
    --amber-light: #FAEEDA;
    --sky: #0C5E8A;
    --sky-light: #E0F2FE;
    --gray: #444441;
    --gray-light: #F1EFE8;
    --text: #1a1a18;
    --text-muted: #5F5E5A;
    --border: #D3D1C7;
    --bg: #ffffff;
    --bg-page: #f7f6f2;
    --code-bg: #F1EFE8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, 'Segoe UI', Arial, sans-serif;
    font-size: 15px;
    line-height: 1.7;
    color: var(--text);
    background: var(--bg-page);
  }
  .layout { display: flex; min-height: 100vh; }

  nav {
    width: 264px;
    min-width: 264px;
    background: var(--bg);
    border-right: 1px solid var(--border);
    padding: 24px 0;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
  }
  nav .logo { padding: 0 20px 20px; border-bottom: 1px solid var(--border); margin-bottom: 12px; }
  nav .logo h1 { font-size: 15px; font-weight: 600; color: var(--accent); }
  nav .logo p { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
  nav a {
    display: block; padding: 7px 20px; font-size: 13px;
    color: var(--text-muted); text-decoration: none;
    border-left: 2px solid transparent; transition: all 0.15s;
  }
  nav a:hover { color: var(--accent); background: var(--accent-light); border-left-color: var(--accent); }
  nav .section-label {
    padding: 14px 20px 4px; font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted);
  }
  nav a.sub { padding-left: 32px; font-size: 12px; }

  main { flex: 1; padding: 48px 56px; max-width: 980px; }
  section { margin-bottom: 64px; }

  h2 {
    font-size: 26px; font-weight: 600; color: var(--text);
    margin-bottom: 8px; padding-bottom: 12px; border-bottom: 2px solid var(--accent-light);
  }
  h2 .tag {
    display: inline-block; font-size: 11px; font-weight: 500;
    background: var(--accent-light); color: var(--accent);
    padding: 2px 8px; border-radius: 4px; margin-left: 10px;
    vertical-align: middle; letter-spacing: 0.05em;
  }
  h3 { font-size: 17px; font-weight: 600; color: var(--text); margin: 28px 0 12px; }
  h4 { font-size: 14px; font-weight: 600; color: var(--text); margin: 16px 0 6px; }
  p { margin-bottom: 12px; color: var(--text-muted); font-size: 14px; }

  pre {
    background: var(--code-bg); border: 1px solid var(--border); border-radius: 8px;
    padding: 16px 18px; font-family: 'SF Mono','Fira Code','Cascadia Code',monospace;
    font-size: 12.5px; line-height: 1.65; overflow-x: auto; margin: 12px 0; color: var(--text);
  }
  code {
    background: var(--code-bg); font-family: 'SF Mono','Fira Code',monospace;
    font-size: 12px; padding: 1px 5px; border-radius: 3px; color: var(--accent);
  }

  table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 13px; }
  th {
    background: var(--gray-light); font-weight: 600; text-align: left;
    padding: 9px 13px; border-bottom: 2px solid var(--border);
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em;
  }
  td { padding: 8px 13px; border-bottom: 1px solid var(--border); vertical-align: top; font-size: 13px; }
  tr:last-child td { border-bottom: none; }
  td code { font-size: 11.5px; }

  .callout {
    border-left: 3px solid var(--accent); background: var(--accent-light);
    border-radius: 0 8px 8px 0; padding: 13px 16px; margin: 14px 0; font-size: 13.5px; color: var(--text);
  }
  .callout.warning { border-color: var(--amber); background: var(--amber-light); }
  .callout.success { border-color: var(--teal); background: var(--teal-light); }
  .callout.sky     { border-color: var(--sky);  background: var(--sky-light); }

  .badge {
    display: inline-block; font-size: 10px; font-weight: 700;
    padding: 2px 7px; border-radius: 3px; letter-spacing: 0.05em; text-transform: uppercase;
  }
  .badge-pk   { background: #e8f4ff; color: #1a5fa8; }
  .badge-fk   { background: var(--teal-light); color: var(--teal); }
  .badge-idx  { background: var(--amber-light); color: var(--amber); }
  .badge-uniq { background: var(--coral-light); color: var(--coral); }
  .badge-opt  { background: var(--gray-light); color: var(--gray); }
  .badge-ext  { background: var(--sky-light); color: var(--sky); }

  .schema-block { background: var(--bg); border: 1px solid var(--border); border-radius: 10px; margin-bottom: 24px; overflow: hidden; }
  .schema-header {
    background: var(--accent); color: white; padding: 10px 18px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .schema-header h4 { margin: 0; font-size: 14px; font-weight: 700; color: white; font-family: 'SF Mono',monospace; }
  .schema-header span { font-size: 11px; opacity: 0.75; font-weight: 400; }
  .schema-header.teal  { background: var(--teal); }
  .schema-header.coral { background: var(--coral); }
  .schema-header.amber { background: var(--amber); }
  .schema-header.gray  { background: var(--gray); }
  .schema-header.sky   { background: var(--sky); }
  .schema-header.purple-dark { background: #3730a3; }

  .schema-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  .schema-table th {
    background: var(--gray-light); padding: 7px 14px; font-size: 10.5px;
    text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted);
    font-weight: 600; border-bottom: 1px solid var(--border);
  }
  .schema-table td { padding: 7px 14px; border-bottom: 1px solid #eceae4; vertical-align: middle; }
  .schema-table tr:last-child td { border-bottom: none; }
  .field-name { font-family: 'SF Mono',monospace; font-size: 12px; font-weight: 600; color: var(--text); }
  .field-type { font-family: 'SF Mono',monospace; font-size: 11.5px; color: var(--teal); white-space: nowrap; }
  .field-notes { color: var(--text-muted); font-size: 12px; }

  .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 16px 0; }
  .card-sm { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px 18px; }
  .card-sm h4 { margin-top: 0; font-size: 13px; }
  .card-sm p { font-size: 12.5px; margin-bottom: 0; }

  /* ERD */
  .erd-container {
    background: var(--bg); border: 1px solid var(--border); border-radius: 10px;
    padding: 28px; margin: 16px 0; overflow-x: auto;
  }
  .erd-row { display: flex; align-items: center; gap: 0; margin-bottom: 6px; flex-wrap: nowrap; }
  .erd-box {
    border: 1.5px solid var(--border); border-radius: 6px; padding: 7px 14px;
    font-family: 'SF Mono',monospace; font-size: 12px; font-weight: 600;
    background: var(--bg); white-space: nowrap; color: var(--text);
  }
  .erd-box.core    { border-color: var(--accent); background: var(--accent-light); color: var(--accent); }
  .erd-box.content { border-color: var(--teal);   background: var(--teal-light);  color: var(--teal); }
  .erd-box.hw      { border-color: var(--amber);  background: var(--amber-light); color: var(--amber); }
  .erd-box.quiz    { border-color: var(--coral);  background: var(--coral-light); color: var(--coral); }
  .erd-box.ext     { border-color: var(--sky);    background: var(--sky-light);   color: var(--sky); border-style: dashed; }
  .erd-line { font-family: monospace; font-size: 13px; color: var(--text-muted); padding: 0 4px; white-space: nowrap; }
  .erd-section { margin-bottom: 20px; }
  .erd-section h5 { font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 10px; font-weight: 600; }

  /* Rel lines */
  .rel-line { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 13px; border-bottom: 1px dashed var(--border); }
  .rel-line:last-child { border-bottom: none; }
  .rel-arrow { color: var(--accent); font-weight: 700; font-family: monospace; }
  .rel-card  { background: var(--bg); border: 1px solid var(--border); border-radius: 3px; font-family: 'SF Mono',monospace; font-size: 11.5px; padding: 1px 6px; }
  .rel-card  { color: var(--text); }
  .rel-cardinality { font-size: 11px; color: var(--text-muted); background: var(--gray-light); padding: 1px 6px; border-radius: 3px; font-family: monospace; }

  /* Decision cards */
  .decision-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 16px 0; }
  .decision-card { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px 18px; border-top: 3px solid var(--accent); }
  .decision-card h4 { margin-top: 0; font-size: 13px; color: var(--accent); }
  .decision-card p { font-size: 12.5px; margin-bottom: 0; }
  .decision-card.teal  { border-top-color: var(--teal); }  .decision-card.teal h4  { color: var(--teal); }
  .decision-card.coral { border-top-color: var(--coral); } .decision-card.coral h4 { color: var(--coral); }
  .decision-card.amber { border-top-color: var(--amber); } .decision-card.amber h4 { color: var(--amber); }
  .decision-card.sky   { border-top-color: var(--sky); }   .decision-card.sky h4   { color: var(--sky); }
  .decision-card.gray  { border-top-color: var(--gray); }  .decision-card.gray h4  { color: var(--gray); }

  /* Flow */
  .flow-row { display: flex; align-items: center; gap: 0; flex-wrap: wrap; margin: 16px 0; }
  .flow-node { background: var(--accent); color: white; border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: 500; }
  .flow-node.teal  { background: var(--teal); }
  .flow-node.amber { background: var(--amber); }
  .flow-node.coral { background: var(--coral); }
  .flow-node.gray  { background: var(--gray); }
  .flow-node.sky   { background: var(--sky); }
  .flow-arrow { font-size: 18px; color: var(--text-muted); padding: 0 8px; }

  /* Domain boundary marker */
  .boundary { border: 2px dashed var(--sky); border-radius: 10px; padding: 16px 20px; margin: 16px 0; }
  .boundary-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--sky); margin-bottom: 8px; }

  /* Future ext */
  .future-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 16px 0; }
  .future-card { background: var(--bg); border: 1px dashed var(--sky); border-radius: 8px; padding: 14px 16px; }
  .future-card h4 { margin-top: 0; font-size: 13px; color: var(--sky); }
  .future-card p  { font-size: 12px; margin-bottom: 0; }

  hr { border: none; border-top: 1px solid var(--border); margin: 28px 0; }

  .overview-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 0; margin: 20px 0; overflow: hidden; border-radius: 10px; border: 1px solid var(--border); }
  .overview-col { padding: 16px 14px; border-right: 1px solid var(--border); }
  .overview-col:last-child { border-right: none; }
  .overview-col h5 { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; margin-bottom: 10px; }
  .overview-col ul { list-style: none; padding: 0; }
  .overview-col ul li { font-size: 12px; color: var(--text-muted); padding: 3px 0; border-bottom: 1px dashed #e8e6e0; }
  .overview-col ul li:last-child { border-bottom: none; }
  .overview-col.col-core  { background: var(--accent-light); } .overview-col.col-core  h5 { color: var(--accent); }
  .overview-col.col-cont  { background: var(--teal-light); }  .overview-col.col-cont  h5 { color: var(--teal); }
  .overview-col.col-hw    { background: var(--amber-light); } .overview-col.col-hw    h5 { color: var(--amber); }
  .overview-col.col-quiz  { background: var(--coral-light); } .overview-col.col-quiz  h5 { color: var(--coral); }
  .overview-col.col-enrol { background: var(--sky-light); }   .overview-col.col-enrol h5 { color: var(--sky); }

  @media (max-width: 1100px) { nav { display: none; } main { padding: 24px 20px; } }
  @media (max-width: 700px)  { .decision-grid { grid-template-columns: 1fr; } .overview-grid { grid-template-columns: 1fr 1fr; } }
</style>
</head>
<body>
<div class="layout">

<!-- SIDEBAR -->
<nav>
  <div class="logo">
    <h1>Learning Domain</h1>
    <p>LearnFlow Design Document v2.0</p>
  </div>
  <div class="section-label">Overview</div>
  <a href="#overview">Domain Overview</a>
  <a href="#boundaries">Domain Boundaries</a>
  <a href="#learning-flow">Learning Flow</a>
  <div class="section-label">Core Tables</div>
  <a href="#course">Course</a>
  <a href="#module">Module</a>
  <a href="#lesson">Lesson</a>
  <a href="#enrollment">CourseEnrollment</a>
  <div class="section-label">Catalog</div>
  <a href="#category">CourseCategory</a>
  <div class="section-label">Lesson Components</div>
  <a href="#content">LessonContent</a>
  <a href="#homework">LessonHomework</a>
  <a href="#practice">LessonPractice</a>
  <a href="#quiz">LessonQuiz</a>
  <a class="sub" href="#quiz-question">QuizQuestion</a>
  <a class="sub" href="#quiz-option">QuizOption</a>
  <div class="section-label">Architecture</div>
  <a href="#erd">ERD Relationships</a>
  <a href="#decisions">Design Decisions</a>
  <a href="#indexes">Indexes & Constraints</a>
  <a href="#cross-domain">Cross-Domain Refs</a>
  <a href="#future">Future Extensions</a>
</nav>

<!-- MAIN -->
<main>

<!-- OVERVIEW -->
<section id="overview">
  <h2>Learning Domain Overview <span class="tag">SCOPE</span></h2>

  <div class="callout sky" style="margin-bottom:18px">
    <strong>v2.0 Changes from v1.0</strong><br>
    <span style="font-size:13px">
      <strong>1.</strong> <code>Enrollment</code> → <code>CourseEnrollment</code> — explicit name anticipating future <code>MentorGroupEnrollment</code>, <code>EventEnrollment</code> etc.<br>
      <strong>2.</strong> <code>Course.mode</code> removed — replaced with <code>supports_online</code> / <code>supports_offline</code> flags. Delivery format moved to <code>CourseEnrollment.delivery_format</code>. One course, no duplication.<br>
      <strong>3.</strong> Cross-domain soft UUIDs replaced with real <code>ForeignKey</code> — monolith, one DB, no reason to pay the complexity cost early.<br>
      <strong>4.</strong> <code>CourseCategory</code> added — hierarchical catalog taxonomy (2 levels). Single FK on Course.
    </span>
  </div>

  <p>The Learning Domain owns the complete course structure — from catalog to lesson content. It defines <em>what</em> students learn. It does not own <em>how far</em> they've gotten (UserProgress), <em>how well</em> they did (Assessment), or <em>who taught them</em> (Mentorship).</p>

  <div class="overview-grid" style="grid-template-columns:repeat(6,1fr)">
    <div class="overview-col col-core">
      <h5>🗂 Core Structure</h5>
      <ul>
        <li>Course</li>
        <li>Module</li>
        <li>Lesson</li>
        <li>CourseEnrollment</li>
      </ul>
    </div>
    <div class="overview-col col-cont">
      <h5>📄 Content</h5>
      <ul>
        <li>LessonContent</li>
        <li>Types: video</li>
        <li>pdf / slides</li>
        <li>text / link</li>
        <li>recording / code</li>
      </ul>
    </div>
    <div class="overview-col col-hw">
      <h5>📝 Practice</h5>
      <ul>
        <li>LessonHomework</li>
        <li>LessonPractice</li>
      </ul>
    </div>
    <div class="overview-col col-quiz">
      <h5>✅ Quiz</h5>
      <ul>
        <li>LessonQuiz</li>
        <li>QuizQuestion</li>
        <li>QuizOption</li>
      </ul>
    </div>
    <div class="overview-col col-enrol">
      <h5>🔗 Bridge</h5>
      <ul>
        <li>CourseEnrollment</li>
        <li>User → Course</li>
        <li>delivery_format</li>
      </ul>
    </div>
    <div class="overview-col" style="background:var(--teal-light)">
      <h5 style="color:var(--teal)">🏷 Catalog</h5>
      <ul>
        <li>CourseCategory</li>
        <li>parent / children</li>
        <li>slug / order</li>
      </ul>
    </div>
  </div>

  <p><strong>12 tables total.</strong> Every table has a single, well-defined responsibility. No god-objects. No polymorphic cross-domain inheritance.</p>
</section>

<!-- DOMAIN BOUNDARIES -->
<section id="boundaries">
  <h2>Domain Boundaries <span class="tag">WHAT WE OWN</span></h2>

  <div class="boundary">
    <div class="boundary-label">🔵 Learning Domain — this document</div>
    <div class="flow-row">
      <div class="flow-node">Course</div><div class="flow-arrow">→</div>
      <div class="flow-node">Module</div><div class="flow-arrow">→</div>
      <div class="flow-node">Lesson</div><div class="flow-arrow">→</div>
      <div class="flow-node teal">Content</div><div class="flow-arrow">+</div>
      <div class="flow-node amber">Homework</div><div class="flow-arrow">+</div>
      <div class="flow-node amber">Practice</div><div class="flow-arrow">+</div>
      <div class="flow-node coral">Quiz</div>
    </div>
  </div>

  <div class="card-grid" style="margin-top:16px">
    <div class="card-sm" style="border-top: 3px solid var(--sky)">
      <h4 style="color:var(--sky)">References (real FK in monolith)</h4>
      <p>Identity domain: <code>User.id</code> is referenced via real Django <code>ForeignKey</code> in <code>CourseEnrollment</code> and <code>Course.created_by</code>. When extracted to microservices — remove FK in one migration.</p>
    </div>
    <div class="card-sm" style="border-top: 3px dashed var(--gray)">
      <h4 style="color:var(--gray)">NOT in this domain</h4>
      <p>UserProgress · Analytics · Assessment/Exams · Certificates · Mentorship groups · Notifications · Submissions review</p>
    </div>
    <div class="card-sm" style="border-top: 3px solid var(--teal)">
      <h4 style="color:var(--teal)">Consumed by other domains</h4>
      <p><code>Lesson.id</code> → UserProgress tracks completion. <code>LessonHomework.id</code> → Submissions domain handles uploads. <code>LessonQuiz.id</code> → Assessment domain records attempts.</p>
    </div>
  </div>
</section>

<!-- LEARNING FLOW -->
<section id="learning-flow">
  <h2>Learning Flow <span class="tag">SEQUENCE</span></h2>
  <p>The learning domain defines the structure. Other domains consume it to power the student journey.</p>

  <div style="display:flex;flex-direction:column;gap:0;background:var(--bg);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin:16px 0">
    <div style="display:flex;align-items:center;gap:14px;padding:13px 20px;border-bottom:1px solid var(--border)">
      <div style="min-width:28px;height:28px;border-radius:50%;background:var(--accent);color:white;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center">1</div>
      <div><strong style="font-size:13px">CourseEnrollment</strong> — <span style="color:var(--text-muted);font-size:13px">Student enrolls in Course → <code>CourseEnrollment</code> row created. Delivery format (online/offline) locked here, not on the Course itself.</span></div>
      <span style="margin-left:auto;font-size:11px;color:var(--sky);background:var(--sky-light);padding:2px 8px;border-radius:4px;white-space:nowrap">Learning Domain</span>
    </div>
    <div style="display:flex;align-items:center;gap:14px;padding:13px 20px;border-bottom:1px solid var(--border)">
      <div style="min-width:28px;height:28px;border-radius:50%;background:var(--accent);color:white;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center">2</div>
      <div><strong style="font-size:13px">Lesson Study</strong> — <span style="color:var(--text-muted);font-size:13px">Student views LessonContent items (video, text, pdf, etc.) in order.</span></div>
      <span style="margin-left:auto;font-size:11px;color:var(--teal);background:var(--teal-light);padding:2px 8px;border-radius:4px;white-space:nowrap">UserProgress Domain</span>
    </div>
    <div style="display:flex;align-items:center;gap:14px;padding:13px 20px;border-bottom:1px solid var(--border)">
      <div style="min-width:28px;height:28px;border-radius:50%;background:var(--accent);color:white;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center">3</div>
      <div><strong style="font-size:13px">Lesson Practice + Quiz</strong> — <span style="color:var(--text-muted);font-size:13px">In-lesson check: LessonPractice exercises and LessonQuiz knowledge check.</span></div>
      <span style="margin-left:auto;font-size:11px;color:var(--coral);background:var(--coral-light);padding:2px 8px;border-radius:4px;white-space:nowrap">Assessment Domain</span>
    </div>
    <div style="display:flex;align-items:center;gap:14px;padding:13px 20px;border-bottom:1px solid var(--border)">
      <div style="min-width:28px;height:28px;border-radius:50%;background:var(--accent);color:white;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center">4</div>
      <div><strong style="font-size:13px">Homework Submission</strong> — <span style="color:var(--text-muted);font-size:13px">Student submits work defined by LessonHomework. Mentor reviews via Submissions domain.</span></div>
      <span style="margin-left:auto;font-size:11px;color:var(--amber);background:var(--amber-light);padding:2px 8px;border-radius:4px;white-space:nowrap">Submissions Domain</span>
    </div>
    <div style="display:flex;align-items:center;gap:14px;padding:13px 20px">
      <div style="min-width:28px;height:28px;border-radius:50%;background:var(--accent);color:white;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center">5</div>
      <div><strong style="font-size:13px">Module Assessment</strong> — <span style="color:var(--text-muted);font-size:13px">End-of-module exam. Pass → unlock next Module. Fail → retake. Owned by Assessment domain.</span></div>
      <span style="margin-left:auto;font-size:11px;color:var(--coral);background:var(--coral-light);padding:2px 8px;border-radius:4px;white-space:nowrap">Assessment Domain</span>
    </div>
  </div>

  <div class="callout">
    <strong>Key principle:</strong> The Learning Domain defines the <em>structure and content</em>. All <em>student interaction with that content</em> (progress, attempts, submissions, grades) lives in separate domains that reference Learning Domain IDs.
  </div>
</section>

<!-- ===================== CORE TABLES ===================== -->

<!-- COURSE -->
<section id="course">
  <h2>Course <span class="tag">TOP-LEVEL CONTAINER</span></h2>
  <p>The root entity of the Learning Domain. A Course groups Modules and defines sequencing rules and publication status. It acts as the catalog entry visible to students and admins. Delivery mode is <strong>not</strong> stored on Course — it is a property of each <code>CourseEnrollment</code>. The Course only declares which delivery formats it supports.</p>

  <div class="schema-block">
    <div class="schema-header">
      <h4>courses_course</h4>
      <span>Top-level learning container · soft-deletable</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes">gen_random_uuid()</td></tr>
      <tr><td class="field-name">title</td><td class="field-type">VARCHAR(255)</td><td>NOT NULL</td><td class="field-notes">Display title shown to students</td></tr>
      <tr><td class="field-name">slug</td><td class="field-type">VARCHAR(255)</td><td>NOT NULL <span class="badge badge-uniq">UNIQUE</span></td><td class="field-notes">URL-safe identifier. Auto-generated from title. e.g. <code>python-backend-dev</code></td></tr>
      <tr><td class="field-name">description</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Long-form course description. Supports markdown.</td></tr>
      <tr><td class="field-name">short_description</td><td class="field-type">VARCHAR(500)</td><td>NULLABLE</td><td class="field-notes">Used in catalog cards and previews</td></tr>
      <tr><td class="field-name">thumbnail_url</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">S3/CDN URL. Null = default placeholder.</td></tr>
      <tr><td class="field-name">category_id</td><td class="field-type">UUID</td><td>NULLABLE <span class="badge badge-fk">FK</span></td><td class="field-notes">→ courses_coursecategory.id, SET NULL on delete. Null = uncategorised.</td></tr>
      <tr><td class="field-name">status</td><td class="field-type">VARCHAR(20)</td><td>NOT NULL, DEFAULT 'draft'</td><td class="field-notes"><code>draft</code> | <code>published</code> | <code>archived</code>. Only published courses visible to students.</td></tr>
      <tr><td class="field-name">supports_online</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT true</td><td class="field-notes">Course can be taken online (self-paced). Validated by CourseEnrollmentService at enrollment time.</td></tr>
      <tr><td class="field-name">supports_offline</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT false</td><td class="field-notes">Course can be taken offline (mentor-led group). Validated by CourseEnrollmentService at enrollment time.</td></tr>
      <tr><td class="field-name">language</td><td class="field-type">VARCHAR(10)</td><td>NOT NULL, DEFAULT 'ru'</td><td class="field-notes">BCP-47 tag. For future localization.</td></tr>
      <tr><td class="field-name">estimated_weeks</td><td class="field-type">SMALLINT</td><td>NULLABLE, CHECK &gt; 0</td><td class="field-notes">Shown in catalog as expected duration</td></tr>
      <tr><td class="field-name">is_sequential</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT true</td><td class="field-notes">If true, modules must be completed in order. If false, all modules are unlocked from the start.</td></tr>
      <tr><td class="field-name">created_by</td><td class="field-type">ForeignKey</td><td>NOT NULL <span class="badge badge-fk">FK</span></td><td class="field-notes">→ <code>settings.AUTH_USER_MODEL</code>, SET NULL on delete. Real DB FK — monolith. Remove when extracting to service.</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">updated_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">deleted_at</td><td class="field-type">TIMESTAMPTZ</td><td>NULLABLE</td><td class="field-notes">Soft delete. Non-null = archived/deleted. Use SoftDeleteManager to exclude from default queries.</td></tr>
    </table>
  </div>

  <pre>-- Indexes
CREATE UNIQUE INDEX idx_course_slug     ON courses_course (slug);
CREATE INDEX idx_course_status          ON courses_course (status) WHERE deleted_at IS NULL;
CREATE INDEX idx_course_category        ON courses_course (category_id) WHERE deleted_at IS NULL;

-- Constraint
ALTER TABLE courses_course
    ADD CONSTRAINT chk_course_status  CHECK (status IN ('draft','published','archived')),
    ADD CONSTRAINT chk_course_weeks   CHECK (estimated_weeks IS NULL OR estimated_weeks > 0),
    -- Must support at least one delivery format
    ADD CONSTRAINT chk_course_delivery CHECK (supports_online = TRUE OR supports_offline = TRUE);</pre>

  <div class="callout warning">
    <strong>Why remove <code>mode</code> from Course?</strong> A course like "Python Backend" is one course — its content (modules, lessons) is identical for online and offline students. Putting <code>mode</code> on Course would force duplicate entries: "Python Backend Online" and "Python Backend Offline". Instead, <code>supports_online</code> / <code>supports_offline</code> flags declare capability, while <code>CourseEnrollment.delivery_format</code> records the student's actual delivery choice. No content duplication.
  </div>
  <div class="callout">
    <strong>Why <code>is_sequential</code> on Course?</strong> Most courses are sequential — students must finish Module 1 before unlocking Module 2. But some courses (e.g. reference material, elective topics) should allow free navigation. This flag drives the unlock logic in the UserProgress domain without needing a separate table.
  </div>
</section>

<!-- MODULE -->
<section id="module">
  <h2>Module <span class="tag">LESSON GROUPING</span></h2>
  <p>A Module groups related Lessons into a logical unit. It is the granularity at which students are assessed (end-of-module assessment). Modules are ordered within a course and can be independently published.</p>

  <div class="schema-block">
    <div class="schema-header teal">
      <h4>courses_module</h4>
      <span>Ordered lesson grouping within a course · soft-deletable</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes"></td></tr>
      <tr><td class="field-name">course_id</td><td class="field-type">UUID</td><td><span class="badge badge-fk">FK</span> NOT NULL</td><td class="field-notes">→ courses_course.id, CASCADE DELETE</td></tr>
      <tr><td class="field-name">title</td><td class="field-type">VARCHAR(255)</td><td>NOT NULL</td><td class="field-notes">e.g. "Module 3 — Django REST Framework"</td></tr>
      <tr><td class="field-name">description</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">What this module covers. Shown before unlock.</td></tr>
      <tr><td class="field-name">order</td><td class="field-type">SMALLINT</td><td>NOT NULL, CHECK &gt; 0</td><td class="field-notes">Position within course. UNIQUE with course_id. No gaps required — reorder via bulk update.</td></tr>
      <tr><td class="field-name">is_published</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT false</td><td class="field-notes">Unpublished modules invisible to students. Allows staged rollout of module-by-module.</td></tr>
      <tr><td class="field-name">estimated_hours</td><td class="field-type">SMALLINT</td><td>NULLABLE, CHECK &gt; 0</td><td class="field-notes">Shown on module overview screen. Informational only.</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">updated_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">deleted_at</td><td class="field-type">TIMESTAMPTZ</td><td>NULLABLE</td><td class="field-notes">Soft delete</td></tr>
    </table>
  </div>

  <pre>-- Ordering uniqueness per course
CREATE UNIQUE INDEX uq_module_course_order
    ON courses_module (course_id, "order")
    WHERE deleted_at IS NULL;

-- Fast ordered listing for a course
CREATE INDEX idx_module_course_published
    ON courses_module (course_id, "order")
    WHERE is_published = TRUE AND deleted_at IS NULL;</pre>

  <div class="callout">
    <strong>Order uniqueness strategy:</strong> The <code>UNIQUE(course_id, order)</code> index is partial (<code>WHERE deleted_at IS NULL</code>). This allows a deleted module to "leave" its slot without blocking a new module at the same position. Reordering is done in a single transaction with a temporary displacement step to avoid constraint violations.
  </div>
</section>

<!-- LESSON -->
<section id="lesson">
  <h2>Lesson <span class="tag">LEARNING UNIT</span></h2>
  <p>The atomic learning container. A Lesson is what a student opens and works through. It may contain zero or more Content items, zero or one Homework, zero or more Practice exercises, and zero or one Quiz. All four are optional.</p>

  <div class="schema-block">
    <div class="schema-header">
      <h4>courses_lesson</h4>
      <span>Atomic learning container · holds content, homework, practice, quiz</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes"></td></tr>
      <tr><td class="field-name">module_id</td><td class="field-type">UUID</td><td><span class="badge badge-fk">FK</span> NOT NULL</td><td class="field-notes">→ courses_module.id, CASCADE DELETE</td></tr>
      <tr><td class="field-name">title</td><td class="field-type">VARCHAR(255)</td><td>NOT NULL</td><td class="field-notes">e.g. "Lesson 4 — JWT Authentication"</td></tr>
      <tr><td class="field-name">description</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Short overview shown in module lesson list</td></tr>
      <tr><td class="field-name">order</td><td class="field-type">SMALLINT</td><td>NOT NULL, CHECK &gt; 0</td><td class="field-notes">Position within module. UNIQUE with module_id.</td></tr>
      <tr><td class="field-name">is_published</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT false</td><td class="field-notes">Controls student visibility independent of module publish state</td></tr>
      <tr><td class="field-name">is_free_preview</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT false</td><td class="field-notes">If true, lesson content visible without enrollment (marketing)</td></tr>
      <tr><td class="field-name">estimated_minutes</td><td class="field-type">SMALLINT</td><td>NULLABLE, CHECK &gt; 0</td><td class="field-notes">Expected time to complete. Shown on lesson card.</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">updated_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">deleted_at</td><td class="field-type">TIMESTAMPTZ</td><td>NULLABLE</td><td class="field-notes">Soft delete. UserProgress records for this lesson preserved.</td></tr>
    </table>
  </div>

  <pre>CREATE UNIQUE INDEX uq_lesson_module_order
    ON courses_lesson (module_id, "order")
    WHERE deleted_at IS NULL;

CREATE INDEX idx_lesson_module_published
    ON courses_lesson (module_id, "order")
    WHERE is_published = TRUE AND deleted_at IS NULL;</pre>

  <div class="callout success">
    <strong>Online vs Offline:</strong> No <code>mode</code> field on Lesson. The lesson structure (content, homework, quiz) is identical for both delivery formats. The student's <code>CourseEnrollment.delivery_format</code> determines how the course is delivered. For offline courses, the <em>Session Scheduling</em> in the Mentorship domain maps which lessons are covered in which class session.
  </div>
</section>

<!-- ENROLLMENT -->
<section id="enrollment">
  <h2>CourseEnrollment <span class="tag">DOMAIN BRIDGE</span></h2>
  <p>CourseEnrollment is the foundational link between the Identity domain (User) and the Learning domain (Course). Named explicitly to distinguish it from future <code>MentorGroupEnrollment</code>, <code>EventEnrollment</code>, and <code>CertificationEnrollment</code> models. Its lifecycle is tied to the course — not the user's auth state. It answers: "which students are taking which course, and in which delivery format?"</p>

  <div class="callout sky">
    <strong>delivery_format lives here, not on Course.</strong> One course can have students enrolled both online and offline simultaneously. The format is a property of the student's enrollment, not of the course content. This eliminates the need for duplicate courses like "Python Backend Online" and "Python Backend Offline".
  </div>

  <div class="schema-block">
    <div class="schema-header sky">
      <h4>courses_courseenrollment</h4>
      <span>User × Course membership — cross-domain bridge · explicit name</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes"></td></tr>
      <tr><td class="field-name">user</td><td class="field-type">ForeignKey</td><td>NOT NULL <span class="badge badge-fk">FK</span> <span class="badge badge-idx">IDX</span></td><td class="field-notes">→ <code>settings.AUTH_USER_MODEL</code>, PROTECT. Real DB FK — monolith. Use <code>on_delete=PROTECT</code>: don't silently drop enrollments if user deleted; handle explicitly via signal.</td></tr>
      <tr><td class="field-name">course</td><td class="field-type">ForeignKey</td><td>NOT NULL <span class="badge badge-fk">FK</span> <span class="badge badge-idx">IDX</span></td><td class="field-notes">→ <code>courses_course.id</code>, RESTRICT DELETE (cannot delete course with active enrollments)</td></tr>
      <tr><td class="field-name">status</td><td class="field-type">VARCHAR(20)</td><td>NOT NULL, DEFAULT 'active'</td><td class="field-notes"><code>active</code> | <code>completed</code> | <code>dropped</code></td></tr>
      <tr><td class="field-name">delivery_format</td><td class="field-type">VARCHAR(10)</td><td>NOT NULL</td><td class="field-notes"><code>online</code> | <code>offline</code>. Selected by student (or admin) at enrollment time. Validated against <code>course.supports_online</code> / <code>course.supports_offline</code>.</td></tr>
      <tr><td class="field-name">enrolled_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes">Immutable after creation</td></tr>
      <tr><td class="field-name">completed_at</td><td class="field-type">TIMESTAMPTZ</td><td>NULLABLE</td><td class="field-notes">Set when all modules passed. Triggers certificate in Certification domain.</td></tr>
      <tr><td class="field-name">dropped_at</td><td class="field-type">TIMESTAMPTZ</td><td>NULLABLE</td><td class="field-notes">Set when status = dropped</td></tr>
      <tr><td class="field-name">enrolled_by</td><td class="field-type">ForeignKey</td><td>NULLABLE <span class="badge badge-fk">FK</span></td><td class="field-notes">If null → self-enrolled. If set → admin/mentor enrolled this student. → <code>settings.AUTH_USER_MODEL</code>, SET NULL on delete.</td></tr>
    </table>
  </div>

  <pre>-- One enrollment per user per course
CREATE UNIQUE INDEX uq_courseenrollment_user_course
    ON courses_courseenrollment (user_id, course_id);

-- Fast lookup: all active courses for a student (dashboard)
CREATE INDEX idx_courseenrollment_user_status
    ON courses_courseenrollment (user_id, status);

-- Fast lookup: all students in a course (mentor/admin view)
CREATE INDEX idx_courseenrollment_course_status
    ON courses_courseenrollment (course_id, status);

-- Constraint
ALTER TABLE courses_courseenrollment
    ADD CONSTRAINT chk_enrollment_status         CHECK (status IN ('active','completed','dropped')),
    ADD CONSTRAINT chk_enrollment_delivery_format CHECK (delivery_format IN ('online','offline'));
</pre>

  <div class="callout warning">
    <strong>Why real FK to User?</strong> We are building a Django monolith with a single PostgreSQL database. Both <code>accounts</code> and <code>courses</code> apps share the same DB. Real foreign keys give us free cascade/protect semantics, <code>select_related</code> in the ORM, and DB-level integrity at zero extra cost. When (if) we ever extract to microservices, we remove these FKs in a single migration. Premature soft-UUID references add complexity without any benefit today.
  </div>
</section>

<!-- ===================== CATALOG ===================== -->

<!-- COURSE CATEGORY -->
<section id="category">
  <h2>CourseCategory <span class="tag">CATALOG TAXONOMY</span></h2>
  <p>Categories organise the course catalog into a navigable hierarchy. Without this, the catalog becomes a flat, unfiltered list that grows unusable. Supports two levels: root categories (Backend, Frontend, DevOps) and subcategories (Django, FastAPI under Backend).</p>

  <div class="callout">
    <strong>Single FK, not a junction table.</strong> One course belongs to one primary category. A junction table (<code>CourseCategoryAssignment</code>) would be needed only if one course genuinely belongs to multiple categories. Start with a single FK — it covers 95% of cases. If multi-category tagging becomes a product requirement, add a junction table without touching existing data.
  </div>

  <div class="schema-block">
    <div class="schema-header teal">
      <h4>courses_coursecategory</h4>
      <span>Hierarchical catalog taxonomy — max 2 levels (root + subcategory)</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes">gen_random_uuid()</td></tr>
      <tr><td class="field-name">name</td><td class="field-type">VARCHAR(100)</td><td>NOT NULL</td><td class="field-notes">Display name. e.g. "Backend Development", "Django"</td></tr>
      <tr><td class="field-name">slug</td><td class="field-type">VARCHAR(100)</td><td>NOT NULL <span class="badge badge-uniq">UNIQUE</span></td><td class="field-notes">URL-safe. e.g. <code>backend</code>, <code>django</code>. Used in catalog routes: <code>/catalog/backend/</code></td></tr>
      <tr><td class="field-name">parent</td><td class="field-type">ForeignKey</td><td>NULLABLE <span class="badge badge-fk">FK</span></td><td class="field-notes">Self-referential. → <code>courses_coursecategory.id</code>, SET NULL on delete. NULL = root category. Non-null = subcategory.</td></tr>
      <tr><td class="field-name">description</td><td class="field-type">VARCHAR(500)</td><td>NULLABLE</td><td class="field-notes">Short description shown on catalog filter panel</td></tr>
      <tr><td class="field-name">icon</td><td class="field-type">VARCHAR(50)</td><td>NULLABLE</td><td class="field-notes">Icon identifier or emoji. e.g. <code>code-bracket</code> (Heroicons), <code>🐍</code>. Rendered by frontend.</td></tr>
      <tr><td class="field-name">order</td><td class="field-type">SMALLINT</td><td>NOT NULL, DEFAULT 0</td><td class="field-notes">Display order within the same parent. Lower = shown first.</td></tr>
      <tr><td class="field-name">is_active</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT true</td><td class="field-notes">Inactive categories hidden from catalog. Courses retain their category_id — they are not orphaned.</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">updated_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
    </table>
  </div>

  <pre>-- Slug must be globally unique (not just per parent) for clean URLs
CREATE UNIQUE INDEX idx_category_slug ON courses_coursecategory (slug);

-- Fast listing: all root categories in order
CREATE INDEX idx_category_root ON courses_coursecategory (parent_id, "order")
    WHERE is_active = TRUE;

-- Fast listing: subcategories of a given parent
CREATE INDEX idx_category_children ON courses_coursecategory (parent_id, "order")
    WHERE parent_id IS NOT NULL AND is_active = TRUE;</pre>

  <h3>Category hierarchy example</h3>
  <pre>Backend (root, parent=NULL)
  ├── Django        (parent=Backend)
  ├── FastAPI       (parent=Backend)
  └── Node.js       (parent=Backend)

Frontend (root, parent=NULL)
  ├── React         (parent=Frontend)
  └── Vue           (parent=Frontend)

DevOps (root, parent=NULL)
Mobile (root, parent=NULL)</pre>

  <div class="callout warning">
    <strong>Max depth = 2.</strong> The schema allows arbitrary depth (self-referential FK), but the application should enforce max 2 levels (root + one subcategory level). Deeper hierarchies produce confusing UX without product benefit at this stage. Application-level validation: <code>if parent.parent_id is not None: raise ValidationError</code>.
  </div>
</section>

<!-- ===================== LESSON COMPONENTS ===================== -->

<!-- LESSON CONTENT -->
<section id="content">
  <h2>LessonContent <span class="tag">UNIFIED CONTENT MODEL</span></h2>
  <p>A single table handles all content types via a <code>type</code> discriminator. One lesson can have multiple content items, ordered and displayed in sequence. This avoids a table-per-type explosion while keeping queries simple.</p>

  <div class="schema-block">
    <div class="schema-header teal">
      <h4>courses_lessoncontent</h4>
      <span>Unified content item: video | pdf | slides | text | link | recording | code</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes"></td></tr>
      <tr><td class="field-name">lesson_id</td><td class="field-type">UUID</td><td><span class="badge badge-fk">FK</span> NOT NULL <span class="badge badge-idx">IDX</span></td><td class="field-notes">→ courses_lesson.id, CASCADE DELETE</td></tr>
      <tr><td class="field-name">type</td><td class="field-type">VARCHAR(20)</td><td>NOT NULL</td><td class="field-notes"><code>video</code> | <code>pdf</code> | <code>slides</code> | <code>text</code> | <code>link</code> | <code>recording</code> | <code>code</code></td></tr>
      <tr><td class="field-name">title</td><td class="field-type">VARCHAR(255)</td><td>NOT NULL</td><td class="field-notes">Displayed above the content item</td></tr>
      <tr><td class="field-name">description</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Optional context shown below title</td></tr>
      <tr><td class="field-name">order</td><td class="field-type">SMALLINT</td><td>NOT NULL, CHECK &gt; 0</td><td class="field-notes">Display order within lesson. UNIQUE per lesson.</td></tr>
      <tr><td class="field-name">url</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Used for: <code>video</code>, <code>pdf</code>, <code>slides</code>, <code>link</code>, <code>recording</code>. S3 key or external URL.</td></tr>
      <tr><td class="field-name">body</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Used for: <code>text</code> (markdown), <code>code</code> (source code). Stored inline.</td></tr>
      <tr><td class="field-name">duration_seconds</td><td class="field-type">INTEGER</td><td>NULLABLE, CHECK &gt; 0</td><td class="field-notes">Used for <code>video</code> and <code>recording</code>. Shown in UI as "12 min".</td></tr>
      <tr><td class="field-name">file_size_bytes</td><td class="field-type">BIGINT</td><td>NULLABLE, CHECK &gt; 0</td><td class="field-notes">Used for <code>pdf</code>, downloadable files</td></tr>
      <tr><td class="field-name">metadata</td><td class="field-type">JSONB</td><td>NOT NULL, DEFAULT '{}'</td><td class="field-notes">Type-specific extras. Schema documented below. Not queried via SQL — application reads it.</td></tr>
      <tr><td class="field-name">is_required</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT true</td><td class="field-notes">If true, UserProgress domain must record this item as viewed before lesson completes.</td></tr>
      <tr><td class="field-name">is_downloadable</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT false</td><td class="field-notes">Only meaningful for pdf, slides, recording. Controls download button visibility.</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">updated_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
    </table>
  </div>

  <h3>metadata JSONB — by content type</h3>
  <table>
    <tr><th>type</th><th>metadata shape</th><th>Example</th></tr>
    <tr><td><code>video</code></td><td><code>{ provider, thumbnail_url, is_hls }</code></td><td><code>{ "provider": "s3", "thumbnail_url": "...", "is_hls": true }</code></td></tr>
    <tr><td><code>pdf</code></td><td><code>{ page_count }</code></td><td><code>{ "page_count": 24 }</code></td></tr>
    <tr><td><code>slides</code></td><td><code>{ slide_count, embed_url }</code></td><td><code>{ "slide_count": 18, "embed_url": "https://..." }</code></td></tr>
    <tr><td><code>text</code></td><td><code>{}</code></td><td>Body is markdown. No extras needed.</td></tr>
    <tr><td><code>link</code></td><td><code>{ open_in_new_tab, link_text }</code></td><td><code>{ "open_in_new_tab": true, "link_text": "MDN Docs" }</code></td></tr>
    <tr><td><code>recording</code></td><td><code>{ recorded_at, session_title }</code></td><td><code>{ "recorded_at": "2024-10-15", "session_title": "Live Q&A" }</code></td></tr>
    <tr><td><code>code</code></td><td><code>{ language, is_runnable, theme }</code></td><td><code>{ "language": "python", "is_runnable": false, "theme": "dark" }</code></td></tr>
  </table>

  <pre>CREATE UNIQUE INDEX uq_content_lesson_order
    ON courses_lessoncontent (lesson_id, "order");

CREATE INDEX idx_content_lesson
    ON courses_lessoncontent (lesson_id, "order");

-- For content type filtering (e.g. "show all videos in this course")
CREATE INDEX idx_content_type
    ON courses_lessoncontent (type, lesson_id);

ALTER TABLE courses_lessoncontent
    ADD CONSTRAINT chk_content_type CHECK (
        type IN ('video','pdf','slides','text','link','recording','code')
    ),
    -- At least one of url or body must be present
    ADD CONSTRAINT chk_content_has_source CHECK (
        url IS NOT NULL OR body IS NOT NULL
    );</pre>

  <div class="callout">
    <strong>url vs body:</strong> The <code>url</code> field holds an S3 key or external URL for binary/remote content. The <code>body</code> field holds inline text content. These are mutually exclusive per type. A CHECK constraint enforces that at least one is provided. Application-level validation enforces which field applies to which type.
  </div>
</section>

<!-- LESSON HOMEWORK -->
<section id="homework">
  <h2>LessonHomework <span class="tag">1:1 PER LESSON</span></h2>
  <p>Homework is an assignment the student completes <em>outside</em> the platform and submits for mentor review. It defines the task — the submission itself lives in the Submissions domain. At most one homework per lesson (enforced via UNIQUE on lesson_id).</p>

  <div class="schema-block">
    <div class="schema-header amber">
      <h4>courses_lessonhomework</h4>
      <span>Assignment definition — submission handled by Submissions domain</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes"></td></tr>
      <tr><td class="field-name">lesson_id</td><td class="field-type">UUID</td><td><span class="badge badge-fk">FK</span> <span class="badge badge-uniq">UNIQUE</span></td><td class="field-notes">→ courses_lesson.id, CASCADE DELETE. UNIQUE enforces max 1 homework per lesson.</td></tr>
      <tr><td class="field-name">title</td><td class="field-type">VARCHAR(255)</td><td>NOT NULL</td><td class="field-notes">e.g. "Build a REST API with authentication"</td></tr>
      <tr><td class="field-name">description</td><td class="field-type">TEXT</td><td>NOT NULL</td><td class="field-notes">Full task description. Supports markdown.</td></tr>
      <tr><td class="field-name">instructions</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Step-by-step guide, acceptance criteria, hints for where to start</td></tr>
      <tr><td class="field-name">max_score</td><td class="field-type">SMALLINT</td><td>NOT NULL, DEFAULT 100, CHECK &gt; 0</td><td class="field-notes">Max points mentor can award. Used by Submissions domain for scoring.</td></tr>
      <tr><td class="field-name">deadline_offset_days</td><td class="field-type">SMALLINT</td><td>NULLABLE, CHECK &gt; 0</td><td class="field-notes">Days after lesson unlock. Null = no deadline. Absolute deadline computed by Submissions domain at submission time.</td></tr>
      <tr><td class="field-name">submission_type</td><td class="field-type">VARCHAR(20)</td><td>NOT NULL, DEFAULT 'file'</td><td class="field-notes"><code>file</code> | <code>link</code> | <code>text</code> | <code>mixed</code>. Tells Submissions domain what upload UI to show.</td></tr>
      <tr><td class="field-name">allowed_file_types</td><td class="field-type">TEXT[]</td><td>NOT NULL, DEFAULT '{}'</td><td class="field-notes">PostgreSQL array. e.g. <code>{pdf,zip,docx}</code>. Empty = any type allowed.</td></tr>
      <tr><td class="field-name">max_file_size_mb</td><td class="field-type">SMALLINT</td><td>NOT NULL, DEFAULT 20, CHECK &gt; 0</td><td class="field-notes">Enforced by Submissions domain on upload</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">updated_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
    </table>
  </div>

  <pre>ALTER TABLE courses_lessonhomework
    ADD CONSTRAINT chk_homework_submission_type CHECK (
        submission_type IN ('file','link','text','mixed')
    );

-- lesson_id UNIQUE index already created by OneToOneField migration</pre>

  <div class="callout success">
    <strong>Learning Domain responsibility ends here.</strong> LessonHomework says "the task is X, score out of Y, deadline is Z days after unlock." The Submissions domain reads these fields when a student submits, computes the absolute deadline, and handles file upload, mentor review, and scoring independently.
  </div>
</section>

<!-- LESSON PRACTICE -->
<section id="practice">
  <h2>LessonPractice <span class="tag">1:N PER LESSON</span></h2>
  <p>Practice exercises are completed <em>within</em> the platform — interactive, in-lesson tasks. Unlike homework, practice is done inline. A lesson can have multiple practice items (e.g., three short coding challenges). The Assessment domain records student attempts.</p>

  <div class="schema-block">
    <div class="schema-header amber">
      <h4>courses_lessonpractice</h4>
      <span>In-platform practice exercise — multiple per lesson, ordered</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes"></td></tr>
      <tr><td class="field-name">lesson_id</td><td class="field-type">UUID</td><td><span class="badge badge-fk">FK</span> NOT NULL <span class="badge badge-idx">IDX</span></td><td class="field-notes">→ courses_lesson.id, CASCADE DELETE</td></tr>
      <tr><td class="field-name">title</td><td class="field-type">VARCHAR(255)</td><td>NOT NULL</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">description</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Context and motivation for the exercise</td></tr>
      <tr><td class="field-name">order</td><td class="field-type">SMALLINT</td><td>NOT NULL, CHECK &gt; 0</td><td class="field-notes">Position within lesson. UNIQUE per lesson.</td></tr>
      <tr><td class="field-name">type</td><td class="field-type">VARCHAR(20)</td><td>NOT NULL, DEFAULT 'coding'</td><td class="field-notes"><code>coding</code> | <code>written</code> | <code>interactive</code>. Determines the UI and evaluation method.</td></tr>
      <tr><td class="field-name">instructions</td><td class="field-type">TEXT</td><td>NOT NULL</td><td class="field-notes">What the student must do. Markdown supported.</td></tr>
      <tr><td class="field-name">starter_code</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Pre-filled code shown to student. Type <code>coding</code> only.</td></tr>
      <tr><td class="field-name">solution_code</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Reference solution. Never exposed to students. Type <code>coding</code> only.</td></tr>
      <tr><td class="field-name">language</td><td class="field-type">VARCHAR(30)</td><td>NULLABLE</td><td class="field-notes">Programming language for <code>coding</code> type. e.g. <code>python</code>, <code>javascript</code></td></tr>
      <tr><td class="field-name">hints</td><td class="field-type">JSONB</td><td>NOT NULL, DEFAULT '[]'</td><td class="field-notes">Ordered array of hint strings. Revealed progressively. e.g. <code>["Start with the models", "Use select_related"]</code></td></tr>
      <tr><td class="field-name">max_score</td><td class="field-type">SMALLINT</td><td>NOT NULL, DEFAULT 100, CHECK &gt; 0</td><td class="field-notes">Max score for this practice item</td></tr>
      <tr><td class="field-name">time_limit_minutes</td><td class="field-type">SMALLINT</td><td>NULLABLE, CHECK &gt; 0</td><td class="field-notes">Null = untimed. Timer managed by Assessment domain during attempt.</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">updated_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
    </table>
  </div>

  <pre>CREATE UNIQUE INDEX uq_practice_lesson_order
    ON courses_lessonpractice (lesson_id, "order");

ALTER TABLE courses_lessonpractice
    ADD CONSTRAINT chk_practice_type CHECK (type IN ('coding','written','interactive'));
</pre>
</section>

<!-- LESSON QUIZ -->
<section id="quiz">
  <h2>LessonQuiz <span class="tag">0:1 PER LESSON</span></h2>
  <p>A short knowledge-check quiz attached to a lesson. At most one quiz per lesson (unlike Practice, which can have many items). The quiz is the <em>definition</em> — student attempts and scoring live in the Assessment domain.</p>

  <div class="schema-block">
    <div class="schema-header coral">
      <h4>courses_lessonquiz</h4>
      <span>Lesson-level knowledge check — max one per lesson</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes"></td></tr>
      <tr><td class="field-name">lesson_id</td><td class="field-type">UUID</td><td><span class="badge badge-fk">FK</span> <span class="badge badge-uniq">UNIQUE</span></td><td class="field-notes">→ courses_lesson.id, CASCADE DELETE. UNIQUE = one quiz per lesson.</td></tr>
      <tr><td class="field-name">title</td><td class="field-type">VARCHAR(255)</td><td>NOT NULL</td><td class="field-notes">e.g. "Check your understanding"</td></tr>
      <tr><td class="field-name">instructions</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Shown before student starts. "Answer all questions. You have 10 minutes."</td></tr>
      <tr><td class="field-name">time_limit_minutes</td><td class="field-type">SMALLINT</td><td>NULLABLE, CHECK &gt; 0</td><td class="field-notes">Null = untimed. Timer enforced by Assessment domain during attempt.</td></tr>
      <tr><td class="field-name">pass_score</td><td class="field-type">SMALLINT</td><td>NOT NULL, DEFAULT 70, CHECK 0–100</td><td class="field-notes">Percentage threshold to pass. Assessment domain uses this to set attempt.is_passed.</td></tr>
      <tr><td class="field-name">max_attempts</td><td class="field-type">SMALLINT</td><td>NULLABLE, CHECK &gt; 0</td><td class="field-notes">Null = unlimited retakes. Assessment domain enforces this.</td></tr>
      <tr><td class="field-name">shuffle_questions</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT false</td><td class="field-notes">Randomize question order per attempt</td></tr>
      <tr><td class="field-name">shuffle_options</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT false</td><td class="field-notes">Randomize answer option order per attempt</td></tr>
      <tr><td class="field-name">show_correct_after_attempt</td><td class="field-type">BOOLEAN</td><td>NOT NULL, DEFAULT true</td><td class="field-notes">Show correct answers + explanations after submitting. False for high-stakes quizzes.</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">updated_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
    </table>
  </div>

  <pre>ALTER TABLE courses_lessonquiz
    ADD CONSTRAINT chk_quiz_pass_score CHECK (pass_score BETWEEN 0 AND 100);</pre>

  <hr>

  <!-- QUIZ QUESTION -->
  <h2 id="quiz-question" style="border-top:none;margin-top:0">QuizQuestion <span class="tag">PART OF QUIZ</span></h2>
  <p>Individual questions within a LessonQuiz. Supports four question types. Explanation field enables pedagogical feedback after answering.</p>

  <div class="schema-block">
    <div class="schema-header purple-dark">
      <h4>courses_quizquestion</h4>
      <span>Individual quiz question · four types</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes"></td></tr>
      <tr><td class="field-name">quiz_id</td><td class="field-type">UUID</td><td><span class="badge badge-fk">FK</span> NOT NULL <span class="badge badge-idx">IDX</span></td><td class="field-notes">→ courses_lessonquiz.id, CASCADE DELETE</td></tr>
      <tr><td class="field-name">type</td><td class="field-type">VARCHAR(20)</td><td>NOT NULL</td><td class="field-notes"><code>single_choice</code> | <code>multiple_choice</code> | <code>true_false</code> | <code>short_text</code></td></tr>
      <tr><td class="field-name">body</td><td class="field-type">TEXT</td><td>NOT NULL</td><td class="field-notes">The question text. Supports markdown (code blocks, bold). e.g. "What does ORM stand for?"</td></tr>
      <tr><td class="field-name">explanation</td><td class="field-type">TEXT</td><td>NULLABLE</td><td class="field-notes">Shown after answering (if <code>show_correct_after_attempt</code> = true). Explains the correct answer.</td></tr>
      <tr><td class="field-name">order</td><td class="field-type">SMALLINT</td><td>NOT NULL, CHECK &gt; 0</td><td class="field-notes">Display order. UNIQUE per quiz.</td></tr>
      <tr><td class="field-name">points</td><td class="field-type">SMALLINT</td><td>NOT NULL, DEFAULT 1, CHECK &gt; 0</td><td class="field-notes">Points awarded for correct answer. Enables weighted questions.</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
      <tr><td class="field-name">updated_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes"></td></tr>
    </table>
  </div>

  <pre>CREATE UNIQUE INDEX uq_question_quiz_order
    ON courses_quizquestion (quiz_id, "order");

ALTER TABLE courses_quizquestion
    ADD CONSTRAINT chk_question_type CHECK (
        type IN ('single_choice','multiple_choice','true_false','short_text')
    );</pre>

  <hr>

  <!-- QUIZ OPTION -->
  <h2 id="quiz-option" style="border-top:none;margin-top:0">QuizOption <span class="tag">ANSWER CHOICE</span></h2>
  <p>Answer options for choice-based questions. Each option is marked correct or not. Multiple options can be correct (for <code>multiple_choice</code> type). For <code>true_false</code> and <code>short_text</code> types, options are unused — correctness is handled by the Assessment domain.</p>

  <div class="schema-block">
    <div class="schema-header purple-dark">
      <h4>courses_quizoption</h4>
      <span>Answer option for single_choice / multiple_choice / true_false</span>
    </div>
    <table class="schema-table">
      <tr><th>Field</th><th>Type</th><th>Constraints</th><th>Notes</th></tr>
      <tr><td class="field-name">id</td><td class="field-type">UUID</td><td><span class="badge badge-pk">PK</span></td><td class="field-notes"></td></tr>
      <tr><td class="field-name">question_id</td><td class="field-type">UUID</td><td><span class="badge badge-fk">FK</span> NOT NULL <span class="badge badge-idx">IDX</span></td><td class="field-notes">→ courses_quizquestion.id, CASCADE DELETE</td></tr>
      <tr><td class="field-name">body</td><td class="field-type">TEXT</td><td>NOT NULL</td><td class="field-notes">Option text. e.g. "Object-Relational Mapper"</td></tr>
      <tr><td class="field-name">is_correct</td><td class="field-type">BOOLEAN</td><td>NOT NULL</td><td class="field-notes">Marked correct. Multiple options can be correct for <code>multiple_choice</code>.</td></tr>
      <tr><td class="field-name">order</td><td class="field-type">SMALLINT</td><td>NOT NULL, CHECK &gt; 0</td><td class="field-notes">Base display order (shuffled at runtime if <code>shuffle_options</code> = true)</td></tr>
      <tr><td class="field-name">created_at</td><td class="field-type">TIMESTAMPTZ</td><td>NOT NULL, DEFAULT now()</td><td class="field-notes">No updated_at — options are replaced, not updated</td></tr>
    </table>
  </div>

  <pre>CREATE UNIQUE INDEX uq_option_question_order
    ON courses_quizoption (question_id, "order");

-- For single_choice: exactly one option can be correct
-- Enforced at application layer, not DB level (too complex for a CHECK constraint)
-- Service method validates: len([o for o in options if o.is_correct]) == 1</pre>
</section>

<!-- ERD -->
<section id="erd">
  <h2>ERD Relationships <span class="tag">FULL MAP</span></h2>

  <div class="erd-container">
    <div class="erd-section">
      <h5>Cross-Domain (real DB FK — monolith)</h5>
      <div class="erd-row">
        <div class="erd-box ext">accounts_user</div>
        <div class="erd-line">──FK created_by──▶</div>
        <div class="erd-box core">Course</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;SET NULL on delete</div>
      </div>
      <div class="erd-row" style="margin-top:6px">
        <div class="erd-box ext">accounts_user</div>
        <div class="erd-line">──FK user_id──────▶</div>
        <div class="erd-box core">CourseEnrollment</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;PROTECT on delete</div>
      </div>
      <div class="erd-row" style="margin-top:6px">
        <div class="erd-box ext">accounts_user</div>
        <div class="erd-line">──FK enrolled_by──▶</div>
        <div class="erd-box core">CourseEnrollment</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;SET NULL on delete, NULLABLE</div>
      </div>
    </div>

    <div class="erd-section">
      <h5>Catalog Structure</h5>
      <div class="erd-row">
        <div class="erd-box content">CourseCategory</div>
        <div class="erd-line">&nbsp;0..1 (parent) ────▶</div>
        <div class="erd-box content">CourseCategory</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;self-referential, max 2 levels</div>
      </div>
      <div class="erd-row" style="margin-top:6px">
        <div class="erd-box content">CourseCategory</div>
        <div class="erd-line">&nbsp;1 ────────── N▶</div>
        <div class="erd-box core">Course</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;SET NULL on delete (nullable FK)</div>
      </div>
    </div>

    <div class="erd-section">
      <h5>Core Structure (DB FK with CASCADE)</h5>
      <div class="erd-row">
        <div class="erd-box core">Course</div>
        <div class="erd-line">&nbsp;1 ──────────────── N▶</div>
        <div class="erd-box core">Module</div>
        <div class="erd-line">&nbsp;1 ──────────────── N▶</div>
        <div class="erd-box core">Lesson</div>
      </div>
      <div class="erd-row" style="margin-top:6px">
        <div class="erd-box core">Course</div>
        <div class="erd-line">&nbsp;1 ──────────────── N▶</div>
        <div class="erd-box sky" style="border-color:var(--sky);background:var(--sky-light);color:var(--sky)">CourseEnrollment</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;(RESTRICT delete)</div>
      </div>
    </div>

    <div class="erd-section">
      <h5>Lesson Components</h5>
      <div class="erd-row">
        <div class="erd-box core">Lesson</div>
        <div class="erd-line">&nbsp;1 ──────────────── N▶</div>
        <div class="erd-box content">LessonContent</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;&nbsp;ordered by "order"</div>
      </div>
      <div class="erd-row" style="margin-top:6px">
        <div class="erd-box core">Lesson</div>
        <div class="erd-line">&nbsp;1 ──────────── 0..1▶</div>
        <div class="erd-box hw">LessonHomework</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;&nbsp;optional, UNIQUE(lesson_id)</div>
      </div>
      <div class="erd-row" style="margin-top:6px">
        <div class="erd-box core">Lesson</div>
        <div class="erd-line">&nbsp;1 ──────────────── N▶</div>
        <div class="erd-box hw">LessonPractice</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;&nbsp;ordered by "order"</div>
      </div>
      <div class="erd-row" style="margin-top:6px">
        <div class="erd-box core">Lesson</div>
        <div class="erd-line">&nbsp;1 ──────────── 0..1▶</div>
        <div class="erd-box quiz">LessonQuiz</div>
        <div class="erd-line">&nbsp;&nbsp;&nbsp;&nbsp;optional, UNIQUE(lesson_id)</div>
      </div>
    </div>

    <div class="erd-section">
      <h5>Quiz Sub-structure</h5>
      <div class="erd-row">
        <div class="erd-box quiz">LessonQuiz</div>
        <div class="erd-line">&nbsp;1 ──────────────── N▶</div>
        <div class="erd-box quiz">QuizQuestion</div>
        <div class="erd-line">&nbsp;1 ──────────────── N▶</div>
        <div class="erd-box quiz">QuizOption</div>
      </div>
    </div>

    <div class="erd-section" style="margin-bottom:0">
      <h5>Consumed by other domains (IDs referenced, no DB FK)</h5>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <div style="font-size:12px;color:var(--text-muted)"><code>Lesson.id</code> → UserProgress domain</div>
        <div style="font-size:12px;color:var(--text-muted)">·</div>
        <div style="font-size:12px;color:var(--text-muted)"><code>LessonHomework.id</code> → Submissions domain</div>
        <div style="font-size:12px;color:var(--text-muted)">·</div>
        <div style="font-size:12px;color:var(--text-muted)"><code>LessonQuiz.id</code> → Assessment domain</div>
        <div style="font-size:12px;color:var(--text-muted)">·</div>
        <div style="font-size:12px;color:var(--text-muted)"><code>LessonPractice.id</code> → Assessment domain</div>
        <div style="font-size:12px;color:var(--text-muted)">·</div>
        <div style="font-size:12px;color:var(--text-muted)"><code>CourseEnrollment.id</code> → Analytics, Certificate domains</div>
      </div>
    </div>
  </div>
</section>

<!-- DESIGN DECISIONS -->
<section id="decisions">
  <h2>Design Decisions <span class="tag">RATIONALE</span></h2>

  <div class="decision-grid">
    <div class="decision-card">
      <h4>Single LessonContent table (no table-per-type)</h4>
      <p>A unified table with a <code>type</code> discriminator + JSONB <code>metadata</code> handles all content types. Adding a new content type (e.g., <code>interactive</code>) is a config change, not a migration. The alternative — 7 separate tables — would require 7 JOINs to load a lesson's content in order.</p>
    </div>
    <div class="decision-card teal">
      <h4>UNIQUE(parent_id, order) — not gaps, not floats</h4>
      <p>Integer ordering with a UNIQUE constraint enforces no duplicates at the DB level. Reordering is done in a transaction using a two-step swap (displace to a temp value, then set target). Simpler than floating-point order values, avoids eventual precision collapse.</p>
    </div>
    <div class="decision-card coral">
      <h4>LessonHomework 1:1, LessonPractice 1:N</h4>
      <p>One homework per lesson = cleaner student UX (one deadline, one submission per lesson). Multiple practices per lesson = pedagogically correct (several exercises build a skill). Different cardinality = different models of interaction.</p>
    </div>
    <div class="decision-card amber">
      <h4>Soft delete on Course/Module/Lesson only</h4>
      <p>Content, Homework, Practice, Quiz are children of Lesson. Soft-deleting the Lesson is sufficient to hide everything below it. Content items themselves are replaced, not archived — hard delete is safe and avoids orphaned records.</p>
    </div>
    <div class="decision-card sky">
      <h4>Real DB FK while in monolith</h4>
      <p>Both <code>accounts</code> and <code>courses</code> apps share one PostgreSQL database. Real <code>ForeignKey</code> to <code>AUTH_USER_MODEL</code> gives cascade semantics, ORM <code>select_related</code>, and DB-level integrity for free. Soft UUID references add application complexity with zero benefit in a single-DB setup. When microservices become a reality, remove FK in one migration.</p>
    </div>
    <div class="decision-card coral">
      <h4>delivery_format on CourseEnrollment, not Course</h4>
      <p>A single "Python Backend" course can have students enrolled online and offline simultaneously. Putting <code>mode</code> on <code>Course</code> would force duplicate courses — "Python Backend Online" and "Python Backend Offline" — with identical content that must be maintained in parallel. Instead, <code>Course</code> declares supported formats via boolean flags; <code>CourseEnrollment.delivery_format</code> records each student's choice.</p>
    </div>
    <div class="decision-card teal">
      <h4>CourseCategory as single FK, not junction</h4>
      <p>One course has one primary category. A junction table (<code>CourseCategoryAssignment</code>) is premature — it adds a join to every catalog query without a clear product need today. The single FK covers 95% of cases. If multi-tagging is required in the future, add the junction table; existing category_id data migrates cleanly.</p>
    </div>
    <div class="decision-card gray">
      <h4>is_sequential on Course, not Module</h4>
      <p>Sequential ordering is a course-wide decision. Having it per-module adds complexity without clear benefit — if some modules are free and some sequential, the unlock logic becomes ambiguous. Start simple: course-wide toggle. Per-module overrides are a future extension if the product needs it.</p>
    </div>
    <div class="decision-card">
      <h4>pass_score and max_attempts live in LessonQuiz</h4>
      <p>These are content configuration values set by the course author, not runtime state. They belong in the Learning Domain alongside the quiz definition. The Assessment domain reads them when creating attempts and computing pass/fail — it never writes them.</p>
    </div>
    <div class="decision-card teal">
      <h4>deadline_offset_days, not deadline_date</h4>
      <p>A relative deadline (N days after the lesson unlocks) is far more maintainable than an absolute date. If a course is re-run or a student is given a late-start exception, no homework dates need updating. The absolute deadline is computed at submission time by the Submissions domain: <code>lesson_unlocked_at + offset_days</code>.</p>
    </div>
  </div>
</section>

<!-- INDEXES -->
<section id="indexes">
  <h2>Indexes &amp; Constraints Summary <span class="tag">PERFORMANCE</span></h2>

  <table>
    <tr><th>Table</th><th>Index</th><th>Purpose</th></tr>
    <tr><td><code>courses_course</code></td><td>UNIQUE <code>(slug)</code></td><td>URL routing — most frequent course lookup</td></tr>
    <tr><td><code>courses_course</code></td><td>PARTIAL <code>(status)</code> WHERE not deleted</td><td>Catalog listing filtered by published status</td></tr>
    <tr><td><code>courses_course</code></td><td><code>(category_id)</code> WHERE not deleted</td><td>Catalog filtered by category (hot path)</td></tr>
    <tr><td><code>courses_coursecategory</code></td><td>UNIQUE <code>(slug)</code></td><td>URL routing for category pages</td></tr>
    <tr><td><code>courses_coursecategory</code></td><td><code>(parent_id, order)</code> WHERE active</td><td>Sidebar/filter listing of categories in order</td></tr>
    <tr><td><code>courses_module</code></td><td>UNIQUE <code>(course_id, order)</code> WHERE not deleted</td><td>Ordered module listing, integrity on reorder</td></tr>
    <tr><td><code>courses_module</code></td><td>PARTIAL <code>(course_id, order)</code> WHERE published</td><td>Student-facing module list (hot path)</td></tr>
    <tr><td><code>courses_lesson</code></td><td>UNIQUE <code>(module_id, order)</code> WHERE not deleted</td><td>Ordered lesson listing, integrity</td></tr>
    <tr><td><code>courses_lesson</code></td><td>PARTIAL <code>(module_id, order)</code> WHERE published</td><td>Student-facing lesson list (hot path)</td></tr>
    <tr><td><code>courses_courseenrollment</code></td><td>UNIQUE <code>(user_id, course_id)</code></td><td>Prevent duplicate enrollments</td></tr>
    <tr><td><code>courses_courseenrollment</code></td><td><code>(user_id, status)</code></td><td>Student dashboard — active courses</td></tr>
    <tr><td><code>courses_courseenrollment</code></td><td><code>(course_id, status)</code></td><td>Mentor/admin — students in a course</td></tr>
    <tr><td><code>courses_lessoncontent</code></td><td>UNIQUE <code>(lesson_id, order)</code></td><td>Ordered content rendering</td></tr>
    <tr><td><code>courses_lessoncontent</code></td><td><code>(type, lesson_id)</code></td><td>Filter content by type (e.g., list all videos)</td></tr>
    <tr><td><code>courses_lessonhomework</code></td><td>UNIQUE <code>(lesson_id)</code></td><td>Enforce one homework per lesson</td></tr>
    <tr><td><code>courses_lessonpractice</code></td><td>UNIQUE <code>(lesson_id, order)</code></td><td>Ordered practice items</td></tr>
    <tr><td><code>courses_lessonquiz</code></td><td>UNIQUE <code>(lesson_id)</code></td><td>Enforce one quiz per lesson</td></tr>
    <tr><td><code>courses_quizquestion</code></td><td>UNIQUE <code>(quiz_id, order)</code></td><td>Ordered question listing</td></tr>
    <tr><td><code>courses_quizoption</code></td><td>UNIQUE <code>(question_id, order)</code></td><td>Ordered option listing</td></tr>
  </table>

  <div class="callout sky">
    <strong>Partial indexes:</strong> All indexes on published/active records use <code>WHERE deleted_at IS NULL</code> or <code>WHERE is_published = TRUE</code>. This keeps index size small — deleted/draft records are excluded. Student-facing queries always filter on published state and benefit from these partial indexes automatically.
  </div>
</section>

<!-- CROSS DOMAIN -->
<section id="cross-domain">
  <h2>Cross-Domain References <span class="tag">BOUNDARIES</span></h2>
  <p>All cross-domain references within the monolith now use real DB-level <code>ForeignKey</code> constraints. The "soft UUID" pattern is reserved for when services are actually extracted.</p>

  <table>
    <tr><th>Field</th><th>References</th><th>Direction</th><th>on_delete</th></tr>
    <tr>
      <td><code>Course.created_by</code></td>
      <td><code>accounts_user.id</code></td>
      <td>Learning → Identity</td>
      <td>SET NULL — course persists if creator account deleted</td>
    </tr>
    <tr>
      <td><code>CourseEnrollment.user</code></td>
      <td><code>accounts_user.id</code></td>
      <td>Learning → Identity</td>
      <td>PROTECT — handle user deletion explicitly via signal; set status=dropped then delete or anonymise</td>
    </tr>
    <tr>
      <td><code>CourseEnrollment.enrolled_by</code></td>
      <td><code>accounts_user.id</code></td>
      <td>Learning → Identity</td>
      <td>SET NULL — audit field; safe to nullify if enrolling admin deleted</td>
    </tr>
    <tr>
      <td><code>Course.category</code></td>
      <td><code>courses_coursecategory.id</code></td>
      <td>Internal Learning Domain</td>
      <td>SET NULL — course becomes uncategorised if category deleted</td>
    </tr>
    <tr>
      <td><code>Lesson.id</code></td>
      <td>Used by UserProgress domain</td>
      <td>UserProgress → Learning</td>
      <td>UserProgress stores lesson_id. Learning domain never writes to UserProgress.</td>
    </tr>
    <tr>
      <td><code>LessonHomework.id</code></td>
      <td>Used by Submissions domain</td>
      <td>Submissions → Learning</td>
      <td>Submission stores homework_id. Homework definition read-only from Submissions.</td>
    </tr>
    <tr>
      <td><code>LessonQuiz.id</code>, <code>LessonPractice.id</code></td>
      <td>Used by Assessment domain</td>
      <td>Assessment → Learning</td>
      <td>Assessment stores quiz/practice IDs. Quiz definition read-only from Assessment.</td>
    </tr>
  </table>
</section>

<!-- FUTURE EXTENSIONS -->
<section id="future">
  <h2>Future Extensions <span class="tag">NOT IMPLEMENTED</span></h2>
  <p>These are identified extension points for the Learning Domain. None are implemented now. The current schema is designed to accommodate them with minimal breaking changes.</p>

  <div class="future-grid">
    <div class="future-card">
      <h4>📋 Prerequisites</h4>
      <p>A <code>ModulePrerequisite</code> junction table (<code>module_id</code> + <code>required_module_id</code>) would let admins define "complete Module 2 before unlocking Module 5." Currently the sequential boolean covers 95% of cases.</p>
    </div>
    <div class="future-card">
      <h4>📝 Lesson Versioning</h4>
      <p>A <code>LessonVersion</code> table with snapshots of content and metadata. Allows rollback after an edit and tracks what version each student saw. The current model has no version history.</p>
    </div>
    <div class="future-card">
      <h4>🌍 Localization</h4>
      <p>A <code>CourseTranslation</code> / <code>LessonTranslation</code> table pattern. The base table stores the primary language; translations store <code>locale</code> + translated fields. The <code>language</code> field on Course prepares for this.</p>
    </div>
    <div class="future-card">
      <h4>⏰ Content Release Scheduling</h4>
      <p>A <code>publish_at</code> TIMESTAMPTZ on Module and Lesson. Celery beat job promotes <code>is_published = false → true</code> at scheduled time. Useful for drip-release courses.</p>
    </div>
    <div class="future-card">
      <h4>🔀 Learning Paths</h4>
      <p>A <code>LearningPath</code> table with an ordered sequence of Courses. Allows "complete these 3 courses to earn the Backend Developer track" cross-course sequences.</p>
    </div>
    <div class="future-card">
      <h4>🏷 Multi-Category Tagging</h4>
      <p>A <code>CourseCategoryAssignment</code> junction table (<code>course_id</code> + <code>category_id</code>) for courses that span multiple domains (e.g., "Full Stack" in both Frontend and Backend). Current single FK covers 95% of cases; add junction only if the product confirms multi-tag need.</p>
    </div>
    <div class="future-card">
      <h4>🌿 Branching Lessons</h4>
      <p>Adaptive learning: after a LessonQuiz, route students to different lessons based on score. Requires a <code>LessonBranch</code> conditional routing table. Complex; deferred until product confirms need.</p>
    </div>
    <div class="future-card">
      <h4>👥 Co-authoring</h4>
      <p>A <code>CourseAuthor</code> junction table to allow multiple staff members to edit the same course. Currently only <code>created_by_id</code> is tracked.</p>
    </div>
    <div class="future-card">
      <h4>✅ Content Approval Workflow</h4>
      <p>A <code>review_status</code> field on LessonContent with states <code>draft → in_review → approved</code>. Required when content is created by contractors or external instructors who need editorial sign-off before publishing.</p>
    </div>
  </div>

  <div class="callout success">
    <strong>Design principle applied:</strong> Every future extension above can be added as a new table or a new nullable column — none require changing the primary keys, relationships, or constraints of the current schema. This is the mark of a well-normalized foundation.
  </div>
</section>

</main>
</div>
</body>
</html>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LearnFlow — UserProgress Domain Architecture Review v2</title>
<style>
  :root {
    --accent: #534AB7; --accent-light: #EEEDFE; --accent-mid: #AFA9EC;
    --teal: #0F6E56;   --teal-light: #E1F5EE;
    --coral: #993C1D;  --coral-light: #FAECE7;
    --amber: #854F0B;  --amber-light: #FAEEDA;
    --sky: #0C5E8A;    --sky-light: #E0F2FE;
    --gray: #444441;   --gray-light: #F1EFE8;
    --green: #166534;  --green-light: #dcfce7;
    --red: #991b1b;    --red-light: #fee2e2;
    --orange: #9a3412; --orange-light: #ffedd5;
    --text: #1a1a18; --text-muted: #5F5E5A;
    --border: #D3D1C7; --bg: #ffffff; --bg-page: #f7f6f2; --code-bg: #F1EFE8;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:-apple-system,'Segoe UI',Arial,sans-serif; font-size:15px; line-height:1.7; color:var(--text); background:var(--bg-page); }
  .layout { display:flex; min-height:100vh; }

  nav { width:270px; min-width:270px; background:var(--bg); border-right:1px solid var(--border); padding:24px 0; position:sticky; top:0; height:100vh; overflow-y:auto; }
  nav .logo { padding:0 20px 16px; border-bottom:1px solid var(--border); margin-bottom:12px; }
  nav .logo h1 { font-size:14px; font-weight:700; color:var(--red); line-height:1.3; }
  nav .logo p  { font-size:11px; color:var(--text-muted); margin-top:3px; }
  nav a { display:block; padding:6px 20px; font-size:12.5px; color:var(--text-muted); text-decoration:none; border-left:2px solid transparent; transition:all 0.15s; }
  nav a:hover { color:var(--accent); background:var(--accent-light); border-left-color:var(--accent); }
  nav .section-label { padding:13px 20px 3px; font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); }
  nav a.sub { padding-left:32px; font-size:12px; }

  main { flex:1; padding:48px 56px; max-width:1060px; }
  section { margin-bottom:72px; }

  h2 { font-size:25px; font-weight:700; color:var(--text); margin-bottom:8px; padding-bottom:12px; border-bottom:2px solid var(--accent-light); }
  h2 .tag { display:inline-block; font-size:11px; font-weight:500; background:var(--accent-light); color:var(--accent); padding:2px 8px; border-radius:4px; margin-left:10px; vertical-align:middle; }
  h3 { font-size:18px; font-weight:700; color:var(--text); margin:32px 0 12px; }
  h4 { font-size:14px; font-weight:700; color:var(--text); margin:14px 0 6px; }
  p  { margin-bottom:12px; color:var(--text-muted); font-size:14px; }
  pre { background:var(--code-bg); border:1px solid var(--border); border-radius:8px; padding:14px 18px; font-family:'SF Mono','Fira Code',monospace; font-size:12px; line-height:1.7; overflow-x:auto; margin:10px 0; color:var(--text); }
  code { background:var(--code-bg); font-family:'SF Mono','Fira Code',monospace; font-size:12px; padding:1px 5px; border-radius:3px; color:var(--accent); }
  table { width:100%; border-collapse:collapse; margin:14px 0; font-size:13px; }
  th { background:var(--gray-light); font-weight:700; text-align:left; padding:9px 13px; border-bottom:2px solid var(--border); font-size:11px; text-transform:uppercase; letter-spacing:0.04em; }
  td { padding:8px 13px; border-bottom:1px solid var(--border); vertical-align:top; font-size:13px; }
  tr:last-child td { border-bottom:none; }

  /* Severity badges */
  .sev { display:inline-flex; align-items:center; gap:5px; font-size:11px; font-weight:700; padding:3px 9px; border-radius:4px; text-transform:uppercase; letter-spacing:0.05em; white-space:nowrap; }
  .sev-critical { background:var(--red-light);    color:var(--red); }
  .sev-high     { background:var(--orange-light);  color:var(--orange); }
  .sev-medium   { background:var(--amber-light);   color:var(--amber); }
  .sev-low      { background:var(--teal-light);    color:var(--teal); }

  /* Finding cards */
  .finding { background:var(--bg); border:1px solid var(--border); border-radius:12px; margin-bottom:20px; overflow:hidden; }
  .finding-header { padding:12px 18px; display:flex; align-items:center; justify-content:space-between; gap:12px; border-bottom:1px solid var(--border); }
  .finding-header.critical { background:var(--red-light);    border-bottom-color:#fecaca; }
  .finding-header.high     { background:var(--orange-light);  border-bottom-color:#fed7aa; }
  .finding-header.medium   { background:var(--amber-light);   border-bottom-color:#fde68a; }
  .finding-header.low      { background:var(--teal-light);    border-bottom-color:#a7f3d0; }
  .finding-id   { font-family:'SF Mono',monospace; font-size:11px; font-weight:700; color:var(--text-muted); min-width:48px; }
  .finding-title { font-size:14px; font-weight:700; color:var(--text); flex:1; }
  .finding-body { padding:16px 18px; }
  .finding-body h4 { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:var(--text-muted); margin:14px 0 5px; }
  .finding-body h4:first-child { margin-top:0; }
  .finding-body p  { font-size:13.5px; margin-bottom:8px; }
  .finding-body p:last-child { margin-bottom:0; }

  /* Before/After blocks */
  .diff-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:12px 0; }
  .diff-block { border-radius:8px; overflow:hidden; }
  .diff-block .diff-label { padding:6px 12px; font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; }
  .diff-block.before .diff-label { background:#fee2e2; color:var(--red); }
  .diff-block.after  .diff-label { background:var(--teal-light); color:var(--teal); }
  .diff-block pre { margin:0; border-radius:0; border:none; border-top:1px solid var(--border); font-size:11.5px; }
  .diff-block.before pre { background:#fff8f8; }
  .diff-block.after  pre { background:#f0fdf4; }

  /* Callouts */
  .callout { border-left:3px solid var(--accent); background:var(--accent-light); border-radius:0 8px 8px 0; padding:13px 16px; margin:14px 0; font-size:13.5px; color:var(--text); }
  .callout.warning { border-color:var(--amber); background:var(--amber-light); }
  .callout.success { border-color:var(--teal);  background:var(--teal-light); }
  .callout.sky     { border-color:var(--sky);   background:var(--sky-light); }
  .callout.danger  { border-color:var(--red);   background:var(--red-light); }

  /* Summary table */
  .summary-table td:first-child { font-family:'SF Mono',monospace; font-size:12px; font-weight:600; }
  .summary-table td:nth-child(2){ font-size:13px; }

  /* Executive verdict */
  .verdict-bar { display:grid; grid-template-columns:repeat(4,1fr); gap:0; border:1px solid var(--border); border-radius:10px; overflow:hidden; margin:20px 0; }
  .verdict-cell { padding:16px 18px; border-right:1px solid var(--border); }
  .verdict-cell:last-child { border-right:none; }
  .verdict-num  { font-size:32px; font-weight:800; font-family:'SF Mono',monospace; line-height:1; }
  .verdict-label { font-size:11px; text-transform:uppercase; letter-spacing:0.07em; color:var(--text-muted); margin-top:4px; }

  /* Recommendation blocks */
  .rec-block { background:var(--teal-light); border:1px solid #a7f3d0; border-radius:8px; padding:14px 18px; margin:12px 0; }
  .rec-block h4 { color:var(--teal); margin-top:0; font-size:13px; }
  .rec-block p  { font-size:13px; margin-bottom:0; }

  /* Section header with area label */
  .area-header { display:flex; align-items:center; gap:12px; margin-bottom:16px; }
  .area-num { background:var(--accent); color:white; border-radius:50%; width:32px; height:32px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:14px; flex-shrink:0; }
  .area-num.red    { background:var(--red); }
  .area-num.amber  { background:var(--amber); }
  .area-num.teal   { background:var(--teal); }
  .area-num.sky    { background:var(--sky); }
  .area-num.coral  { background:var(--coral); }
  .area-num.gray   { background:var(--gray); }

  /* Change table */
  .change-table td:nth-child(3) { font-size:12.5px; }
  .change-added   { background:#f0fdf4; }
  .change-modified{ background:#fffbeb; }
  .change-removed { background:#fff1f2; }

  hr { border:none; border-top:1px solid var(--border); margin:24px 0; }
  @media (max-width:1100px) { nav { display:none; } main { padding:24px 20px; } }
  @media (max-width:700px)  { .diff-grid { grid-template-columns:1fr; } .verdict-bar { grid-template-columns:1fr 1fr; } }
</style>
</head>
<body>
<div class="layout">

<!-- SIDEBAR -->
<nav>
  <div class="logo">
    <h1>Architecture Review<br>UserProgress Domain v2</h1>
    <p>Staff Engineer · LearnFlow</p>
  </div>
  <div class="section-label">Overview</div>
  <a href="#executive">Executive Summary</a>
  <a href="#issue-index">Issue Index</a>
  <div class="section-label">Area 1 · Counters</div>
  <a class="sub" href="#F1">F1 · O(n) fan-out on content delete</a>
  <a class="sub" href="#F2">F2 · Race condition: lost increments</a>
  <a class="sub" href="#F3">F3 · Counter drift on completed lessons</a>
  <a class="sub" href="#F4">F4 · Missing LessonContentAdded handler</a>
  <a class="sub" href="#F5">F5 · Broken CHECK constraint tolerance</a>
  <div class="section-label">Area 2 · Percentage</div>
  <a class="sub" href="#F6">F6 · Module-granularity is misleading</a>
  <a class="sub" href="#F7">F7 · assessment_pending counts as 0%</a>
  <div class="section-label">Area 3 · Continue Learning</div>
  <a class="sub" href="#F8">F8 · Cross-module lesson ordering bug</a>
  <a class="sub" href="#F9">F9 · in_progress vs unlocked priority inversion</a>
  <a class="sub" href="#F10">F10 · assessment_pending dead-end</a>
  <a class="sub" href="#F11">F11 · Non-sequential continue is wrong</a>
  <div class="section-label">Area 4 · Online / Offline</div>
  <a class="sub" href="#F12">F12 · Attendance bypasses homework gate</a>
  <a class="sub" href="#F13">F13 · No AttendanceRevoked path</a>
  <a class="sub" href="#F14">F14 · Delivery format change mid-course</a>
  <div class="section-label">Area 5 · Content Tracking</div>
  <a class="sub" href="#F15">F15 · Video viewed ≠ video watched</a>
  <a class="sub" href="#F16">F16 · is_required change not handled</a>
  <a class="sub" href="#F17">F17 · Next-module first-lesson not unlocked</a>
  <div class="section-label">Additional</div>
  <a class="sub" href="#F18">F18 · Bulk attendance race condition</a>
  <a class="sub" href="#F19">F19 · Re-enroll progress reset</a>
  <a class="sub" href="#F20">F20 · Override audit trail missing</a>
  <div class="section-label">Resolution</div>
  <a href="#schema-changes">Schema Changes v2</a>
  <a href="#algorithm-changes">Algorithm Changes v2</a>
</nav>

<!-- MAIN -->
<main>

<!-- ═══ EXECUTIVE SUMMARY ═══ -->
<section id="executive">
  <h2>Executive Summary <span class="tag">STAFF REVIEW</span></h2>

  <p>The v1 architecture is structurally sound — the four-table hierarchy, snapshot strategy, and synchronous cascade are the right foundations. However, there are <strong>20 issues</strong> ranging from correctness bugs that will surface on day one to scalability problems that only appear under load. None require a full redesign, but several require non-trivial algorithm changes before implementation begins.</p>

  <div class="verdict-bar">
    <div class="verdict-cell" style="background:var(--red-light)">
      <div class="verdict-num" style="color:var(--red)">4</div>
      <div class="verdict-label">🔴 Critical — data corruption or permanent stuck states</div>
    </div>
    <div class="verdict-cell" style="background:var(--orange-light)">
      <div class="verdict-num" style="color:var(--orange)">7</div>
      <div class="verdict-label">🟠 High — breaks at scale or for offline students</div>
    </div>
    <div class="verdict-cell" style="background:var(--amber-light)">
      <div class="verdict-num" style="color:var(--amber)">6</div>
      <div class="verdict-label">🟡 Medium — edge cases that produce wrong behaviour</div>
    </div>
    <div class="verdict-cell" style="background:var(--teal-light)">
      <div class="verdict-num" style="color:var(--teal)">3</div>
      <div class="verdict-label">🟢 Low — improvements worth making before ship</div>
    </div>
  </div>

  <div class="callout danger">
    <strong>Do not implement v1 as written.</strong> F2 (lost counter increments) and F18 (bulk attendance race condition) will cause students to get permanently stuck in <code>in_progress</code> with no recovery path except a manual admin override. F8 (ordering bug) will send students to the wrong next lesson on every sequential course. These three alone block implementation.
  </div>

  <div class="callout success">
    <strong>What v1 gets right:</strong> The four-table structure, snapshot-at-enrollment strategy, the synchronous cascade pattern, <code>completion_source</code> as the online/offline differentiator, and post-commit event dispatch are all correct decisions worth keeping. The review below is about <em>fixing</em> the implementation detail, not replacing the foundation.
  </div>
</section>

<!-- ═══ ISSUE INDEX ═══ -->
<section id="issue-index">
  <h2>Issue Index <span class="tag">20 FINDINGS</span></h2>
  <table class="summary-table">
    <tr><th>ID</th><th>Finding</th><th>Area</th><th>Severity</th></tr>
    <tr><td>F1</td><td>O(n) DB fan-out when content is deleted — synchronous event handler blocks</td><td>Counters</td><td><span class="sev sev-critical">Critical</span></td></tr>
    <tr><td>F2</td><td>Race condition on <code>viewed_required_count</code> — lost increments cause permanent stuck state</td><td>Counters</td><td><span class="sev sev-critical">Critical</span></td></tr>
    <tr><td>F3</td><td>Counter drift on already-completed lessons — inconsistent state after content addition</td><td>Counters</td><td><span class="sev sev-high">High</span></td></tr>
    <tr><td>F4</td><td>No handler for <code>LessonContentAdded</code> — new required content never increments snapshots</td><td>Counters</td><td><span class="sev sev-high">High</span></td></tr>
    <tr><td>F5</td><td><code>CHECK viewed ≤ required + 1</code> is wrong — masks real drift, won't catch multi-step errors</td><td>Counters</td><td><span class="sev sev-low">Low</span></td></tr>
    <tr><td>F6</td><td>Module-granularity percentage is misleading — equal weight to a 1-lesson and a 20-lesson module</td><td>Percentage</td><td><span class="sev sev-high">High</span></td></tr>
    <tr><td>F7</td><td><code>assessment_pending</code> shows 0% credit for completed lessons — discourages students</td><td>Percentage</td><td><span class="sev sev-medium">Medium</span></td></tr>
    <tr><td>F8</td><td>Cross-module <code>lesson_order</code> comparison has no <code>module_order</code> — sends students to wrong lesson</td><td>Continue</td><td><span class="sev sev-critical">Critical</span></td></tr>
    <tr><td>F9</td><td><code>in_progress</code> vs <code>unlocked</code> priority is inverted — abandons mid-lesson student</td><td>Continue</td><td><span class="sev sev-high">High</span></td></tr>
    <tr><td>F10</td><td><code>assessment_pending</code> returns <code>next_lesson: null</code> with no action signal — dead-end UX</td><td>Continue</td><td><span class="sev sev-high">High</span></td></tr>
    <tr><td>F11</td><td>Non-sequential "continue" returns first-by-order instead of last-active</td><td>Continue</td><td><span class="sev sev-medium">Medium</span></td></tr>
    <tr><td>F12</td><td>Attendance bypasses homework gate — students can complete lessons without submitting work</td><td>Offline</td><td><span class="sev sev-high">High</span></td></tr>
    <tr><td>F13</td><td>No <code>AttendanceRevoked</code> path — mentor mistakes are permanent</td><td>Offline</td><td><span class="sev sev-medium">Medium</span></td></tr>
    <tr><td>F14</td><td>Delivery format change mid-course leaves completion logic using stale context</td><td>Offline</td><td><span class="sev sev-medium">Medium</span></td></tr>
    <tr><td>F15</td><td>One API call marks a 2-hour video as "viewed" — no watch threshold enforced</td><td>Content</td><td><span class="sev sev-medium">Medium</span></td></tr>
    <tr><td>F16</td><td><code>is_required</code> flag change on existing content is not handled — counters diverge</td><td>Content</td><td><span class="sev sev-medium">Medium</span></td></tr>
    <tr><td>F17</td><td><code>_unlock_next_module</code> never unlocks the first lesson of the next module</td><td>Content</td><td><span class="sev sev-critical">Critical</span></td></tr>
    <tr><td>F18</td><td>Bulk offline attendance race condition — concurrent <code>_check_module_completion</code> calls without row locking</td><td>Additional</td><td><span class="sev sev-critical">Critical</span></td></tr>
    <tr><td>F19</td><td>Re-enroll after drop resets progress to zero — product decision not made explicit</td><td>Additional</td><td><span class="sev sev-low">Low</span></td></tr>
    <tr><td>F20</td><td>Admin override has no audit trail in the schema — <code>reason</code> is API-only and discarded</td><td>Additional</td><td><span class="sev sev-low">Low</span></td></tr>
  </table>
</section>

<!-- ═══ AREA 1: COUNTERS ═══ -->
<section id="area1">
  <div class="area-header">
    <div class="area-num red">1</div>
    <h2 style="border:none; padding:0; margin:0;">Snapshot Counter Scalability</h2>
  </div>

  <div class="finding" id="F1">
    <div class="finding-header critical">
      <span class="finding-id">F1</span>
      <span class="finding-title">O(n) synchronous fan-out when content is deleted</span>
      <span class="sev sev-critical">Critical</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The <code>handle_content_deleted</code> handler updates <code>required_content_count</code> and <code>viewed_required_count</code> on every <code>LessonProgress</code> row for every enrolled student in the course. It then conditionally calls <code>_check_lesson_completion</code> for each affected row. All of this runs inside the same synchronous event handler — blocking the request thread of whichever staff member deleted the content item.</p>
      <h4>Impact</h4>
      <p>A popular course with 10,000 active enrollments triggers 10,000 <code>LessonProgress</code> reads, up to 10,000 <code>LessonContentView</code> existence checks, up to 10,000 counter writes, and up to 10,000 <code>_check_lesson_completion</code> calls — all in one synchronous transaction. This will hit a 30-second DB timeout at a few hundred enrollments. The same problem exists for <code>LessonPublished</code> (adds a new row per enrolled student) and <code>ModulePublished</code> (updates all module progress rows).</p>
      <h4>Recommendation</h4>
      <p>Fan-out operations that touch N rows where N grows with enrollment count must be background tasks, not inline event handlers. The event handler enqueues a task; the task processes rows in batches of 500 with a short delay between batches to avoid DB saturation.</p>

      <div class="diff-grid">
        <div class="diff-block before">
          <div class="diff-label">v1 — synchronous, will timeout</div>
          <pre>def handle_content_deleted(lesson_id, content_id):
    affected = LessonProgress.filter(lesson_id=lesson_id)
    for lp in affected:             # N iterations
        lp.required_content_count -= 1
        if viewed(lp, content_id):
            lp.viewed_required_count -= 1
        lp.save()
        _check_lesson_completion(lp)  # N more queries</pre>
        </div>
        <div class="diff-block after">
          <div class="diff-label">v2 — enqueue background task</div>
          <pre>def handle_content_deleted(lesson_id, content_id, was_required):
    if not was_required:
        return          # no counter impact, done
    # Enqueue — do not process inline
    tasks.fan_out_content_deletion.delay(
        lesson_id=lesson_id,
        content_id=content_id,
    )

# Background task (Celery / similar)
def fan_out_content_deletion(lesson_id, content_id):
    qs = LessonProgress.filter(lesson_id=lesson_id, status__ne='completed')
    for batch in chunked(qs, 500):
        # bulk update + per-row completion check</pre>
        </div>
      </div>
    </div>
  </div>

  <div class="finding" id="F2">
    <div class="finding-header critical">
      <span class="finding-id">F2</span>
      <span class="finding-title">Race condition on <code>viewed_required_count</code> — lost increments cause permanent stuck state</span>
      <span class="sev sev-critical">Critical</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The <code>record_content_view</code> algorithm increments <code>viewed_required_count</code> with a read-modify-write pattern. Two concurrent requests (e.g., a mobile app syncing two offline views simultaneously, or a student with two tabs open) will both read the same current value and both write the same incremented value — losing one increment entirely.</p>

      <div class="diff-grid">
        <div class="diff-block before">
          <div class="diff-label">The race — thread B's increment is lost</div>
          <pre>T=0  A reads viewed_required_count = 1
T=0  B reads viewed_required_count = 1
T=1  A writes 2  ← correct
T=1  B writes 2  ← should be 3, is 2

Result: viewed=2, required=3
        content gate never passes.
        Student is permanently stuck.</pre>
        </div>
        <div class="diff-block after">
          <div class="diff-label">v2 — use F() expressions + created flag</div>
          <pre>view_record, created = LessonContentView.get_or_create(
    enrollment_id=enrollment_id,
    content_id=content_id,
    defaults={...}
)

if created and view_record.is_required:
    # Atomic increment — no read-modify-write
    LessonProgress.filter(enrollment_id=..., lesson_id=...).update(
        viewed_required_count=F('viewed_required_count') + 1
    )
    # Re-fetch after F() update for completion check
    lp.refresh_from_db()</pre>
        </div>
      </div>

      <h4>Why the UNIQUE constraint alone is not enough</h4>
      <p>The UNIQUE index on <code>(enrollment_id, content_id)</code> prevents duplicate rows but does not protect the counter. The increment must be atomic at the DB level. <code>F()</code> expressions translate to <code>UPDATE ... SET col = col + 1</code> — a single atomic SQL statement. All counter increments and decrements throughout the entire domain must use this pattern.</p>

      <div class="rec-block">
        <h4>Rule for all counters in this domain</h4>
        <p>Every increment or decrement of <code>viewed_required_count</code>, <code>completed_lessons_count</code>, and <code>completed_modules_count</code> must use Django's <code>F()</code> expression. The only read of these counters allowed in the completion check must be a <code>refresh_from_db()</code> call immediately after the atomic update — not a stale in-memory value.</p>
      </div>
    </div>
  </div>

  <div class="finding" id="F3">
    <div class="finding-header high">
      <span class="finding-id">F3</span>
      <span class="finding-title">Counter drift on already-completed lessons</span>
      <span class="sev sev-high">High</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>When a staff member adds a new required content item to a lesson where some students have already reached <code>status=completed</code>, the fan-out handler increments <code>required_content_count</code> on those completed rows. Now <code>viewed_required_count (3) < required_content_count (4)</code> on a row with <code>status=completed</code>. The <code>CHECK(completed_at IS NULL OR status = 'completed')</code> constraint prevents reverting status, so the row enters a permanently inconsistent state: complete but counters say otherwise.</p>
      <h4>Recommendation</h4>
      <p>Fan-out handlers for counter updates must filter out rows where <code>status = 'completed'</code>. Completed lessons are frozen — they do not participate in counter updates regardless of what the Learning Domain changes. A completed lesson stays completed. This is the correct product behaviour: retroactive content addition does not un-complete a lesson a student has already finished.</p>

      <pre>-- v2: fan-out targets only non-completed rows
UPDATE progress_lessonprogress
   SET required_content_count = required_content_count + 1
 WHERE lesson_id = $lesson_id
   AND status != 'completed';   -- ← this filter is the entire fix</pre>
    </div>
  </div>

  <div class="finding" id="F4">
    <div class="finding-header high">
      <span class="finding-id">F4</span>
      <span class="finding-title">No handler for <code>LessonContentAdded</code> — new required content invisible to counters</span>
      <span class="sev sev-high">High</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The v1 document defines a handler for <code>LessonContentDeleted</code> but not for <code>LessonContentAdded</code>. The Learning Domain's <code>LessonContentService.add_content()</code> does not emit a corresponding event that UserProgress listens to. When a staff member adds a new required content item to a published lesson, all enrolled students' <code>required_content_count</code> snapshots become stale — they remain at the old value. Students could complete a lesson without viewing the new required content.</p>
      <h4>Recommendation</h4>
      <p>Learning Domain must emit <code>LessonContentAdded(lesson_id, content_id, is_required)</code>. UserProgress must handle it with the same fan-out background task pattern as F1. The same <code>status != 'completed'</code> filter from F3 applies.</p>
    </div>
  </div>

  <div class="finding" id="F5">
    <div class="finding-header low">
      <span class="finding-id">F5</span>
      <span class="finding-title"><code>CHECK viewed ≤ required + 1</code> is wrong — masks bugs</span>
      <span class="sev sev-low">Low</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The constraint <code>CHECK(viewed_required_count &lt;= required_content_count + 1)</code> was documented as "tolerance for concurrent updates." This is the wrong way to handle concurrency. Tolerating a counter that is one ahead hides genuine bugs and will not catch a counter that's 3 or 5 ahead (which can happen with F4 and the fan-out race). Once F2's <code>F()</code> expressions are applied, concurrent increments are atomic and no tolerance is needed.</p>
      <h4>Recommendation</h4>
      <p>Remove the <code>+1</code> tolerance. The correct constraint is <code>CHECK(viewed_required_count &lt;= required_content_count)</code>. With atomic <code>F()</code> increments and the <code>status != 'completed'</code> filter from F3, this constraint will never be violated in normal operation. Any violation indicates a real bug that should be surfaced, not masked.</p>
    </div>
  </div>
</section>

<!-- ═══ AREA 2: PERCENTAGE ═══ -->
<section id="area2">
  <div class="area-header">
    <div class="area-num amber">2</div>
    <h2 style="border:none; padding:0; margin:0;">Progress Percentage Calculation</h2>
  </div>

  <div class="finding" id="F6">
    <div class="finding-header high">
      <span class="finding-id">F6</span>
      <span class="finding-title">Module-granularity percentage is misleading — equal weight regardless of lesson count</span>
      <span class="sev sev-high">High</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The current formula is <code>completion_percentage = completed_modules_count / total_modules_count</code>. This gives equal weight to every module regardless of how many lessons it contains. A course with modules of sizes [20 lessons, 1 lesson, 1 lesson] would show a student as <strong>67% complete</strong> after finishing modules 2 and 3 — when they've only completed 2 of 22 lessons.</p>

      <div class="diff-grid">
        <div class="diff-block before">
          <div class="diff-label">v1 — module weight: always 1/N</div>
          <pre>Module 1: 20 lessons  → weight 33%
Module 2:  1 lesson   → weight 33%
Module 3:  1 lesson   → weight 33%

Student finishes M2 + M3 → 67%
But has done 2 / 22 actual lessons.
</pre>
        </div>
        <div class="diff-block after">
          <div class="diff-label">v2 — lesson-based: weight by lesson count</div>
          <pre>total_lessons   = SUM(mp.total_lessons_count)
                = 20 + 1 + 1 = 22

completed_lessons = SUM(mp.completed_lessons_count)

percentage = completed_lessons / total_lessons
           = 2 / 22 = 9%   ← accurate</pre>
        </div>
      </div>

      <h4>Schema implication</h4>
      <p>Add <code>total_lessons_count</code> and <code>completed_lessons_count</code> to <code>CourseProgress</code>. These are maintained the same way as on <code>ModuleProgress</code> — incremented via the cascade. Alternatively, compute on-demand by <code>SUM</code> over <code>ModuleProgress</code> rows. For the monolith with proper indexing, the SUM approach is acceptable and avoids adding two more counters to maintain. Prefer the SUM approach initially — add the denormalized counters only if profiling shows the query is slow at the dashboard scale.</p>

      <div class="rec-block">
        <h4>Recommended implementation for <code>get_completion_percentage</code></h4>
        <p>Query: <code>SELECT SUM(completed_lessons_count), SUM(total_lessons_count) FROM progress_moduleprogress WHERE enrollment_id = X AND NOT is_stale</code>. Single indexed query per enrollment. Add it to <code>CourseProgressSelector.get_completion_percentage()</code>. Cache the result on the <code>CourseProgress</code> row with a <code>cached_percentage</code> INT field (updated on each lesson completion). Dashboard reads the cached field; the SUM query recalculates it.</p>
      </div>
    </div>
  </div>

  <div class="finding" id="F7">
    <div class="finding-header medium">
      <span class="finding-id">F7</span>
      <span class="finding-title"><code>assessment_pending</code> shows 0% credit for lesson work inside the module</span>
      <span class="sev sev-medium">Medium</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>A module in <code>assessment_pending</code> has <code>completed_lessons_count == total_lessons_count</code> but <code>ModuleProgress.status != 'completed'</code>. With the v1 percentage formula, the entire module contributes 0 to <code>completed_modules_count</code>. A student who finishes all 10 lessons of an 11-lesson course and is waiting to take the assessment sees themselves at exactly the same percentage as when they started the last module. This is a psychological problem — it demotivates students and makes the progress bar feel broken.</p>
      <h4>Recommendation</h4>
      <p>The lesson-based percentage from F6 naturally resolves this — lessons inside an <code>assessment_pending</code> module <em>are</em> counted as completed in <code>completed_lessons_count</code>. The percentage rises as lessons complete, regardless of module assessment status. No additional change needed beyond fixing F6.</p>
    </div>
  </div>
</section>

<!-- ═══ AREA 3: CONTINUE LEARNING ═══ -->
<section id="area3">
  <div class="area-header">
    <div class="area-num coral">3</div>
    <h2 style="border:none; padding:0; margin:0;">Continue Learning Strategy</h2>
  </div>

  <div class="finding" id="F8">
    <div class="finding-header critical">
      <span class="finding-id">F8</span>
      <span class="finding-title">Cross-module <code>lesson_order</code> comparison missing <code>module_order</code> — wrong lesson returned</span>
      <span class="sev sev-critical">Critical</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The v1 spec for <code>get_next_lesson</code> returns the LessonProgress with <code>status=unlocked</code> and the lowest <code>lesson_order</code>. But <code>lesson_order</code> is <strong>scoped per module</strong> — every module starts its own ordering from 1. Comparing raw <code>lesson_order</code> across modules is meaningless.</p>

      <pre>Module 1 (module_order=1): lessons with lesson_order = 1, 2, 3, 4, 5
Module 2 (module_order=2): lessons with lesson_order = 1, 2, 3

Student just finished Module 1, Lesson 5.
Module 2, Lesson 1 (lesson_order=1) is now unlocked.
Module 1, Lesson 5 is now complete.

v1 query: ORDER BY lesson_order ASC → returns Module 1 Lesson 1 (order=1, status=completed)
          or Module 2 Lesson 1 (also order=1)... undefined tie-break.

Correct query: ORDER BY module_order ASC, lesson_order ASC</pre>

      <h4>Recommendation</h4>
      <p>The query for <code>get_next_lesson</code> must always include <code>module_order</code> as the primary sort key. This requires <code>module_order</code> to be stored on <code>LessonProgress</code> (it already is, as a snapshot field) and the index must cover <code>(enrollment_id, module_order, lesson_order)</code>.</p>
    </div>
  </div>

  <div class="finding" id="F9">
    <div class="finding-header high">
      <span class="finding-id">F9</span>
      <span class="finding-title"><code>in_progress</code> vs <code>unlocked</code> priority is inverted — mid-lesson student is abandoned</span>
      <span class="sev sev-high">High</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The v1 spec says: return the first <code>unlocked</code> lesson, <em>fall back to</em> first <code>in_progress</code> if none. This is backwards. <code>unlocked</code> means the student hasn't started yet. <code>in_progress</code> means the student opened the lesson, watched some content, and left. "Continue" should resume the interrupted lesson, not advance to the next one.</p>

      <div class="diff-grid">
        <div class="diff-block before">
          <div class="diff-label">v1 — wrong priority</div>
          <pre>1. First unlocked lesson  ← sends to NEW lesson
2. Fallback: in_progress  ← abandons the student
                              who is mid-way through</pre>
        </div>
        <div class="diff-block after">
          <div class="diff-label">v2 — correct priority</div>
          <pre>1. Most recent in_progress lesson  ← resume
   (ordered by started_at DESC)
2. First unlocked lesson           ← continue
   (ordered by module_order, lesson_order)
3. None → course complete or pending assessment</pre>
        </div>
      </div>
    </div>
  </div>

  <div class="finding" id="F10">
    <div class="finding-header high">
      <span class="finding-id">F10</span>
      <span class="finding-title"><code>assessment_pending</code> returns <code>next_lesson: null</code> — dead-end UX</span>
      <span class="sev sev-high">High</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>When a module is in <code>assessment_pending</code>, there are no <code>unlocked</code> lessons in the course (the first lesson of the next module is still <code>locked</code>, waiting for the current module to complete). The <code>get_next_lesson</code> query returns nothing. The API currently returns <code>next_lesson: null</code>. The student sees a dead "Continue" button with no explanation — they don't know they need to take an assessment.</p>
      <h4>Recommendation</h4>
      <p>Add a <code>next_action</code> field to the response. When <code>get_next_lesson</code> finds no lesson but a module is in <code>assessment_pending</code>, return a structured signal the frontend can act on.</p>

      <pre>-- v2 response shape for get_next_lesson
{
  "next_lesson": null,
  "next_action": {
    "type": "take_module_assessment",   // or "course_complete", or "lesson_unlocked"
    "module_id": "uuid",
    "module_title": "Python OOP",
    "assessment_url": "/assessments/modules/uuid/"  // from Assessment domain
  }
}</pre>

      <p>The <code>CourseProgressSelector.get_next_lesson</code> method should be renamed to <code>get_next_action</code> and return a typed discriminated union: <code>{ type: "lesson", lesson_id }</code> | <code>{ type: "assessment", module_id }</code> | <code>{ type: "complete" }</code> | <code>{ type: "not_started" }</code>.</p>
    </div>
  </div>

  <div class="finding" id="F11">
    <div class="finding-header medium">
      <span class="finding-id">F11</span>
      <span class="finding-title">Non-sequential "continue" returns first-by-order instead of last-active</span>
      <span class="sev sev-medium">Medium</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>For non-sequential courses, all lessons start as <code>unlocked</code>. The current <code>get_next_lesson</code> implementation ordered by <code>(module_order, lesson_order)</code> would return Lesson 1 of Module 1 every time — the student's last-visited lesson is ignored entirely.</p>
      <h4>Recommendation</h4>
      <p>Non-sequential courses should use a different "continue" strategy: return the most recently active lesson, whether it is <code>in_progress</code> or the most recently accessed <code>unlocked</code> lesson. Use <code>LessonProgress.started_at DESC</code> as the sort for non-sequential. The selector must branch on <code>Course.is_sequential</code> (read via Learning Domain selector or cached on CourseProgress).</p>

      <pre>-- Add is_sequential snapshot to CourseProgress for hot-path use
ALTER TABLE progress_courseprogress
    ADD COLUMN is_sequential BOOLEAN NOT NULL DEFAULT TRUE;</pre>
    </div>
  </div>
</section>

<!-- ═══ AREA 4: ONLINE/OFFLINE ═══ -->
<section id="area4">
  <div class="area-header">
    <div class="area-num sky">4</div>
    <h2 style="border:none; padding:0; margin:0;">Online vs Offline Completion Logic</h2>
  </div>

  <div class="finding" id="F12">
    <div class="finding-header high">
      <span class="finding-id">F12</span>
      <span class="finding-title">Attendance bypasses homework gate — offline students skip required work</span>
      <span class="sev sev-high">High</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The v1 design states attendance bypasses <em>both</em> content and homework gates. But homework is pedagogically different from watching a video. Content can be covered in a classroom session — the mentor's attendance mark is a reasonable proxy for "the student engaged with the material." Homework submission is a separate act of work product — attending a session does not produce the homework.</p>
      <h4>Design question that was skipped</h4>
      <p>The v1 architecture note says "for offline, attendance IS completion." This was stated as a resolved decision but it conflates two distinct concerns: <em>did the student attend the session?</em> (the attendance mark answers this) vs <em>did the student produce the required deliverable?</em> (only homework submission answers this).</p>
      <h4>Recommendation</h4>
      <p>Attendance should bypass the <strong>content gate only</strong>. The homework gate should apply regardless of delivery format. This is a product decision that must be confirmed, but the architecture should be built to support it. The implementation change is minimal:</p>

      <div class="diff-grid">
        <div class="diff-block before">
          <div class="diff-label">v1 — both gates bypassed</div>
          <pre>def handle_attendance_marked(...):
    lp.status           = 'completed'
    lp.completion_source = 'mentor_attendance'
    # homework gate skipped entirely</pre>
        </div>
        <div class="diff-block after">
          <div class="diff-label">v2 — content gate bypassed, homework gate still applied</div>
          <pre>def handle_attendance_marked(...):
    # Content gate: bypass by setting counter equal
    lp.viewed_required_count = lp.required_content_count
    lp.completion_source     = 'mentor_attendance'
    # Homework gate: still evaluated
    _check_lesson_completion(enrollment_id, lesson_id)</pre>
        </div>
      </div>

      <p>This means an offline student whose lesson has required homework still needs to submit it after attending the session. The content gate is passed by the attendance mark; the homework gate still requires a submission event from the Submissions Domain.</p>
    </div>
  </div>

  <div class="finding" id="F13">
    <div class="finding-header medium">
      <span class="finding-id">F13</span>
      <span class="finding-title">No <code>AttendanceRevoked</code> path — mentor mistakes are permanent</span>
      <span class="sev sev-medium">Medium</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>Lesson completion is designed as a terminal state. But offline attendance can be marked in error — wrong student, wrong session, typo. Since <code>completion_source = 'mentor_attendance'</code> locks the lesson as completed with no reversal path, a mentor mistake permanently advances a student past lessons they haven't actually attended.</p>
      <h4>Recommendation</h4>
      <p>Two options. <strong>Option A (simple):</strong> Add an admin-only <code>POST /progress/enrollments/{id}/lessons/{id}/reset/</code> endpoint backed by a hard reset in <code>LessonProgressService</code> — this is an escape hatch, not a normal flow. Require dual-staff approval in the application layer. <strong>Option B (strict):</strong> Keep completion terminal but require the Mentorship Domain to emit a <code>CourseEnrollmentService.complete_enrollment()</code> reversal — complex and probably overkill. Option A is sufficient for v1.</p>

      <p>Additionally, the <code>AttendanceMarked</code> event must carry an <code>idempotency_key</code> (session_id + enrollment_id) to prevent duplicate processing if the event is delivered twice.</p>
    </div>
  </div>

  <div class="finding" id="F14">
    <div class="finding-header medium">
      <span class="finding-id">F14</span>
      <span class="finding-title">Delivery format change mid-course — completion logic reads stale context</span>
      <span class="sev sev-medium">Medium</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>An admin can change <code>CourseEnrollment.delivery_format</code> from <code>offline</code> to <code>online</code> mid-course. But <code>LessonProgressService.record_content_view</code> determines which gates to apply by reading <code>enrollment.delivery_format</code> at call time. This is correct — it uses the live value. However, lessons already completed as <code>completion_source = 'mentor_attendance'</code> remain completed under the offline model. Future lessons now use online gate logic. The student is in a mixed state that is actually fine for progress tracking, but the completion percentage and analytics will show a mixed <code>completion_source</code> within one enrollment.</p>
      <h4>Recommendation</h4>
      <p>This is acceptable behaviour — document it explicitly. Emit an <code>EnrollmentDeliveryFormatChanged</code> event that UserProgress listens to. When received, update a <code>delivery_format</code> snapshot field on <code>CourseProgress</code>. This snapshot is then available to <code>LessonProgressService</code> without requiring a cross-domain lookup on every content view call.</p>

      <pre>-- Add delivery_format snapshot to CourseProgress
ALTER TABLE progress_courseprogress
    ADD COLUMN delivery_format VARCHAR(10) NOT NULL DEFAULT 'online';
-- Updated via EnrollmentDeliveryFormatChanged event handler</pre>
    </div>
  </div>
</section>

<!-- ═══ AREA 5: CONTENT TRACKING ═══ -->
<section id="area5">
  <div class="area-header">
    <div class="area-num teal">5</div>
    <h2 style="border:none; padding:0; margin:0;">Content Progress Tracking Model</h2>
  </div>

  <div class="finding" id="F15">
    <div class="finding-header medium">
      <span class="finding-id">F15</span>
      <span class="finding-title">One API call marks a 2-hour video as "viewed" — no watch threshold</span>
      <span class="sev sev-medium">Medium</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p><code>POST /progress/lessons/{id}/content/{id}/view/</code> records a view and creates the <code>LessonContentView</code> row. For <code>type=text</code> or <code>type=pdf</code>, a single "opened the page" signal is a reasonable proxy for consumption. For <code>type=video</code> or <code>type=recording</code>, this means a student who opens the video player and immediately closes it has "viewed" a 4-hour lecture and passes the content gate.</p>
      <h4>Impact</h4>
      <p>For now, this is a product decision as much as a technical one. The architecture should support enforcement without requiring it. The current model stores <code>last_position_seconds</code> but never uses it for gate evaluation.</p>
      <h4>Recommendation</h4>
      <p>Add a <code>minimum_watch_ratio</code> field (DECIMAL 0–1, default 0.0) to <code>LessonContent</code> in the Learning Domain. The UserProgress domain stores <code>total_duration_seconds</code> on <code>LessonContentView</code> (snapshotted from LessonContent at view time) and uses it with <code>last_position_seconds</code> to evaluate whether the watch threshold is met. The content gate check becomes:</p>

      <pre>-- Content gate check for a single content item (video)
def is_content_item_complete(view_record):
    if content.type not in ('video', 'recording'):
        return view_record is not None    # opened = done for non-video

    if content.minimum_watch_ratio == 0:
        return view_record is not None    # no threshold set

    if view_record is None:
        return False

    watch_ratio = view_record.last_position_seconds / view_record.total_duration_seconds
    return watch_ratio >= content.minimum_watch_ratio</pre>

      <p>The <code>viewed_required_count</code> counter is then incremented only when the threshold is met, not on first open. This is a non-breaking change — defaulting <code>minimum_watch_ratio = 0</code> preserves existing behaviour.</p>
    </div>
  </div>

  <div class="finding" id="F16">
    <div class="finding-header medium">
      <span class="finding-id">F16</span>
      <span class="finding-title"><code>is_required</code> flag change on existing content is not handled</span>
      <span class="sev sev-medium">Medium</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The Learning Domain allows updating a content item — including its <code>is_required</code> flag. Two cases:</p>
      <p><strong>Case A (FALSE → TRUE):</strong> A student already viewed this content item before it became required. Their <code>LessonContentView</code> row exists. But <code>viewed_required_count</code> was not incremented when it was first viewed (because it wasn't required then). The student now has an invisible deficit — they've watched the video but the counter doesn't reflect it.</p>
      <p><strong>Case B (TRUE → FALSE):</strong> A student's <code>viewed_required_count</code> includes this item. The item is now not required. Their counter is inflated, and <code>required_content_count</code> will be decremented by the fan-out handler, leaving <code>viewed &gt; required</code> — technically fine for gate evaluation but semantically wrong.</p>
      <h4>Recommendation</h4>
      <p>The Learning Domain should emit a <code>LessonContentRequirementChanged(content_id, lesson_id, old_value, new_value)</code> event. UserProgress handles it by: for FALSE→TRUE, checking if a <code>LessonContentView</code> exists for each enrolled student and, if so, incrementing <code>viewed_required_count</code>. Apply the same background task fan-out pattern from F1.</p>
    </div>
  </div>

  <div class="finding" id="F17">
    <div class="finding-header critical">
      <span class="finding-id">F17</span>
      <span class="finding-title"><code>_unlock_next_module</code> never unlocks the first lesson of the next module</span>
      <span class="sev sev-critical">Critical</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The v1 cascade is: <code>_check_lesson_completion</code> → <code>_unlock_next_lesson</code> → <code>_check_module_completion</code> → <code>_unlock_next_module</code> → <code>_check_course_completion</code>. The <code>_unlock_next_module</code> function is mentioned but never specified. It presumably sets <code>ModuleProgress.status = 'unlocked'</code>. But it does <strong>not</strong> unlock the first <code>LessonProgress</code> row in that next module. After module unlock, all lessons in the new module still have <code>status=locked</code>. No lesson is unlocked. The student is stuck — no <code>get_next_lesson</code> call will return anything from the new module.</p>

      <div class="diff-grid">
        <div class="diff-block before">
          <div class="diff-label">v1 — next module unlocked, lessons still all locked</div>
          <pre>ModuleProgress(module=2) → status='unlocked'  ✓
LessonProgress(module=2, lesson=1) → status='locked'  ✗
LessonProgress(module=2, lesson=2) → status='locked'  ✗
LessonProgress(module=2, lesson=3) → status='locked'  ✗
→ get_next_lesson returns nothing. Student is stuck.</pre>
        </div>
        <div class="diff-block after">
          <div class="diff-label">v2 — _unlock_next_module also unlocks first lesson</div>
          <pre>def _unlock_next_module(enrollment_id, completed_module_id):
    next_mp = find_next_module(enrollment_id, completed_module_id)
    if not next_mp:
        return   # last module just completed

    next_mp.status     = 'unlocked'
    next_mp.unlocked_at = now()

    # ← This step was missing entirely in v1
    first_lesson = LessonProgress.filter(
        enrollment_id=enrollment_id,
        module_id=next_mp.module_id,
        lesson_order=1,
        status='locked'
    ).first()
    if first_lesson:
        first_lesson.status     = 'unlocked'
        first_lesson.unlocked_at = now()
        EMIT LessonUnlocked</pre>
        </div>
      </div>

      <p>This is a logic gap, not an edge case. Without this fix, every sequential course breaks at every module boundary for every student.</p>
    </div>
  </div>
</section>

<!-- ═══ ADDITIONAL FINDINGS ═══ -->
<section id="area6">
  <div class="area-header">
    <div class="area-num gray">+</div>
    <h2 style="border:none; padding:0; margin:0;">Additional Findings</h2>
  </div>

  <div class="finding" id="F18">
    <div class="finding-header critical">
      <span class="finding-id">F18</span>
      <span class="finding-title">Bulk offline attendance creates race condition on module completion counter</span>
      <span class="sev sev-critical">Critical</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>When a mentor marks attendance for a session that covered 5 lessons, the <code>AttendanceMarked</code> event contains <code>lesson_ids: [L1, L2, L3, L4, L5]</code>. The handler loops and calls <code>handle_attendance_marked</code> for each lesson. Each call ultimately calls <code>_check_module_completion</code>, which reads <code>completed_lessons_count</code>, increments it, and checks if all lessons are done.</p>
      <p>If these 5 calls run concurrently (either via Celery parallelism or async task workers), they each read the same starting value of <code>completed_lessons_count</code> before any write lands:</p>

      <pre>Module has 5 lessons. completed_lessons_count starts at 0.
All 5 completion checks run concurrently — no row locking.

Worker 1: reads 0, writes 1, checks: 1 >= 5? No
Worker 2: reads 0, writes 1, checks: 1 >= 5? No   ← lost update
Worker 3: reads 0, writes 1, checks: 1 >= 5? No   ← lost update
Worker 4: reads 0, writes 1, checks: 1 >= 5? No   ← lost update
Worker 5: reads 0, writes 1, checks: 1 >= 5? No   ← lost update

Final completed_lessons_count = 1.
Module never completes.
Student is permanently stuck unless admin manually overrides.</pre>

      <h4>Recommendation</h4>
      <p><strong>For the cascade itself:</strong> The <code>_check_module_completion</code> function must acquire a row-level lock on the <code>ModuleProgress</code> row using <code>SELECT ... FOR UPDATE</code> before reading and incrementing. This serialises concurrent lesson completions for the same module.</p>
      <p><strong>For the bulk attendance event:</strong> Process lesson completions for a single enrollment serially, not in parallel. The handler serialises completions per enrollment via a per-enrollment distributed lock or by processing the lesson list in-order within a single task.</p>

      <pre>-- v2: Row-level locking in _check_module_completion
def _check_module_completion(enrollment_id, module_id):
    with transaction.atomic():
        # Acquire row lock before any read
        mp = ModuleProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id,
            module_id=module_id
        )
        # Safe to read and update now — serialised
        ...</pre>

      <div class="callout warning" style="margin-top:12px">
        <strong>SELECT FOR UPDATE must be applied consistently</strong> throughout the entire cascade chain: <code>_check_lesson_completion</code>, <code>_check_module_completion</code>, and <code>_check_course_completion</code> all need row-level locks on their respective progress rows. This is non-negotiable for correctness in any concurrent environment.
      </div>
    </div>
  </div>

  <div class="finding" id="F19">
    <div class="finding-header low">
      <span class="finding-id">F19</span>
      <span class="finding-title">Re-enroll after drop resets progress to zero — product decision not explicit</span>
      <span class="sev sev-low">Low</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>When a student drops a course and re-enrolls, a new <code>CourseEnrollment</code> is created (new UUID). <code>ProgressInitialisationService.initialise_progress</code> is called for the new enrollment and creates all-fresh <code>LessonProgress</code> rows (starting from <code>locked</code>/<code>unlocked</code>). The student loses all previously completed progress. This may or may not be the intended behaviour — the v1 document never explicitly decided.</p>
      <h4>Impact</h4>
      <p>A student who drops at 80% completion and re-enrolls starts at 0%. For online self-paced learning this feels punitive. For offline group-based learning it may be intentional (they join a new cohort).</p>
      <h4>Recommendation</h4>
      <p>Make this an explicit product decision and document it. If "preserve progress on re-enroll" is desired, add a <code>previous_enrollment_id</code> FK (nullable) to <code>CourseEnrollment</code>. On initialisation, check if a completed LessonProgress row exists for the user on a previous enrollment for the same lesson, and if so, start those lessons as <code>completed</code> with the original <code>completion_source</code>. This is opt-in behaviour controlled by Learning Domain's re-enrollment business rules.</p>
    </div>
  </div>

  <div class="finding" id="F20">
    <div class="finding-header low">
      <span class="finding-id">F20</span>
      <span class="finding-title">Admin override has no audit trail in the schema</span>
      <span class="sev sev-low">Low</span>
    </div>
    <div class="finding-body">
      <h4>Finding</h4>
      <p>The <code>override_lesson_complete</code> API requires a <code>reason</code> string. But <code>LessonProgress</code> has no <code>override_reason</code> or <code>override_by_id</code> fields. The reason is received by the API and discarded. When a compliance audit asks "why was this student's lesson manually completed?", there's no answer in the database.</p>
      <h4>Recommendation</h4>
      <p>Add two nullable fields to <code>LessonProgress</code>:</p>
      <pre>override_by_id     UUID NULLABLE  -- actor who performed the override
override_reason    TEXT NULLABLE  -- reason provided at override time</pre>
      <p>These fields are only populated when <code>completion_source = 'admin_override'</code>. No migration complexity — both are nullable with no backfill needed.</p>
    </div>
  </div>
</section>

<!-- ═══ SCHEMA CHANGES v2 ═══ -->
<section id="schema-changes">
  <h2>Schema Changes for v2 <span class="tag">RESOLUTION</span></h2>

  <table class="change-table">
    <tr><th>Table</th><th>Change</th><th>Reason</th><th>Type</th></tr>

    <tr class="change-added"><td>progress_courseprogress</td><td>ADD <code>delivery_format VARCHAR(10)</code></td><td>F14 — avoid cross-domain read on every content view</td><td>ADD COLUMN</td></tr>
    <tr class="change-added"><td>progress_courseprogress</td><td>ADD <code>is_sequential BOOLEAN DEFAULT TRUE</code></td><td>F11 — non-sequential continue logic branch</td><td>ADD COLUMN</td></tr>
    <tr class="change-added"><td>progress_courseprogress</td><td>ADD <code>cached_percentage SMALLINT DEFAULT 0</code></td><td>F6 — fast dashboard read without SUM query</td><td>ADD COLUMN</td></tr>
    <tr class="change-added"><td>progress_moduleprogress</td><td>ADD <code>is_stale BOOLEAN DEFAULT FALSE</code></td><td>Referenced in services section but missing from schema</td><td>ADD COLUMN</td></tr>
    <tr class="change-added"><td>progress_lessonprogress</td><td>ADD <code>is_stale BOOLEAN DEFAULT FALSE</code></td><td>Handle lesson deletion without data loss</td><td>ADD COLUMN</td></tr>
    <tr class="change-added"><td>progress_lessonprogress</td><td>ADD <code>is_active BOOLEAN DEFAULT TRUE</code></td><td>Referenced in CourseProgressService but missing from schema</td><td>ADD COLUMN</td></tr>
    <tr class="change-added"><td>progress_lessonprogress</td><td>ADD <code>override_by_id UUID NULLABLE</code></td><td>F20 — audit trail for admin overrides</td><td>ADD COLUMN</td></tr>
    <tr class="change-added"><td>progress_lessonprogress</td><td>ADD <code>override_reason TEXT NULLABLE</code></td><td>F20 — audit trail for admin overrides</td><td>ADD COLUMN</td></tr>
    <tr class="change-modified"><td>progress_lessonprogress</td><td>CHANGE CHECK constraint from <code>viewed &lt;= required + 1</code> to <code>viewed &lt;= required</code></td><td>F5 — remove false tolerance</td><td>MODIFY CONSTRAINT</td></tr>
    <tr class="change-added"><td>progress_lessoncontentview</td><td>ADD <code>total_duration_seconds INT NULLABLE</code></td><td>F15 — video watch threshold evaluation</td><td>ADD COLUMN</td></tr>
    <tr class="change-added"><td>courses_lessoncontent (Learning Domain)</td><td>ADD <code>minimum_watch_ratio DECIMAL(3,2) DEFAULT 0.0</code></td><td>F15 — configurable video completion threshold</td><td>ADD COLUMN (Learning Domain)</td></tr>
    <tr class="change-added"><td>courses_courseenrollment (Learning Domain)</td><td>ADD <code>previous_enrollment_id UUID NULLABLE FK</code></td><td>F19 — optional progress preservation on re-enroll</td><td>ADD COLUMN (Learning Domain)</td></tr>
  </table>

  <div class="callout warning" style="margin-top:16px">
    <strong>New index required (F8 fix):</strong> <code>CREATE INDEX idx_lp_enr_module_lesson ON progress_lessonprogress (enrollment_id, module_order, lesson_order) WHERE status IN ('unlocked','in_progress') AND is_stale = FALSE AND is_active = TRUE</code> — this partial index powers the <code>get_next_action</code> query efficiently.
  </div>
</section>

<!-- ═══ ALGORITHM CHANGES v2 ═══ -->
<section id="algorithm-changes">
  <h2>Algorithm Changes for v2 <span class="tag">RESOLUTION</span></h2>

  <table>
    <tr><th>Algorithm</th><th>Change</th><th>Fixes</th></tr>
    <tr><td><code>record_content_view</code></td><td>Use <code>get_or_create</code> and only increment counter if <code>created=True</code>. Use <code>F('viewed_required_count') + 1</code>. Call <code>refresh_from_db()</code> before completion check.</td><td>F2</td></tr>
    <tr><td><code>_check_lesson_completion</code></td><td>Add <code>select_for_update()</code> on LessonProgress row at start of method.</td><td>F18</td></tr>
    <tr><td><code>_check_module_completion</code></td><td>Add <code>select_for_update()</code> on ModuleProgress row. Use <code>F('completed_lessons_count') + 1</code> for increment.</td><td>F2, F18</td></tr>
    <tr><td><code>_check_course_completion</code></td><td>Add <code>select_for_update()</code> on CourseProgress row. Use <code>F('completed_modules_count') + 1</code> for increment. Update <code>cached_percentage</code> here.</td><td>F2, F18</td></tr>
    <tr><td><code>_unlock_next_module</code></td><td>After setting next ModuleProgress to <code>unlocked</code>, also set the first LessonProgress of that module to <code>unlocked</code>.</td><td>F17 — critical gap</td></tr>
    <tr><td><code>get_next_lesson</code> → <code>get_next_action</code></td><td>Rename. Change priority: <code>in_progress</code> first (by <code>started_at DESC</code>), then <code>unlocked</code> (by <code>module_order ASC, lesson_order ASC</code>). Add <code>assessment_pending</code> detection returning typed next-action response. Branch on <code>is_sequential</code>.</td><td>F8, F9, F10, F11</td></tr>
    <tr><td>fan-out handlers</td><td>All handlers that update N rows where N = enrolled students must be converted to background tasks (Celery or equivalent) with batch processing (500 rows/batch). Applies to: <code>handle_content_deleted</code>, <code>handle_content_added</code>, <code>handle_lesson_published</code>, <code>handle_lesson_deleted</code>, <code>handle_assessment_added</code>.</td><td>F1</td></tr>
    <tr><td><code>handle_content_deleted</code>, <code>handle_content_added</code></td><td>Add <code>WHERE status != 'completed'</code> filter to all counter update queries.</td><td>F3</td></tr>
    <tr><td><code>handle_attendance_marked</code></td><td>Change to bypass content gate only (set <code>viewed_required_count = required_content_count</code>), then call <code>_check_lesson_completion</code> to evaluate homework gate. Do not directly set <code>status=completed</code>.</td><td>F12</td></tr>
    <tr><td><code>initialise_progress</code></td><td>Snapshot <code>delivery_format</code> and <code>is_sequential</code> from enrollment + course onto CourseProgress row.</td><td>F11, F14</td></tr>
  </table>

  <h3>New event subscriptions required</h3>
  <table>
    <tr><th>New Event</th><th>Producer</th><th>Handler</th><th>Fixes</th></tr>
    <tr><td><code>LessonContentAdded</code></td><td>Learning Domain / LessonContentService</td><td><code>ProgressInitialisationService.handle_content_added</code></td><td>F4</td></tr>
    <tr><td><code>LessonContentRequirementChanged</code></td><td>Learning Domain / LessonContentService</td><td><code>ProgressInitialisationService.handle_content_requirement_changed</code></td><td>F16</td></tr>
    <tr><td><code>EnrollmentDeliveryFormatChanged</code></td><td>Learning Domain / CourseEnrollmentService</td><td><code>CourseProgressService.handle_delivery_format_changed</code></td><td>F14</td></tr>
    <tr><td><code>AttendanceRevoked</code></td><td>Mentorship Domain (future)</td><td><code>LessonProgressService.handle_attendance_revoked</code> (admin-gated)</td><td>F13</td></tr>
  </table>

  <div class="callout success" style="margin-top:24px">
    <strong>v2 verdict:</strong> With the 4 critical findings resolved (F2, F8, F17, F18) and the 7 high-severity findings addressed, the architecture is production-ready. The remaining medium and low findings are improvements that can be done in a follow-up sprint without blocking the initial implementation. Total new events required from Learning Domain: 2 (<code>LessonContentAdded</code>, <code>LessonContentRequirementChanged</code>). Total schema additions: 8 columns across 4 tables. No existing columns removed or renamed.
  </div>
</section>

</main>
</div>
</body>
</html>
# Mentorship Domain — Design v1

**Дата:** 2026-06-07  
**Статус:** ПРИНЯТО  
**Версия:** 1.0

---

## Ключевые решения

### 1. MentorGroup — только admin назначает (v1)

**Решение:** Студент НЕ выбирает ментора.

**Причина:** Выбор ментора студентом почти всегда приводит к проблемам с балансировкой нагрузки:
- Популярные менторы перегружены
- Непопулярные менторы простаивают
- Нужна сложная система ограничения выбора

**Для v1:**
```
Admin создаёт группу:
  Python Backend #12
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

### 2. Ограничение нагрузки ментора

**Решение:** Заложить в дизайн сейчас, даже если не используем в v1.

```sql
accounts_mentorprofile:
  max_students INT DEFAULT 30
  current_students INT DEFAULT 0
```

**Зачем сейчас:** Через год придётся мигрировать данные. Проще добавить поле сразу.

**Использование в v2:** Автоматический capacity-based assignment.

---

### 3. Расписание — НЕ привязывать модули к датам

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

### 4. Attendance — ментор отмечает вручную (v1)

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

### 5. Турникет — для контроля и аналитики, не для прогресса

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

### 6. Attendance → UserProgress flow

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

### 7. Bulk attendance marking (обязательно)

**Проблема:**
```
30 студентов × 15 занятий = 450 кликов
```

**Решение:**
```
Session #15

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

### 8. Mentor workload queue (обязательно)

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

### 9. Mentor override для lesson completion

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

## Схема БД

### mentorship_mentorgroup

**Цель:** Группа студентов с одним ментором для offline обучения.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| mentor_id | UUID FK | → accounts_user |
| course_id | UUID FK | → courses_course |
| name | VARCHAR(255) | "Python Backend #12" |
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

### mentorship_studentmentorgroup

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

### mentorship_offlinesession

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

### mentorship_attendance

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

### mentorship_accessevent

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

### mentorship_mentorworkreview (read model)

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

## События

### Исходящие (из Mentorship Domain)

```python
@dataclass
class AttendanceMarked:
    session_id: UUID
    student_id: UUID
    enrollment_id: UUID
    lesson_id: UUID
    status: str  # present/absent/late/excused
    marked_by_id: UUID  # Mentor
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

### Входящие (от других доменов)

```python
# От Submissions Domain
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

# От Assessment Domain
@receiver(assessment_needs_mentor_review)
def handle_assessment_needs_mentor_review(sender, event, **kwargs):
    """
    Добавить assessment attempt в очередь ментора.
    """
    pass
```

---

## Примеры flow

### Пример 1: Создание группы и занятий

```
1. Admin создаёт MentorGroup:
   - Python Backend #12
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

### Пример 2: Отметка посещаемости

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

### Пример 3: Mentor override для lesson completion

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

### Пример 4: Mentor work queue

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

## ADR (новые решения)

### ADR-019: Студент НЕ выбирает ментора (v1)

**Контекст:** Нужна система назначения студентов менторам.

**Отклонённые варианты:**
- Студент выбирает ментора сам — балансировка нагрузки невозможна

**Решение:** Только admin назначает студентов в группы. Один ментор → одна группа → N студентов.

**Причина:** Популярные менторы перегружены, непопулярные простаивают. Нужен контроль.

**Последствия:** В v2 можно добавить авто-распределение (round-robin, capacity-based).

---

### ADR-020: Расписание — динамическое, не жёсткое

**Контекст:** Нужно планировать offline занятия.

**Отклонённые варианты:**
- Привязать Module к датам (Module 1: 2026-01-01, 2026-01-03...) — ломается при переносах

**Решение:** `OfflineSession` — отдельная сущность с `scheduled_start/end`, `status` (scheduled/cancelled/rescheduled).

**Причина:** Реальная жизнь: праздники, болезнь, отключение света. Расписание должно быть гибким.

**Последствия:** Занятия можно отменять, переносить без изменения структуры модуля.

---

### ADR-021: Attendance — ментор отмечает вручную, турникет = подсказка

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

### ADR-022: Mentor override для lesson completion

**Контекст:** Offline обучение не всегда укладывается в правила (контент просмотрен, домашка сдана).

**Решение:** `LessonProgress.completion_source` может быть `mentor_override`.

**Причина:** Ментор на месте, он знает лучше. Студент может выполнить задание устно в аудитории.

**Последствия:** Нужен audit trail: `override_by_id`, `override_reason`, `override_at`.

---

### ADR-023: Mentor work queue — критичная функция для v1

**Контекст:** Ментор должен видеть что нужно проверить.

**Решение:** Read model `MentorWorkReview` — очередь работ с сортировкой (overdue → oldest).

**Причина:** Без этого ментор не знает что проверять первым. Это важнее чатов и комментариев.

**Последствия:** Таблица обновляется через события (SubmissionSubmitted, AssessmentNeedsMentorReview).

---

## Интеграция с другими доменами

### UserProgress Domain

```python
# Mentorship слушает
@receiver(lesson_progress_unlocked)
def handle_lesson_progress_unlocked(sender, event, **kwargs):
    """
    Когда урок разблокирован для offline студента,
    можно автоматически создать OfflineSession (если настроено).
    """
    pass

# Mentorship emit
AttendanceMarked → UserProgress → LessonCompleted
```

### Submissions Domain

```python
# Submissions emit
SubmissionSubmitted → Mentorship → MentorWorkReview (add to queue)

# Mentorship emit
SubmissionReviewed → Submissions → update status
```

### Assessment Domain

```python
# Assessment emit
AssessmentNeedsMentorReview → Mentorship → MentorWorkReview (add to queue)

# Mentorship emit
AssessmentResponseGraded → Assessment → update response
```

---

## Что дальше

1. ✅ Дизайн Mentorship завершён
2. 🟡 Дизайн Certificates Domain (последний)
3. ⬜ Обновить `docs/DATABASE.md` (все 4 домена)
4. ⬜ Добавить ADR-019..023 в `docs/DECISIONS.md`
5. ⬜ Обновить `docs/CONVERSATION_LOG.md`
6. ⬜ Обновить `CLAUDE.md` и `TASKS.md`
# Submissions Domain — Design v1

**Дата:** 2026-06-07  
**Статус:** ПРИНЯТО  
**Версия:** 1.0

---

## Ключевые решения

### 1. Submission — это попытка выполнения задания, не задание

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

### 2. Assignment вместо LessonHomework + ProjectTask

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

### 3. Типы submission

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

### 4. Версионирование (обязательно)

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

### 5. Статусы

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

### 6. Проверка ментора (v1 — только общий feedback)

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

### 7. Автоматическая проверка — отдельно от mentor review

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

### 8. CI интеграция — не в v1

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

### 9. Безопасность — обязательная проверка файлов

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

### 10. Один ментор на submission (v1)

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

## Схема БД

### submissions_assignment

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

### submissions_submission

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

### submissions_submissionrevision

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

### submissions_submissionfile

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

### submissions_autocheck

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

### submissions_submissionreview

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

## События

### Исходящие (из Submissions Domain)

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
    status: str  # changes_requested / approved / rejected
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

### Входящие (от других доменов)

```python
# От Learning Domain
@receiver(lesson_published)
def handle_lesson_published(sender, event: LessonPublished, **kwargs):
    """
    Если у урока есть assignment, инициализировать Submission
    для всех enrolled студентов (через Celery fan-out).
    """
    pass

# От Assessment Domain
@receiver(assessment_attempt_started)
def handle_assessment_attempt_started(sender, event, **kwargs):
    """
    Если assessment содержит project items,
    создать Assignment + Submission для студента.
    """
    pass
```

---

## Примеры flow

### Пример 1: Homework (text_answer)

```
1. Lesson published → Assignment created
2. Student enrolled → Submission created (status=draft)
3. Student writes answer → SubmissionRevision 1 created
4. Student clicks "Submit" → status=submitted, SubmissionSubmitted event
5. Mentor reviews → SubmissionReview created (score=8/10, status=approved)
6. status=approved → SubmissionApproved event
7. UserProgress listens → homework_submitted=True → check lesson completion
```

### Пример 2: Project (github_repository)

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

### Пример 3: File upload with virus scan

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

## ADR (новые решения)

### ADR-014: Assignment вместо отдельных LessonHomework и ProjectTask

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

### ADR-015: Версионирование через SubmissionRevision

**Контекст:** Студент пересдаёт работу после замечаний ментора.

**Решение:** `Submission` (контейнер) + `SubmissionRevision` (версии).

**Причина:** Студент почти всегда пересдаёт. Нужна история изменений.

**Последствия:** Ментор всегда проверяет конкретную ревизию, не Submission целиком.

---

### ADR-016: Payload JSONB для разных типов submission

**Контекст:** Разные типы submission хранят разные данные (GitHub URL vs uploaded files vs text).

**Отклонённые варианты:**
- Отдельные таблицы для каждого типа — слишком много таблиц
- Отдельные поля `github_url`, `file_id`, `text_answer` — NULL everywhere

**Решение:** `SubmissionRevision.payload JSONB` с разной структурой по типу.

**Причина:** Гибкость, легко добавлять новые типы без миграций.

**Последствия:** Валидация payload на уровне application logic, не DB constraints.

---

### ADR-017: Автопроверки отдельно от mentor review

**Контекст:** Нужны и автоматические проверки (tests, linting) и ручная проверка ментора.

**Решение:** `AutoCheck` (автомат) ≠ `SubmissionReview` (ментор). Разные таблицы.

**Причина:**
- Автопроверка может быть зелёной, но ментор поставит низкий балл за архитектуру
- Ментор может одобрить даже если coverage < 80% (есть причины)
- Не смешивать источники оценки

**Последствия:** UI должен показывать оба результата отдельно.

---

### ADR-018: Обязательная проверка файлов на вирусы

**Контекст:** Студенты загружают ZIP, PDF, DOCX — потенциальный вектор атаки.

**Решение:** Все загруженные файлы проходят ClamAV scan перед доступом ментора.

**Причина:** Безопасность. Нельзя давать ментору скачивать непроверенные файлы.

**Последствия:**
- Дополнительная задержка (секунды)
- Celery worker для сканирования
- S3 temp bucket для непроверенных файлов

---

## Что дальше

1. ✅ Дизайн Submissions завершён
2. 🟡 Дизайн Mentorship Domain (ментор как reviewer)
3. 🟡 Дизайн Certificates Domain
4. ⬜ Обновить `docs/DATABASE.md`
5. ⬜ Добавить ADR-014..018 в `docs/DECISIONS.md`
# Roadmap

## Статус доменов

| Домен         | Дизайн | Код | Тесты | Продакшн |
|---------------|:------:|:---:|:-----:|:--------:|
| Identity      | ✅     | ✅  | ?     | ?        |
| Learning      | ✅     | 🔲  | 🔲    | 🔲       |
| UserProgress  | ✅     | 🔲  | 🔲    | 🔲       |
| Assessment    | ✅     | 🔲  | 🔲    | 🔲       |
| Submissions   | 🔲     | 🔲  | 🔲    | 🔲       |
| Mentorship    | 🔲     | 🔲  | 🔲    | 🔲       |
| Notifications | 🔲     | 🔲  | 🔲    | 🔲       |
| Analytics     | 🔲     | 🔲  | 🔲    | 🔲       |
| Certificates  | 🔲     | 🔲  | 🔲    | 🔲       |

---

## Phase 1 — Ядро платформы (текущая)

**Цель:** Студент может записаться на курс и пройти его от начала до конца.

- [x] Дизайн Learning Domain
- [x] Дизайн UserProgress Domain
- [x] Дизайн Assessment Domain
- [ ] Реализация `apps/courses/` (models, selectors, services, API)
- [ ] Реализация `apps/progress/`
- [ ] Реализация `apps/assessment/`
- [ ] Integration tests: enrollment → progress → assessment → completion
- [ ] Базовый Admin UI

## Phase 2 — Submissions & Mentorship

**Цель:** Менторы могут вести группы, проверять задания.

- [ ] Дизайн Submissions Domain
- [ ] Дизайн Mentorship Domain
- [ ] Реализация `apps/submissions/`
- [ ] Реализация `apps/mentorship/`
- [ ] AttendanceMarked → UserProgress offline completion
- [ ] HomeworkSubmitted → UserProgress homework gate

## Phase 3 — Уведомления & Аналитика

- [ ] Дизайн Notifications Domain
- [ ] Email/Push уведомления для ключевых событий
- [ ] Дизайн Analytics Domain
- [ ] Dashboard для Staff/Admin

## Phase 4 — Сертификаты

- [ ] Дизайн Certificates Domain
- [ ] PDF генерация
- [ ] Публичная верификация

## Phase 5 — Масштабирование

- [ ] Redis кеш для каталога курсов
- [ ] Вынос Coding Execution в отдельный сервис
- [ ] CDN для LessonContent
- [ ] Горизонтальное масштабирование Celery workers

---

## Нерешённые вопросы

| Вопрос | Приоритет | Блокирует |
|--------|-----------|-----------|
| Сохранять ли прогресс при повторной записи на курс? | Medium | Phase 2 |
| Как хранить исходный код из coding assessment? | High | Phase 1 |
| Sandbox для execution: внутренний или внешний сервис? | High | Phase 1 |
| Мобильное приложение: нужен ли GraphQL? | Low | Phase 3 |
