

**Domain:** Enrollment  
**Version:** v1  
**Status:** ✅ COMPLETED  
**Date:** 2026-06-14  
**Related ADR:** ADR-032 (Enrollment Domain Extraction)

---



Enrollment Domain реализован на 100% как Integration Hub для всей LMS платформы.

**Роль:** Центральная точка интеграции для Payment → Enrollment → Progress → Certificates flow.

---





**Models (3/3):**
- ✅ CourseEnrollment (Aggregate Root) — 200+ строк
- ✅ AccessRule — 80 строк
- ✅ EnrollmentPrerequisite — 90 строк

**Value Objects (3/3):**
- ✅ EnrollmentStatus — с методами can_access, is_terminal, can_transition_to
- ✅ DeliveryFormat — online/offline/hybrid с helper методами
- ✅ AccessLevel — full/limited/preview

**Domain Services (3/3):**
- ✅ EnrollmentService — 250+ строк (enroll, activate, suspend, drop, complete)
- ✅ AccessControlService — 100 строк (can_access_content, rule checking)
- ✅ PrerequisiteChecker — 80 строк (check prerequisites)

**Domain Events (6/6):**
- ✅ StudentEnrolledEvent (Outbox Pattern) — критичное событие
- ✅ enrollment_completed (Signal)
- ✅ access_granted (Signal)
- ✅ access_revoked (Signal)
- ✅ enrollment_suspended (Signal)
- ✅ enrollment_dropped (Signal)

---



**Commands (5/5):**
- ✅ EnrollStudentCommand + Handler
- ✅ ActivateEnrollmentCommand + Handler
- ✅ SuspendEnrollmentCommand + Handler
- ✅ DropEnrollmentCommand + Handler
- ✅ CompleteEnrollmentCommand + Handler

**Queries (3/3):**
- ✅ EnrollmentDetailQuery + Handler
- ✅ MyEnrollmentsQuery + Handler
- ✅ CheckAccessQuery + Handler

**Event Handlers (4/4):**
- ✅ handle_payment_succeeded (Payment → Enrollment)
- ✅ handle_payment_failed (Payment → Enrollment)
- ✅ handle_refund_issued (Payment → Enrollment)
- ✅ handle_course_completed (Progress → Enrollment)

---



**REST API v1 Endpoints (5/5):**
- ✅ POST /api/v1/enrollment/enrollments/ — создать enrollment
- ✅ GET /api/v1/enrollment/enrollments/ — список enrollments
- ✅ GET /api/v1/enrollment/enrollments/{id}/ — детали enrollment
- ✅ POST /api/v1/enrollment/enrollments/{id}/drop/ — отказаться от курса
- ✅ GET /api/v1/enrollment/enrollments/{id}/check-access/ — проверка доступа

**Serializers (6/6) — Feature-Sliced:**
- ✅ EnrollmentCreateSerializer
- ✅ EnrollmentListSerializer
- ✅ EnrollmentDetailSerializer
- ✅ DropEnrollmentSerializer
- ✅ CheckAccessRequestSerializer
- ✅ CheckAccessResponseSerializer

---



**Migrations:**
- ✅ 0003_add_enrollment_domain_models.py — успешно применена
  - Расширен CourseEnrollment (+12 полей)
  - Созданы AccessRule, EnrollmentPrerequisite
  - Добавлены indexes и constraints

**Database:**
- ✅ 3 таблицы созданы
- ✅ 6 индексов добавлено
- ✅ 3 check constraints
- ✅ 1 unique constraint

---




- ✅ PaymentSucceeded (Outbox) → activate enrollment
- ✅ PaymentFailed (Outbox) → suspend enrollment
- ✅ RefundIssued (Outbox) → drop enrollment
- ✅ CourseCompleted (Outbox) → complete enrollment


- ✅ StudentEnrolled (Outbox) → Progress (initialize)
- ✅ enrollment_completed (Signal) → Certificates (generate)
- ✅ access_granted (Signal) → Notifications
- ✅ access_revoked (Signal) → Notifications
- ✅ enrollment_suspended (Signal) → Notifications
- ✅ enrollment_dropped (Signal) → Analytics

---



| Rule | Status | Description |
|------|--------|-------------|
| BR-01 | ✅ | Нельзя записаться дважды на один курс |
| BR-02 | ✅ | Курс должен быть опубликован (checked by caller) |
| BR-03 | ✅ | Курс не может превышать max_students (checked by caller) |
| BR-04 | ✅ | Проверка prerequisites через PrerequisiteChecker |
| BR-06 | ✅ | Бесплатные курсы → instant active status |
| BR-07 | ✅ | Платные курсы → pending until payment |
| BR-08 | ✅ | Payment failure → suspend (not drop) |
| BR-09 | ✅ | Refund → drop (terminal) |
| BR-10 | ✅ | Completion triggered by Progress Domain |

---



```
pending ──PaymentSucceeded──► active ──CourseCompleted──► completed
   │                             │
   │                             │
   └──PaymentFailed──► suspended ─┘

active ──Drop──► dropped (terminal)
```

---



| Metric | Value |
|--------|-------|
| Total Files | 34 |
| Total Lines | ~2,280 |
| Models | 3 |
| Value Objects | 3 |
| Domain Services | 3 |
| Commands | 5 |
| Queries | 3 |
| Event Handlers | 4 |
| REST API Endpoints | 5 |
| Serializers | 6 |
| Migrations | 1 |

---



- ❌ Unit Tests — not implemented
- ❌ Integration Tests — not implemented
- ❌ API Tests — not implemented

**Recommendation:** Tests should be written after Payment Domain is completed to test full integration flow.

---



**Integration Ready For:**
1. ✅ Payment Domain — event handlers готовы
2. ✅ Certificates Domain — event emission готов
3. ✅ Mentorship Domain — structure готова

**Required Before Production:**
1. Integration tests (enrollment → payment → progress → certificates)
2. Unit tests для domain services
3. API endpoint tests

---



- Design: docs/design/ENROLLMENT_DOMAIN_V1.md
- ADR: docs/DECISIONS.md (ADR-032)
- Architecture: docs/ARCHITECTURE.md
- Database: docs/DATABASE.md

---

**Status:** ✅ READY FOR INTEGRATION
**Next Domain:** Payment
