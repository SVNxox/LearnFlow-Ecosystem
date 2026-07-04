

**Назначение:** Обязательная проверка перед написанием любого кода в LearnFlow.  
**Когда использовать:** Перед созданием models, services, API endpoints, migrations, events, tasks.

---



1. **Прочитай соответствующие разделы** перед началом работы
2. **Отметь каждый пункт** — если нашёл проблему, исправь до написания кода
3. **Документируй решения** — если принял архитектурное решение, обнови ADR
4. **Не пропускай разделы** — даже если кажется, что раздел не относится к задаче

---






- [ ] Использую ли `select_related()` для FK (1:1, M:1)?
- [ ] Использую ли `prefetch_related()` для M:M и обратных FK?
- [ ] Нет ли циклов `for item in queryset:` где внутри вызываются `item.related.all()`?
- [ ] Создал ли Selector/Query класс вместо прямого ORM в views?

**Примеры:**
```python

lessons = Lesson.objects.filter(module_id=module_id)
for lesson in lessons:
    print(lesson.module.title)  


lessons = Lesson.objects.select_related('module').filter(module_id=module_id)
for lesson in lessons:
    print(lesson.module.title)  
```


- [ ] Добавил ли индексы на поля в `WHERE`, `ORDER BY`, `JOIN`?
- [ ] Использую ли `db_index=True` для FK и часто фильтруемых полей?
- [ ] Нужен ли composite index для multi-column фильтров?
- [ ] Нужен ли partial index с `condition=Q(...)` для filtered queries?
- [ ] Проверил ли что индекс из `DATABASE.md` реально есть в `models.py`?

**Примеры:**
```python

class Course(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=['category_id', 'status', '-created_at'],
                condition=Q(deleted_at__isnull=True),
                name='idx_course_cat_status'
            )
        ]
```


- [ ] Настроен ли `CONN_MAX_AGE` в production settings?
- [ ] Добавлен ли pgBouncer в архитектуру (для >10k users)?
- [ ] Настроен ли `statement_timeout` для защиты от long queries?


- [ ] Использую ли `transaction.atomic()` для мутаций?
- [ ] Нет ли тяжёлых операций (API calls, Celery tasks) внутри транзакции?
- [ ] Использую ли `transaction.on_commit()` для событий?
- [ ] Нужен ли `select_for_update()` для cascade completion?

---






- [ ] Эта модель — aggregate root или entity внутри агрегата?
- [ ] Если entity — кто её aggregate root? Правильно ли это?
- [ ] Не создаю ли я God Aggregate (>5 entities в одном агрегате)?
- [ ] Lifecycle: independent, dependent, или immutable?

**Правило:** Если сомневаешься — создай отдельный aggregate root.


- [ ] Использую ли FK только к Identity Domain (`User`)?
- [ ] Для других доменов использую ли `UUIDField` (soft reference)?
- [ ] Снимаю ли snapshot данных если ссылаюсь на другой домен?
- [ ] Не импортирую ли models из другого домена напрямую?

**Примеры:**
```python

class CourseEnrollment(models.Model):
    course = models.ForeignKey(Course, ...)  


class CourseEnrollment(models.Model):
    course_id = models.UUIDField(db_index=True)
    course_title_snapshot = models.CharField(max_length=255)
```


- [ ] Один Service/Command = одна ответственность = один use case?
- [ ] Не делает ли Service слишком много (>200 строк)?
- [ ] Правильно ли выбран домен для этого Service?

---






- [ ] Добавил ли `UniqueConstraint` для защиты от double-submit?
- [ ] Проверил ли критичные операции: enrollment, payment, certificate?
- [ ] Обрабатываю ли `IntegrityError` в API views?

**Примеры:**
```python

class CourseEnrollment(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'course_id'],
                name='uq_enrollment_user_course'
            )
        ]
```


- [ ] Есть ли `idempotency_key` для payment webhooks?
- [ ] Event handlers идемпотентны (get_or_create вместо create)?
- [ ] Celery tasks используют Redis lock для deduplication?


- [ ] Нет ли разрыва между check access и write operation?
- [ ] Использую ли `select_for_update()` для check+lock в одной транзакции?
- [ ] Настроен ли `nowait=True` для fail-fast при lock contention?

**Примеры:**
```python

if has_access(user, resource):  
    
    write_to_resource(resource)  


with transaction.atomic():
    resource = Resource.objects.select_for_update().get(
        id=resource_id,
        owner=user  
    )
    write_to_resource(resource)
```

---






- [ ] Это критичное событие (creates root, money, external API)?  
  → **Outbox Pattern**
- [ ] Это обычное событие (counter increment, notification)?  
  → **Django Signal**

**Критерии Outbox:**
1. Создаёт aggregate root (нельзя потерять)
2. Меняет деньги/баллы/сертификаты
3. Уходит во внешний сервис (retry нужен)
4. Потеря события = data corruption


- [ ] Handler использует `get_or_create()` вместо `create()`?
- [ ] Повторная обработка события безопасна?
- [ ] Добавлен ли `logger.info()` при skip duplicate events?

**Примеры:**
```python

def handle_student_enrolled(payload):
    progress, created = CourseProgress.objects.get_or_create(
        enrollment_id=payload['enrollment_id'],
        defaults={'status': 'not_started', ...}
    )
    if not created:
        logger.info(f"CourseProgress already exists: {progress.id}")
```


- [ ] Fan-out события идут через Celery с батчингом (не синхронно)?
- [ ] Batch size ≤ 500 строк?
- [ ] Есть ли rate limiting для массовых операций?

---






- [ ] Это действительно дорогой запрос (>100ms)?
- [ ] Запрос вызывается часто (>10 RPS)?
- [ ] Данные меняются редко (не чаще раза в минуту)?

**Кандидаты на кеширование:**
- Course catalog (category list, published courses)
- User profile (roles, permissions)
- Configuration (system settings)

**НЕ кешировать:**
- Progress данные (меняются постоянно)
- Payment status (критичная актуальность)
- Assessment attempts (security risk)


- [ ] Где инвалидирую кеш при update/delete?
- [ ] Использую ли cache versioning для schema changes?
- [ ] Есть ли риск показать stale data?

**Примеры:**
```python

class CourseService:
    def publish_course(self, course_id):
        with transaction.atomic():
            course = Course.objects.get(id=course_id)
            course.status = 'published'
            course.save()
            
            transaction.on_commit(lambda:
                cache.delete(f'course_catalog:published')
            )
```

---






- [ ] Проверяю ли `request.user` перед доступом к объекту?
- [ ] Использую ли `get_object_or_404()` с user filter?
- [ ] Нет ли IDOR уязвимости (прямой доступ по ID)?

**Примеры:**
```python

enrollment = CourseEnrollment.objects.get(id=enrollment_id)  


enrollment = get_object_or_404(
    CourseEnrollment,
    id=enrollment_id,
    user=request.user  
)
```


- [ ] DRF защищает от SQL Injection? (Yes, если не использую `.raw()`)
- [ ] XSS: фронтенд sanitizes HTML? (React auto-escapes)
- [ ] CSRF: настроен `CSRF_COOKIE`? (DRF session auth)
- [ ] Rate limiting на auth endpoints? (❌ TODO)


- [ ] Нет ли секретов в коде?
- [ ] Используется ли `env()` для всех credentials?
- [ ] `.env` в `.gitignore`? (✅)

---






- [ ] Использую ли presigned URLs вместо proxy через Django?
- [ ] Настроен ли size limit (client-side и server-side)?
- [ ] Добавлен ли progress indicator для больших файлов?


- [ ] Virus scanning через ClamAV обязателен?
- [ ] Quarantine bucket для failed scans?
- [ ] MIME-type validation (magic bytes, не extension)?
- [ ] Whitelist allowed file types по assignment type?

**Примеры:**
```python

import magic

def validate_file_type(file):
    mime = magic.from_buffer(file.read(2048), mime=True)
    if mime not in ['application/pdf', 'application/zip']:
        raise ValidationError("Invalid file type")
```

---






- [ ] Код выполняется в Docker container (не на хосте)?
- [ ] Network isolation (no internet access)?
- [ ] Separate worker queue `coding` для sandboxed tasks?


- [ ] CPU limit (1 core)?
- [ ] Memory limit (256MB)?
- [ ] Timeout (5s для tests, 30s для projects)?
- [ ] Disk quota (100MB)?

**Примеры:**
```python

docker run --rm \
  --cpus=1 \
  --memory=256m \
  --network=none \
  --pids-limit=50 \
  --read-only \
  python:3.12-slim python /code/solution.py
```

---






- [ ] Использую ли structured logging (JSON)?
- [ ] Добавлен ли `user_id`, `enrollment_id` в context?
- [ ] Нет ли sensitive data в логах (passwords, tokens)?

**Примеры:**
```python

logger.info(
    "Student enrolled",
    extra={
        'user_id': str(user.id),
        'course_id': str(course.id),
        'delivery_format': enrollment.delivery_format
    }
)
```


- [ ] Добавлены ли метрики для критичных операций?
- [ ] Настроены ли алерты для error rate > 5%?
- [ ] Slow query logging включён в PostgreSQL?

---






- [ ] Domain Layer: unit-тесты для Services/Commands?
- [ ] Application Layer: integration тесты с реальной БД?
- [ ] API Layer: E2E тесты для happy path + error cases?


- [ ] `assertNumQueries()` для защиты от N+1?
- [ ] Load test для >100 concurrent users?

**Примеры:**
```python

def test_lesson_detail_no_n_plus_1(self):
    with self.assertNumQueries(3):  
        response = self.client.get(f'/api/lessons/{lesson.id}/')
```

---






- [ ] Нет ли `ALTER TABLE ... ADD COLUMN NOT NULL`? (блокирует таблицу!)
- [ ] Использую ли `null=True` сначала, потом backfill, потом `NOT NULL`?
- [ ] Нет ли `DROP COLUMN` без подготовительного deploy?

**Safe migration strategy:**
```sql
-- Deploy 1: Add column (nullable)
ALTER TABLE courses_course ADD COLUMN new_field VARCHAR(255) NULL;

-- Deploy 2: Backfill data
UPDATE courses_course SET new_field = 'default' WHERE new_field IS NULL;

-- Deploy 3: Make NOT NULL
ALTER TABLE courses_course ALTER COLUMN new_field SET NOT NULL;
```

---






- [ ] Измерил ли P95 latency текущего endpoint?
- [ ] Запустил ли `EXPLAIN ANALYZE` для slow queries?
- [ ] Профилировал ли код (`django-silk` или `py-spy`)?


- [ ] Используется ли `cursor-based` для больших списков (>10k rows)?
- [ ] Добавлен ли `limit` для защиты от fetch all?

---






- [ ] Нужна ли история изменений? (оценки, платежи, сертификаты = YES)
- [ ] Добавлены ли поля: `modified_by_id`, `modified_at`, `change_reason`?


- [ ] Используется ли soft delete там где реально нужен?
- [ ] Не злоупотребляю ли soft delete везде? (performance cost!)


- [ ] `USE_TZ=True` в settings? (✅)
- [ ] Все даты в UTC в БД? (✅)
- [ ] Конвертация в local timezone только в UI?

---






- [ ] Добавлен ли feature flag для новой функциональности?
- [ ] Можно ли откатить feature без code deploy?


- [ ] Celery workers масштабируются по queue depth?
- [ ] Web pods масштабируются по CPU/memory?


- [ ] Тяжёлые аналитические запросы идут в read replica?
- [ ] Используется ли materialized view для reports?


- [ ] Добавлена ли политика retention для personal data?
- [ ] Реализован ли export data endpoint?
- [ ] Реализован ли delete account endpoint (anonymization)?

---



**Создаю новую модель:**
→ Раздел 1 (Индексы) + 2 (Aggregate) + 3 (UniqueConstraints) + 13 (Audit)

**Создаю Service:**
→ Раздел 1 (N+1, Transactions) + 2 (SRP) + 4 (Events)

**Создаю API endpoint:**
→ Раздел 1 (N+1) + 6 (Security) + 9 (Logging) + 12 (Performance)

**Создаю миграцию:**
→ Раздел 11 (Zero-Downtime)

**Создаю Celery task:**
→ Раздел 3 (Idempotency) + 4 (Event Storm) + 9 (Monitoring)

---



- `docs/ARCHITECTURE.md` — архитектурные паттерны
- `docs/DATABASE.md` — схема БД и индексы
- `docs/SECURITY.md` — security checklist
- `docs/DECISIONS.md` — все ADR
- `CLAUDE.md` — правила работы с кодовой базой

---

**Версия:** 1.0  
**Дата:** 2026-06-08  
**Статус:** Living Document (обновляется при обнаружении новых паттернов)

---

Этот чеклист создан на основе архитектурного аудита LearnFlow и должен использоваться **перед написанием любого production-ready кода**.
