



**JWT** через `djangorestframework-simplejwt`.

```
Access token:  15 минут
Refresh token: 7 дней (ротация при каждом использовании)
```

Refresh tokens хранятся в `accounts_refreshtoken` (БД), могут быть отозваны.



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



- Прогресс студента доступен только самому студенту, его ментору и Staff/Admin
- Email не раскрывается через API (только для auth)
- `user_id` в events — UUID, не email



Студенческий код запускается в **изолированном sandbox**:
- Отдельный Docker контейнер
- Ограничения: CPU, RAM, время, сеть (отключена)
- Нет доступа к файловой системе хоста
- Нет доступа к БД или другим сервисам

Код студента **никогда** не выполняется в основном Django процессе.



- Soft delete везде — данные не удаляются физически
- При запросе на удаление аккаунта: анонимизация (email → deleted@..., имя → Deleted User)
- `progress_courseprogress.user_id` — денормализованный FK, каскадно зануляется



```
SECRET_KEY         → Environment variable (никогда в коде)
DATABASE_URL       → Environment variable
CELERY_BROKER_URL  → Environment variable
JWT_SECRET         → Environment variable
```

`.env` файл не коммитится в git (добавлен в `.gitignore`).



- ❌ Не логировать пароли, токены, персональные данные
- ❌ Не возвращать `is_correct` для quiz options студенту до завершения
- ❌ Не раскрывать `sample_answer` ментора студенту
- ❌ Не раскрывать hidden test cases студенту
- ❌ Не выполнять код студента вне sandbox



**Проверка на вирусы (обязательно):**
- Все загруженные файлы проходят ClamAV scan перед доступом ментора
- Flow: Student upload → S3 temp → ClamAV scan → S3 permanent (если passed)
- `SubmissionFile.scan_status`: pending / running / passed / failed
- Никогда не давать ментору скачивать файлы со статусом `pending` или `running`

**Ограничения размера:**
- ZIP ≤ 100 MB
- PDF ≤ 20 MB
- PPTX/DOCX ≤ 50 MB
- Проверять `Content-Length` header перед загрузкой

**MIME type validation:**
- Не доверять расширению файла (`virus.exe.pdf`)
- Проверять содержимое файла (magic bytes)
- Whitelist разрешённых MIME types по типу assignment

**Архивные бомбы:**
- Проверять `max_uncompressed_size` при распаковке
- Пример: 10 KB zip → 100 GB unpacked
- Ограничение: uncompressed ≤ 10× compressed size, max 500 MB

**См. также:** ADR-018 в DECISIONS.md

---



**Rate limiting:**
- `/api/v1/certificates/verify/{code}` — публичный endpoint
- 100 requests/hour per IP
- Защита от brute-force перебора verification codes

**Предотвращение brute-force:**
- Verification code: 6 символов (A-Z, 0-9) = 36^6 = ~2 млрд комбинаций
- Rate limiting блокирует перебор
- Никаких hints при неправильном коде

**Что показывать публично:**
- ✅ Student name, Course name, Issue date, Status (valid/revoked)
- ❌ Email студента, Enrollment details, Internal IDs

---



**MentorWorkQueue:**
- Ментор видит только submissions своих студентов
- Проверка: `student_id IN mentor.group.students`
- Нельзя проверять submissions студентов из других групп

**Attendance:**
- Только ментор группы может отмечать attendance
- Проверка: `session.group.mentor_id == request.user.id`

**Mentor override:**
- Только ментор студента может сделать lesson completion override
- Audit trail обязателен: `override_by_id`, `override_reason`, `override_at`
