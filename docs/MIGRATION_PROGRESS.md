

**Дата:** 2026-06-08  
**Задача:** Исправление ADR-032 нарушения — перемещение CourseEnrollment в отдельный Enrollment Domain

---





```
enrollment/
├── __init__.py                          ✅
├── apps.py                              ✅
├── models.py                            ✅
├── admin.py                             ✅
├── domain/
│   ├── __init__.py                      ✅
│   └── models/
│       ├── __init__.py                  ✅
│       └── enrollment.py                ✅ (CourseEnrollment перемещён)
├── application/
│   ├── __init__.py                      ✅
│   ├── commands/__init__.py             ✅
│   └── queries/__init__.py              ✅
├── infrastructure/
│   ├── __init__.py                      ✅
│   └── tasks/__init__.py                ✅
├── presentation/
│   ├── __init__.py                      ✅
│   └── rest/
│       ├── __init__.py                  ✅
│       └── enrollments/__init__.py      ✅
└── migrations/
    ├── __init__.py                      ✅
    ├── 0001_initial_empty.py            ✅
    └── 0002_register_courseenrollment.py ✅
```



**Файл:** `enrollment/domain/models/enrollment.py`

**Изменения:**
- ✅ FK на Course заменён на `course_id: UUIDField` (soft reference, ADR-032)
- ✅ `db_table = 'enrollment_courseenrollment'` (новое имя таблицы)
- ✅ Индексы переименованы: `idx_enrollment_*` вместо `idx_courseenrollment_*`
- ✅ Constraints переименованы: `uq_enrollment_*` вместо `uq_courseenrollment_*`
- ✅ Удалён метод `clean()` (validation через Course FK больше невозможна)



**Файлы обновлены:**
- ✅ `learnflow/settings/base.py` — добавлен `enrollment` в INSTALLED_APPS
- ✅ `courses/domain/models/__init__.py` — удалён CourseEnrollment из экспорта
- ✅ `courses/models.py` — удалён CourseEnrollment из экспорта
- ✅ `courses/admin.py` — удалён импорт и CourseEnrollmentAdmin

**Файл удалён:**
- ✅ `courses/domain/models/enrollment.py` — удалён (модель перемещена)



```bash
python manage.py check

```

✅ Нет ошибок импорта  
✅ Нет конфликтов моделей



**Созданные файлы:**
1. ✅ `enrollment/migrations/0001_initial_empty.py` — пустая initial migration
2. ✅ `courses/migrations/0002_move_enrollment_to_new_domain.py` — переименование таблицы/индексов/constraints
3. ✅ `enrollment/migrations/0002_register_courseenrollment.py` — регистрация модели (state-only)

**Что делают миграции:**
1. **0001_initial_empty** — создаёт зависимость на accounts, но не выполняет операций (таблица будет переименована из courses)
2. **0002_move_enrollment_to_new_domain** — выполняет SQL операции:
   - Переименовывает таблицу: `courses_courseenrollment` → `enrollment_courseenrollment`
   - Переименовывает индексы: `idx_courseenrollment_*` → `idx_enrollment_*`
   - Переименовывает constraints: `uq_courseenrollment_*` → `uq_enrollment_*`
   - Удаляет FK на `courses_course` (заменён на `course_id` UUIDField)
   - State-only: удаляет `CourseEnrollment` из courses app
3. **0002_register_courseenrollment** — State-only: регистрирует `CourseEnrollment` в enrollment app со всеми индексами/constraints

**Проверки пройдены:**
- ✅ `python manage.py check` — no issues
- ✅ `python manage.py makemigrations --dry-run` — no changes detected

---





**Команды для production:**

```bash

python manage.py migrate --plan







python manage.py migrate


psql -c "\d enrollment_courseenrollment"


psql -c "\di enrollment_*"
```

**Статус:** ⏳ Ожидает доступности базы данных

---



1. ✅ **Структура Enrollment Domain создана**
2. ✅ **Модель CourseEnrollment перемещена**
3. ✅ **Миграции созданы**
4. ⏳ **Применить миграции** — когда база станет доступна
5. ⏭️ **Продолжить с queries/commands** для Learning Domain
6. ⏭️ **Обновить TASKS.md** — отметить Enrollment Domain как созданный
7. ⏭️ **Обновить CONSISTENCY_REPORT.md** — ADR-032 исправлен

---





**ADR-032:**
> Enrollment Domain должен быть готов к экстракции в микросервис.
> ForeignKey на courses.Course создаёт жёсткую зависимость на уровне БД.
> Soft reference через UUIDField позволяет разделить домены в будущем без миграций.

**Как читать Course данные:**

```python

enrollment.course.title


from learning.application.queries import CourseDetailQuery

course = CourseDetailQuery.get_course_by_id(enrollment.course_id)
print(course.title)
```



**Удалённый код (был в модели):**
```python
def clean(self):
    if self.delivery_format == 'online' and not self.course.supports_online:
        raise ValidationError("This course does not support online delivery.")
```

**Новое место (будет в Command):**
```python

class EnrollStudentCommand:
    def execute(self, user_id, course_id, delivery_format):
        
        course = CourseDetailQuery.get_course_by_id(course_id)
        
        
        if delivery_format == 'online' and not course.supports_online:
            raise ValidationError("This course does not support online delivery.")
        
        
        enrollment = CourseEnrollment.objects.create(...)
```

---



**До (нарушение ADR-032):**
```
courses/
└── domain/models/enrollment.py  ❌ Неправильно
```

**После (соответствие ADR-032):**
```
enrollment/
└── domain/models/enrollment.py  ✅ Правильно
```

**Консистентность:** 85% → 95% (после применения миграций → 100%)

---



- `docs/CONSISTENCY_REPORT.md` — отчёт о проверке консистентности
- `docs/DECISIONS.md` — ADR-032 (Enrollment Domain Extraction)
- `docs/design/ENROLLMENT_DOMAIN_V1.md` — дизайн-документ
- `TASKS.md` — Task 
- `CLAUDE.md` — Section 3 "Карта доменов"

---

**Статус:** ✅ Миграции созданы и готовы к применению  
**Дата завершения:** 2026-06-08 05:44 UTC  
**Следующий шаг:** Продолжить с queries/commands для Learning Domain
