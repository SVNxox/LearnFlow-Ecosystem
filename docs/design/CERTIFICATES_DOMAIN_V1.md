

**Дата:** 2026-06-08  
**Статус:** ПРИНЯТО  
**Версия:** 1.0

---





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
    "color": "
    "position": {"x": 400, "y": 300}
  },
  "course_name": {
    "font": "Montserrat-Regular",
    "size": 24,
    "color": "
    "position": {"x": 400, "y": 350}
  }
}
```

---



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



```python

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
    
    
    tasks.generate_certificate.delay(certificate.id)
```

---





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
        
        
        html = render_certificate_html(cert, template)
        
        
        pdf_bytes = HTML(string=html).write_pdf()
        
        
        s3_key = f"certificates/{cert.certificate_number}.pdf"
        pdf_url = upload_to_s3(pdf_bytes, s3_key)
        
        
        cert.pdf_url = pdf_url
        cert.pdf_generated_at = timezone.now()
        cert.status = 'issued'
        cert.issued_at = timezone.now()
        cert.save()
        
        
        dispatch(CertificateIssued(...))
        
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

---



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

@ratelimit(key='ip', rate='100/h', method='GET')
def verify_certificate(request, verification_code):
    ...
```

**Предотвращение brute-force:**
- Verification code — 6 символов (A-Z, 0-9) = 36^6 = ~2 миллиарда комбинаций
- Rate limiting блокирует перебор

---





**Контекст:** Разные курсы требуют разные дизайны сертификатов.

**Решение:** `CertificateTemplate` таблица с конфигурацией layout/fonts. `Course → template_id`.

**Причина:** Один шаблон для всех курсов — плохой UX. Backend и Design курсы требуют разные визуалы.

**Последствия:** Admin может создавать новые шаблоны без кода.

---



**Контекст:** Студент может изменить имя в профиле после получения сертификата.

**Решение:** `student_full_name_snapshot`, `course_name_snapshot` — копии на момент выдачи.

**Причина:** Сертификат — юридический документ. Нельзя автоматически обновлять.

**Последствия:** Если нужно переиздать — через `CertificateReissueRequest`.

---



**Контекст:** Генерация PDF занимает 5-15 секунд.

**Отклонённые варианты:**
- Синхронная генерация в `CourseCompleted` handler — блокирует UserProgress

**Решение:** Celery task `generate_certificate.delay()`.

**Причина:** Не блокировать завершение курса.

**Последствия:** Сертификат доступен не мгновенно (статус `pending` → `issued`).

---



**Контекст:** 10,000 скачиваний = 10,000 генераций?

**Решение:** `Certificate.pdf_url` — сохраняем PDF в S3 один раз.

**Причина:** Генерация дорогая (CPU, время). Бессмысленно повторять.

**Последствия:** S3 storage cost (минимальный).

---



**Контекст:** Нужна возможность отозвать сертификат (списывание, ошибка выдачи).

**Решение:** `Certificate.status = 'revoked'` + `revoked_at`, `revoked_by_id`, `revoked_reason`.

**Причина:** Сертификаты могут быть выданы ошибочно или нечестно получены.

**Последствия:** Публичная страница показывает "Certificate Revoked" с причиной.

---





```python

CourseCompleted → Certificates → request_certificate()


CertificateIssued → Notifications → send email
```



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



1. ✅ Дизайн Certificates завершён
2. ✅ Все 4 домена спроектированы (Assessment, Submissions, Mentorship, Certificates)
3. ⬜ Обновить `docs/DATABASE.md` (добавить все 4 домена)
4. ⬜ Добавить ADR-024..028 в `docs/DECISIONS.md`
5. ⬜ Обновить `docs/CONVERSATION_LOG.md`
6. ⬜ Обновить `CLAUDE.md` (статусы доменов → ДИЗАЙН ГОТОВ)
7. ⬜ Обновить `TASKS.md` (обновить Phase 1A → завершено)
