

**Status:** Approved  
**Date:** 2026-06-08  
**Author:** Architecture Team  
**Related ADR:** ADR-032 (Enrollment Domain Extraction)

---



**Enrollment Domain** — отдельный bounded context, отвечающий за **access control** и **contract management** между студентами и курсами.

**Ключевое отличие от Learning Domain:**
- **Learning** = Content (что изучаем: Course, Module, Lesson)
- **Enrollment** = Access & Contract (кто изучает, на каких условиях, есть ли доступ)

**Enrollment = Integration Hub** для всей LMS платформы:
```
Payment → Enrollment → Progress → Certificates
            ↓
        Learning
```

---





| Ответственность          | Описание                                                     |
|--------------------------|--------------------------------------------------------------|
| **Access Control**       | Проверка: может ли студент получить доступ к курсу?         |
| **Contract Terms**       | Online/Offline, даты начала/окончания, статус оплаты         |
| **Enrollment Lifecycle** | pending → active → suspended → dropped → completed           |
| **Integration Hub**      | Центральная точка интеграции Payment → Progress → Certificates |
| **Business Rules**       | Prerequisites, max_students, enrollment deadlines            |



- ❌ Course content (это Learning Domain)
- ❌ Student progress (это Progress Domain)
- ❌ Payment processing (это Payment Domain)
- ❌ Certificates generation (это Certificates Domain)

---





**Описание:** Контракт между студентом и курсом.

```python

from django.db import models
from shared.domain.base_models import UUIDModel, TimestampedModel

class CourseEnrollment(UUIDModel, TimestampedModel):
    """
    Aggregate Root: Student's contract with a course.
    
    Responsibility:
    - Access rights (can student access course?)
    - Enrollment status (active, suspended, dropped, completed)
    - Delivery format (online, offline, hybrid)
    - Payment linkage (payment_id)
    - Timeline (enrolled_at, start_date, end_date, completed_at)
    
    Does NOT own:
    - Progress (that's progress/ domain)
    - Payment details (that's payment/ domain)
    - Course content (that's learning/ domain)
    """
    
    
    user = models.ForeignKey('identity.User', on_delete=models.PROTECT)
    course_id = models.UUIDField()  
    
    
    delivery_format = models.CharField(
        max_length=10,
        choices=[
            ('online', 'Online'),
            ('offline', 'Offline'),
            ('hybrid', 'Hybrid')
        ]
    )
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Full'),
            ('limited', 'Limited'),
            ('preview', 'Preview')
        ],
        default='full'
    )
    
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),        
            ('active', 'Active'),          
            ('suspended', 'Suspended'),    
            ('dropped', 'Dropped'),        
            ('completed', 'Completed'),    
        ],
        default='pending'
    )
    
    
    payment_id = models.UUIDField(null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    enrolled_by = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='enrollments_created'
    )
    
    start_date = models.DateField(null=True, blank=True)  
    end_date = models.DateField(null=True, blank=True)    
    
    
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_reason = models.TextField(null=True, blank=True)
    
    
    dropped_at = models.DateTimeField(null=True, blank=True)
    dropped_reason = models.TextField(null=True, blank=True)
    
    
    completed_at = models.DateTimeField(null=True, blank=True)
    
    
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'enrollment_courseenrollment'
        unique_together = [('user', 'course_id')]
        indexes = [
            models.Index(fields=['status', 'deleted_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['course_id', 'status']),
            models.Index(fields=['payment_id']),
        ]
    
    def can_access_course(self) -> bool:
        """Business rule: Check if student has access."""
        if self.status != 'active':
            return False
        
        if self.payment_status not in ['paid', 'pending']:
            return False
        
        
        now = timezone.now().date()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def is_expired(self) -> bool:
        """Check if enrollment has expired."""
        if not self.end_date:
            return False
        return timezone.now().date() > self.end_date
```

**Таблица:** `enrollment_courseenrollment`

**Индексы:**
- `idx_enrollment_status_deleted`
- `idx_enrollment_user_status`
- `idx_enrollment_course_status`
- `idx_enrollment_payment_id`

**Уникальные ограничения:**
- `uq_enrollment_user_course` — один студент не может записаться на курс дважды

---



**Описание:** Правила доступа к контенту курса.

```python

class AccessRule(UUIDModel, TimestampedModel):
    """
    Access rules for course content.
    
    Examples:
    - Course becomes available 3 days after enrollment
    - Module 2 unlocks only after Module 1 completion
    - Bonus content available only for paid students
    """
    
    enrollment = models.ForeignKey(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name='access_rules'
    )
    
    resource_type = models.CharField(
        max_length=20,
        choices=[
            ('course', 'Course'),
            ('module', 'Module'),
            ('lesson', 'Lesson'),
            ('content', 'Content'),
        ]
    )
    resource_id = models.UUIDField()  
    
    rule_type = models.CharField(
        max_length=30,
        choices=[
            ('time_based', 'Time-based'),          
            ('prerequisite', 'Prerequisite'),      
            ('payment_tier', 'Payment Tier'),      
            ('delivery_format', 'Delivery Format'), 
        ]
    )
    
    
    rule_config = models.JSONField(default=dict)
    
    
    
    
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'enrollment_accessrule'
        indexes = [
            models.Index(fields=['enrollment', 'resource_type']),
            models.Index(fields=['resource_id']),
        ]
```

**Таблица:** `enrollment_accessrule`

---



**Описание:** Prerequisites для записи на курс.

```python

class EnrollmentPrerequisite(UUIDModel, TimestampedModel):
    """
    Prerequisites for enrolling in a course.
    
    Examples:
    - "Backend Advanced" requires "Python Fundamentals" completion
    - "Backend Advanced" requires "Final Project" score >= 70
    - "Backend Advanced" requires "Junior Certificate"
    """
    
    course_id = models.UUIDField()  
    
    prerequisite_type = models.CharField(
        max_length=20,
        choices=[
            ('course', 'Course Completion'),
            ('assessment', 'Assessment Score'),
            ('certificate', 'Certificate'),
            ('custom', 'Custom Rule'),
        ]
    )
    
    
    prerequisite_config = models.JSONField(default=dict)
    
    
    
    
    
    is_required = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        db_table = 'enrollment_prerequisite'
        ordering = ['order']
        indexes = [
            models.Index(fields=['course_id', 'is_required']),
        ]
```

**Таблица:** `enrollment_prerequisite`

---



**Описание:** Лист ожидания когда курс заполнен.

```python

class Waitlist(UUIDModel, TimestampedModel):
    """
    Waitlist for learning that are full.
    
    When a spot opens up:
    1. Send notification to next person in queue
    2. Give them 24 hours to enroll
    3. If they don't enroll, move to next person
    """
    
    user = models.ForeignKey('identity.User', on_delete=models.CASCADE)
    course_id = models.UUIDField()  
    
    position = models.PositiveIntegerField()  
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('waiting', 'Waiting'),
            ('notified', 'Notified'),
            ('enrolled', 'Enrolled'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        default='waiting'
    )
    
    notified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)  
    
    class Meta:
        db_table = 'enrollment_waitlist'
        unique_together = [('user', 'course_id')]
        ordering = ['position']
        indexes = [
            models.Index(fields=['course_id', 'status', 'position']),
        ]
```

**Таблица:** `enrollment_waitlist`

---





```python

from enum import Enum

class EnrollmentStatus(str, Enum):
    PENDING = 'pending'       
    ACTIVE = 'active'         
    SUSPENDED = 'suspended'   
    DROPPED = 'dropped'       
    COMPLETED = 'completed'   
    
    @property
    def can_access(self) -> bool:
        """Can student access course in this status?"""
        return self == EnrollmentStatus.ACTIVE
    
    @property
    def is_terminal(self) -> bool:
        """Is this a terminal state?"""
        return self in [EnrollmentStatus.DROPPED, EnrollmentStatus.COMPLETED]
```



```python

class DeliveryFormat(str, Enum):
    ONLINE = 'online'    
    OFFLINE = 'offline'  
    HYBRID = 'hybrid'    
```



```python

class AccessLevel(str, Enum):
    FULL = 'full'           
    LIMITED = 'limited'     
    PREVIEW = 'preview'     
```

---





```python

from django.db import transaction
from enrollment.domain.models.enrollment import CourseEnrollment
from shared.infrastructure.outbox.publisher import publish_to_outbox

class EnrollmentDomainService:
    """Complex business logic for enrollment."""
    
    @staticmethod
    def can_student_enroll(user, course_id) -> tuple[bool, str]:
        """
        Check all enrollment business rules.
        
        BR-01: Student cannot enroll twice in same course
        BR-02: Course must be published
        BR-03: Course must not be full (max_students)
        BR-04: Student must meet prerequisites
        """
        
        if CourseEnrollment.objects.filter(
            user=user,
            course_id=course_id,
            status__in=['pending', 'active', 'suspended']
        ).exists():
            return False, "Already enrolled in this course"
        
        
        from learning.application.queries.course_detail import CourseCatalogQueryHandler
        try:
            course = CourseCatalogQueryHandler.get_by_id(course_id)
            if course.status != 'published':
                return False, "Course is not available for enrollment"
        except Course.DoesNotExist:
            return False, "Course not found"
        
        
        if course.max_students:
            active_count = CourseEnrollment.objects.filter(
                course_id=course_id,
                status='active'
            ).count()
            if active_count >= course.max_students:
                return False, "Course is full"
        
        
        from enrollment.domain.services.prerequisite_checker import PrerequisiteChecker
        has_prereqs, missing = PrerequisiteChecker.check(user, course_id)
        if not has_prereqs:
            return False, f"Missing prerequisites: {', '.join(missing)}"
        
        return True, ""
    
    @staticmethod
    @transaction.atomic
    def enroll_student(user, course_id, delivery_format, payment_id=None):
        """
        Core enrollment logic.
        
        Returns: CourseEnrollment
        """
        
        can_enroll, reason = EnrollmentDomainService.can_student_enroll(user, course_id)
        if not can_enroll:
            raise ValidationError(reason)
        
        
        enrollment = CourseEnrollment.objects.create(
            user=user,
            course_id=course_id,
            delivery_format=delivery_format,
            payment_id=payment_id,
            status='pending' if payment_id else 'active',
            payment_status='pending' if payment_id else 'paid',
            enrolled_by=user,
        )
        
        
        transaction.on_commit(lambda: publish_to_outbox(
            event_type='StudentEnrolled',
            aggregate_id=enrollment.id,
            payload={
                'enrollment_id': str(enrollment.id),
                'user_id': str(user.id),
                'course_id': str(course_id),
                'delivery_format': delivery_format,
                'status': enrollment.status,
                'occurred_at': timezone.now().isoformat(),
            }
        ))
        
        return enrollment
```



```python

class AccessControlService:
    """Check if student can access specific content."""
    
    @staticmethod
    def can_access_content(user, course_id, content_id) -> tuple[bool, str]:
        """
        Check if student has access to specific content.
        
        Checks:
        1. Active enrollment
        2. Access rules (time-based, prerequisites)
        3. Payment status
        """
        
        try:
            enrollment = CourseEnrollment.objects.get(
                user=user,
                course_id=course_id,
                status='active'
            )
        except CourseEnrollment.DoesNotExist:
            return False, "Not enrolled in course"
        
        
        if not enrollment.can_access_course():
            return False, "Enrollment is not active"
        
        
        rules = AccessRule.objects.filter(
            enrollment=enrollment,
            resource_id=content_id,
            is_active=True
        )
        
        for rule in rules:
            can_access, reason = AccessControlService._check_rule(enrollment, rule)
            if not can_access:
                return False, reason
        
        return True, ""
    
    @staticmethod
    def _check_rule(enrollment, rule) -> tuple[bool, str]:
        """Check specific access rule."""
        if rule.rule_type == 'time_based':
            days_after = rule.rule_config.get('days_after_enrollment', 0)
            unlock_date = enrollment.enrolled_at + timedelta(days=days_after)
            if timezone.now() < unlock_date:
                return False, f"Content unlocks on {unlock_date.date()}"
        
        elif rule.rule_type == 'payment_tier':
            required_status = rule.rule_config.get('required_payment_status')
            if enrollment.payment_status != required_status:
                return False, "Requires paid access"
        
        
        
        return True, ""
```



```python

class PrerequisiteChecker:
    """Check if student meets prerequisites."""
    
    @staticmethod
    def check(user, course_id) -> tuple[bool, list[str]]:
        """
        Check all prerequisites for course.
        
        Returns: (has_prerequisites, missing_list)
        """
        prerequisites = EnrollmentPrerequisite.objects.filter(
            course_id=course_id,
            is_required=True
        ).order_by('order')
        
        missing = []
        
        for prereq in prerequisites:
            has_prereq = PrerequisiteChecker._check_single(user, prereq)
            if not has_prereq:
                missing.append(prereq.get_display_name())
        
        return len(missing) == 0, missing
    
    @staticmethod
    def _check_single(user, prereq) -> bool:
        """Check single prerequisite."""
        if prereq.prerequisite_type == 'course':
            required_course_id = prereq.prerequisite_config['required_course_id']
            return CourseEnrollment.objects.filter(
                user=user,
                course_id=required_course_id,
                status='completed'
            ).exists()
        
        elif prereq.prerequisite_type == 'assessment':
            
            pass
        
        elif prereq.prerequisite_type == 'certificate':
            
            pass
        
        return True
```

---





```python

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class StudentEnrolledEvent:
    """
    Event payload for Outbox.
    
    Consumed by:
    - Progress Domain (initialize CourseProgress)
    - Analytics Domain (track enrollment)
    - Notifications Domain (welcome email)
    """
    enrollment_id: UUID
    user_id: UUID
    course_id: UUID
    delivery_format: str
    status: str
    occurred_at: datetime
```

**Обработка:** Outbox Pattern → Celery task каждые 10 секунд

**Consumers:**
- `progress/` → initialize CourseProgress
- `analytics/` → track enrollment metrics
- `notifications/` → send welcome email

---



```python

from django.dispatch import Signal

enrollment_completed = Signal()
```

**Emitted when:** Progress Domain отправляет `CourseCompleted` → Enrollment marks as completed

**Consumers:**
- `certificates/` → generate certificate
- `analytics/` → completion metrics

---



```python

from django.dispatch import Signal

access_granted = Signal()
access_revoked = Signal()
```

**Use case:** Когда payment succeeds/fails → notify Learning Domain

---



```python

enrollment_suspended = Signal()
```

**Consumers:**
- `progress/` → freeze progress tracking
- `notifications/` → notify student

---



| BR-ID | Rule                                                                  |
|-------|-----------------------------------------------------------------------|
| BR-01 | Student cannot enroll twice in the same course                       |
| BR-02 | Course must be published to allow enrollment                         |
| BR-03 | Course cannot exceed max_students limit                              |
| BR-04 | Student must meet all required prerequisites                         |
| BR-05 | Enrollment status can only change via approved transitions           |
| BR-06 | Free courses → instant active status (no payment required)           |
| BR-07 | Paid courses → pending until payment succeeds                        |
| BR-08 | Payment failure → suspend enrollment (not drop)                      |
| BR-09 | Refund → drop enrollment (terminal state)                            |
| BR-10 | Enrollment completion → triggered by Progress Domain (CourseCompleted) |

**Status Transitions:**

```
pending ──PaymentSucceeded──► active ──CourseCompleted──► completed
   │                             │
   │                             │
   └──PaymentFailed──► suspended ─┘
   
active ──Drop──► dropped (terminal)
```

---





```python

@receiver(payment_succeeded_signal)
def handle_payment_succeeded(sender, payment_id, enrollment_id, **kwargs):
    """When payment succeeds → activate enrollment."""
    from enrollment.application.commands.activate_enrollment import ActivateEnrollmentHandler
    ActivateEnrollmentHandler.handle(enrollment_id, payment_id)
```



```python



@receiver(student_enrolled_outbox)
def handle_student_enrolled(sender, enrollment_id, course_id, user_id, **kwargs):
    """Initialize progress tracking."""
    from progress.application.commands.initialize_progress import InitializeProgressHandler
    InitializeProgressHandler.handle(enrollment_id, course_id, user_id)
```



```python

@receiver(course_completed_signal)
def handle_course_completed(sender, enrollment_id, **kwargs):
    """Mark enrollment as completed."""
    from enrollment.application.commands.complete_enrollment import CompleteEnrollmentHandler
    CompleteEnrollmentHandler.handle(enrollment_id)
```

---





**Description:** Enroll student in course

**Request:**
```json
{
  "course_id": "uuid",
  "delivery_format": "online"
}
```

**Response:**
```json
{
  "id": "uuid",
  "course_id": "uuid",
  "user_id": "uuid",
  "status": "pending",
  "delivery_format": "online",
  "enrolled_at": "2026-06-08T10:00:00Z"
}
```

---



**Description:** List my enrollments

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "course": {
        "id": "uuid",
        "title": "Python Backend Fundamentals"
      },
      "status": "active",
      "delivery_format": "online",
      "enrolled_at": "2026-06-08T10:00:00Z",
      "progress_percentage": 45
    }
  ]
}
```

---



**Description:** Get enrollment details

---



**Description:** Drop enrollment (terminal action)

**Request:**
```json
{
  "reason": "Changed career path"
}
```

---



**Description:** Check if student can access specific content

**Request:**
```json
{
  "content_id": "uuid"
}
```

**Response:**
```json
{
  "can_access": true,
  "reason": ""
}
```

---





```bash
mkdir -p enrollment/domain/models
mkdir -p enrollment/domain/value_objects
mkdir -p enrollment/domain/events
mkdir -p enrollment/domain/services
mkdir -p enrollment/application/commands
mkdir -p enrollment/application/queries
mkdir -p enrollment/application/handlers
mkdir -p enrollment/presentation/rest/enrollments
```



```python














```



```bash

grep -r "from learning.models import CourseEnrollment"



```



Move enrollment-related services from `learning/` to `enrollment/domain/services/`



- Old: `POST /api/v1/courses/{id}/enroll/`
- New: `POST /api/v1/enrollments/`

---





```python

def test_can_access_course_when_active_and_paid():
    enrollment = CourseEnrollment(status='active', payment_status='paid')
    assert enrollment.can_access_course() == True

def test_cannot_access_course_when_suspended():
    enrollment = CourseEnrollment(status='suspended', payment_status='paid')
    assert enrollment.can_access_course() == False
```



```python

def test_enroll_student_publishes_event():
    cmd = EnrollStudentCommand(user_id=user.id, course_id=course.id, ...)
    enrollment = EnrollStudentHandler.handle(cmd)
    
    
    assert DomainEventOutbox.objects.filter(
        event_type='StudentEnrolled',
        aggregate_id=enrollment.id
    ).exists()
```

---



1. **Waitlist System** — автоматическое уведомление при освобождении места
2. **Enrollment Bundles** — запись на несколько курсов одновременно
3. **Trial Period** — 7 дней бесплатного доступа
4. **Group Enrollments** — корпоративные лицензии для компаний
5. **Auto-renewal** — автоматическое продление подписки
6. **Transfer Enrollment** — перенос на другой курс

---



- ADR-032: Enrollment Domain Extraction
- docs/ARCHITECTURE_REVISED.md
- docs/DATABASE.md (Enrollment tables)
- docs/design/PAYMENT_DOMAIN_V1.md

---

**Last Updated:** 2026-06-08  
**Next Review:** After Phase 1B implementation
