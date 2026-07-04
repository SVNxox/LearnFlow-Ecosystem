

**Current Status:** Phase 1B.1 (Identity API Refactoring) ✅ Complete  
**Date:** 2026-06-08

---




- ✅ Feature-Sliced structure applied
- ✅ Domain-prefixed URLs (`/api/v1/identity/`)
- ✅ Shared error schemas
- ✅ ADR-034 & API_VERSIONING.md created
- ✅ OpenAPI schema tested (25 KB, 14 endpoints)

**Result:** Identity Domain is now the **reference implementation** for all future domains.

---




1. Fix `UserProfileSerializer` type hints:
   ```python
   
   @extend_schema_field(serializers.ListField(child=serializers.CharField()))
   def get_roles(self, obj):
       ...
   
   @extend_schema_field(UserSettingsSerializer)
   def get_settings(self, obj):
       ...
   ```

2. Fix `LogoutAllView` missing serializer:
   ```python
   
   class LogoutAllView(APIView):
       serializer_class = LogoutRequestSerializer  
       ...
   ```

3. Re-generate schema and verify no errors:
   ```bash
   python manage.py spectacular --file schema.yaml --validate
   ```

**Estimated time:** 30 minutes

---




- [ ] POST `/api/v1/identity/auth/register/` (create user)
- [ ] POST `/api/v1/identity/auth/login/` (get tokens)
- [ ] POST `/api/v1/identity/auth/token/refresh/` (refresh token)
- [ ] POST `/api/v1/identity/auth/logout/` (invalidate token)
- [ ] POST `/api/v1/identity/auth/logout/all/` (invalidate all)
- [ ] GET `/api/v1/identity/auth/verify-email/?token=...` (verify)
- [ ] POST `/api/v1/identity/auth/verify-email/resend/` (resend)
- [ ] POST `/api/v1/identity/auth/password-reset/` (request reset)
- [ ] POST `/api/v1/identity/auth/password-reset/confirm/` (confirm reset)


- [ ] GET `/api/v1/identity/profile/me/` (get profile)
- [ ] PATCH `/api/v1/identity/profile/me/` (update profile)
- [ ] POST `/api/v1/identity/profile/me/password/` (change password)
- [ ] GET `/api/v1/identity/profile/me/settings/` (get settings)
- [ ] PATCH `/api/v1/identity/profile/me/settings/` (update settings)
- [ ] GET `/api/v1/identity/profile/me/sessions/` (list sessions)
- [ ] DELETE `/api/v1/identity/profile/me/sessions/{id}/` (revoke session)


- [ ] Open `/api/v1/schema/swagger/`
- [ ] Verify tags: `Identity — Auth`, `Identity — Profile`, etc.
- [ ] Test "Try it out" functionality
- [ ] Verify error responses match `ErrorResponseSerializer`

**Tools:**
- Postman/Insomnia collection (export from Swagger)
- Or curl scripts
- Or pytest integration tests

**Estimated time:** 2-3 hours

---



**After manual testing passes:**

1. Backup old files (just in case):
   ```bash
   mkdir -p .backups/phase1b1
   cp identity/views.py .backups/phase1b1/
   cp identity/serializers.py .backups/phase1b1/
   cp identity/urls.py .backups/phase1b1/
   ```

2. Delete old files:
   ```bash
   rm identity/views.py
   rm identity/serializers.py
   rm identity/urls.py
   ```

3. Search for imports referencing old files:
   ```bash
   grep -r "from accounts.views import" .
   grep -r "from accounts.serializers import" .
   grep -r "from accounts.urls import" .
   ```

4. Update any found imports to new structure.

5. Run tests:
   ```bash
   python manage.py test identity
   ```

**Estimated time:** 30 minutes

---



Apply Feature-Sliced structure to `courses/` app (Learning Domain).


```
courses/
├── models.py              ❌ Multiple models
├── admin.py
├── apps.py
└── ...
```


```
learning/                  
├── domain/
│   ├── models/
│   │   ├── course.py      
│   │   ├── module.py      
│   │   ├── lesson.py      
│   │   └── content.py     
│   ├── value_objects/
│   │   ├── course_slug.py
│   │   └── delivery_format.py
│   ├── events/
│   │   ├── course_published.py
│   │   └── lesson_published.py
│   └── services/
│       └── publication.py
├── application/
│   ├── commands/
│   │   ├── create_course.py
│   │   ├── publish_course.py
│   │   └── create_lesson.py
│   ├── queries/
│   │   ├── course_catalog.py
│   │   ├── course_detail.py
│   │   └── lesson_detail.py
│   └── handlers/
│       └── event_handlers.py
├── presentation/rest/
│   └── v1/
│       ├── courses/
│       │   ├── create.py
│       │   ├── update.py
│       │   ├── publish.py
│       │   ├── detail.py
│       │   ├── list.py
│       │   └── serializers/
│       └── lessons/
│           ├── detail.py
│           └── serializers/
└── admin/
    ├── course.py
    └── lesson.py
```


1. Create directory structure
2. Split `courses/models.py` → `domain/models/{course,module,lesson,content}.py`
3. Create value objects (CourseSlug, DeliveryFormat)
4. Create domain events (CoursePublished, LessonPublished)
5. Extract services (publication.py)
6. Create Application Layer (Commands, Queries, Handlers)
7. Create Presentation Layer (REST API v1)
8. Update URLs: `/api/v1/learning/courses/`
9. Update `INSTALLED_APPS` in settings
10. Create and run migrations
11. Update admin
12. Write tests

**Reference:** `accounts/` (completed in Phase 1B.1)

**Estimated time:** 1-2 days

---



Create Enrollment Domain from scratch (no existing code to refactor).


```
enrollment/
├── domain/
│   ├── models/
│   │   ├── enrollment.py      
│   │   ├── access_rule.py
│   │   ├── prerequisite.py
│   │   └── waitlist.py
│   ├── value_objects/
│   │   ├── enrollment_status.py
│   │   ├── delivery_format.py
│   │   └── access_level.py
│   ├── events/
│   │   ├── student_enrolled.py       
│   │   ├── enrollment_completed.py   
│   │   ├── access_granted.py
│   │   └── access_revoked.py
│   └── services/
│       ├── enrollment_service.py
│       ├── access_control.py
│       └── prerequisite_checker.py
├── application/
│   ├── commands/
│   │   ├── enroll_student.py
│   │   ├── drop_enrollment.py
│   │   ├── suspend_enrollment.py
│   │   └── reactivate_enrollment.py
│   ├── queries/
│   │   ├── enrollment_detail.py
│   │   ├── my_enrollments.py
│   │   └── check_access.py
│   └── handlers/
├── presentation/rest/
│   └── v1/
│       ├── enrollments/
│       │   ├── create.py
│       │   ├── detail.py
│       │   ├── list.py
│       │   ├── drop.py
│       │   └── serializers/
│       └── access/
└── tests/
```


1. Read design doc: `docs/design/ENROLLMENT_DOMAIN_V1.md`
2. Create Django app: `python manage.py startapp enrollment`
3. Create directory structure
4. Implement domain models (enrollment.py, access_rule.py, prerequisite.py, waitlist.py)
5. Implement value objects
6. Implement domain events
7. Implement domain services
8. Create Application Layer
9. Create Presentation Layer
10. Update URLs: `/api/v1/enrollment/enroll/`
11. Create migrations
12. Write tests
13. Set up event handlers (integrate with Learning, Payment, Progress)

**Reference:** 
- `docs/design/ENROLLMENT_DOMAIN_V1.md`
- `accounts/` (structure reference)

**Estimated time:** 2-3 days

---



Create Payment Domain from scratch.


```
payment/
├── domain/
│   ├── models/
│   │   ├── payment.py
│   │   ├── transaction.py
│   │   ├── refund.py
│   │   └── subscription.py
│   ├── value_objects/
│   │   ├── money.py
│   │   └── payment_status.py
│   ├── events/
│   │   ├── payment_succeeded.py   
│   │   ├── payment_failed.py      
│   │   └── refund_issued.py       
│   └── services/
│       ├── payment_processor.py
│       └── refund_processor.py
├── application/
├── infrastructure/
│   ├── tasks/
│   └── integrations/
│       ├── stripe_client.py
│       └── payme_client.py     
├── presentation/rest/
│   └── v1/
│       ├── payments/
│       └── refunds/
└── tests/
```


1. Read design doc: `docs/design/PAYMENT_DOMAIN_V1.md`
2. Create Django app
3. Implement domain models
4. Implement value objects (Money, PaymentStatus)
5. Implement domain events (Outbox pattern for critical events)
6. Implement payment processor service
7. Integrate Stripe SDK
8. Integrate Payme.uz SDK (optional for MVP)
9. Create Application Layer
10. Create Presentation Layer (webhooks!)
11. Update URLs: `/api/v1/payment/create/`, `/api/v1/payment/webhook/`
12. Write tests (especially webhook handling)
13. Set up event handlers (integrate with Enrollment)

**Reference:** `docs/design/PAYMENT_DOMAIN_V1.md`

**Estimated time:** 3-4 days

---



Create UserProgress Domain from scratch.


```
progress/
├── domain/
│   ├── models/
│   │   ├── course_progress.py
│   │   ├── module_progress.py
│   │   └── lesson_progress.py
│   ├── events/
│   │   ├── lesson_completed.py    
│   │   ├── module_completed.py    
│   │   └── course_completed.py    
│   └── services/
│       ├── initialization.py
│       └── completion_cascade.py
├── application/
├── presentation/rest/
│   └── v1/
│       ├── progress/
│       └── completion/
└── tests/
```


1. Read design doc: `docs/design/learnflow-userprogress-review-v2.md`
2. Create Django app
3. Implement progress models with snapshot fields
4. Implement completion cascade logic (lesson → module → course)
5. Implement atomic counters with F() expressions
6. Implement event handlers (listen to StudentEnrolled, LessonPublished)
7. Create Application Layer
8. Create Presentation Layer
9. Update URLs: `/api/v1/progress/my-progress/`
10. Write tests (especially race conditions)

**Reference:** `docs/design/learnflow-userprogress-review-v2.md`

**Estimated time:** 2-3 days

---



1. **Assessment Domain** (v3 design ready) — 3-4 days
2. **Submissions Domain** (v1 design ready) — 2-3 days
3. **Mentorship Domain** (v1 design ready) — 2 days
4. **Certificates Domain** (v1 design ready) — 2 days

**Total estimated time:** 9-12 days

---



| Phase   | Domain           | Status      | Est. Time   |
|---------|------------------|-------------|-------------|
| 1B.1    | Identity API     | ✅ Done     | —           |
| 1B.2    | Fix warnings     | ⏳ TODO     | 30 min      |
| 1B.3    | Manual testing   | ⏳ TODO     | 2-3 hours   |
| 1B.4    | Cleanup          | ⏳ TODO     | 30 min      |
| 1B.5    | Learning         | ⏳ TODO     | 1-2 days    |
| 1B.6    | Enrollment       | ⏳ TODO     | 2-3 days    |
| 1B.7    | Payment          | ⏳ TODO     | 3-4 days    |
| 1B.8    | UserProgress     | ⏳ TODO     | 2-3 days    |
| 1B.9    | Assessment+      | ⏳ TODO     | 9-12 days   |

**Total Phase 1B:** 20-27 days (3-4 weeks)

---





**Pros:**
- Aligns with domain name in documentation
- Clearer distinction (Learning = content, Enrollment = access)

**Cons:**
- Requires migration renaming
- Breaks existing references

**Recommendation:** Yes, rename. Better to do it now than later.



**Recommendation:** No. Keep them until Phase 1B.3 (manual testing) passes.



**Recommendation:** Learning first. Enrollment depends on Learning (needs `course_id`).

---



- `CLAUDE.md` — Project instructions
- `PHASE_1B1_SUMMARY.md` — Identity API refactoring summary
- `docs/ARCHITECTURE.md` — System architecture
- `docs/DECISIONS.md` — ADRs
- `docs/design/` — Domain design documents

---

**Next Step:** Phase 1B.3 (Manual Testing) or Phase 1B.5 (Learning Domain)?
