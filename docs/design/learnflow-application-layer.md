

**Domain:** Learning Domain  
**Version:** v1.0

---



All business actions the Learning Domain must support:


1. UC-01: List all published courses
2. UC-02: Filter courses by category
3. UC-03: Filter courses by delivery format
4. UC-04: View course detail (public)
5. UC-05: View free-preview lesson
6. UC-06: List all categories
7. UC-07: Search courses by keyword


8. UC-08: Enroll in a course
9. UC-09: View my enrolled courses
10. UC-10: View course curriculum
11. UC-11: View lesson content
12. UC-12: View lesson homework definition
13. UC-13: View practice exercises
14. UC-14: View lesson quiz definition
15. UC-15: Drop a course


16. UC-16: Create a course
17. UC-17: Edit course metadata
18. UC-18: Publish a course
19. UC-19: Archive a course
20. UC-20: Delete a course (soft)
21. UC-21: Create a module
22. UC-22: Edit module metadata
23. UC-23: Publish / unpublish module
24. UC-24: Reorder modules
25. UC-25: Delete module (soft)


26. UC-26: Create a lesson
27. UC-27: Edit lesson metadata
28. UC-28: Publish / unpublish lesson
29. UC-29: Reorder lessons within a module
30. UC-30: Delete lesson (soft)
31. UC-31: Add content item to lesson
32. UC-32: Edit content item
33. UC-33: Reorder content items
34. UC-34: Delete content item
35. UC-35: Set / replace lesson homework
36. UC-36: Edit homework definition
37. UC-37: Remove homework from lesson


38. UC-38: Add practice item to lesson
39. UC-39: Edit practice item
40. UC-40: Reorder practice items
41. UC-41: Delete practice item
42. UC-42: Create lesson quiz
43. UC-43: Edit quiz settings
44. UC-44: Add question to quiz
45. UC-45: Edit question
46. UC-46: Reorder questions
47. UC-47: Add option to question
48. UC-48: Delete quiz


49. UC-49: Create course category
50. UC-50: Edit / reorder category
51. UC-51: Deactivate category
52. UC-52: Enroll student (admin)
53. UC-53: Change student delivery format
54. UC-54: View all enrollments (course)
55. UC-55: Force-drop student enrollment
56. UC-56: View unpublished draft content

**Scope boundary:** These cover content definition and enrollment creation only. Tracking progress, submitting homework, attempting quizzes, and issuing certificates are handled by separate domains.

---



Selectors are the **only** sanctioned way to read Learning Domain data. They own query optimisation, caching strategy, and visibility rules.



Handles all public-facing catalog queries.

| Method | Description |
|--------|-------------|
| `get_published_courses(filters, user)` | Returns published courses with annotations. Applies category/format filters. |
| `get_course_card(slug)` | Lightweight single-course read for catalog card. |
| `get_all_categories()` | Returns active categories with course counts. |
| `search_courses(query, user)` | Full-text search on title + description. |

**Filters:** `category_slug`, `delivery_format`, `language`, `page`, `page_size`



Full course detail reads with visibility-aware filtering.

| Method | Description |
|--------|-------------|
| `get_course_detail(course_id, user)` | Full course + modules + lessons (metadata only). |
| `get_course_for_author(course_id, user)` | Admin/Staff view - returns all drafts. |
| `get_modules_for_course(course_id, user)` | Ordered visible modules. |
| `get_course_by_slug(slug, user)` | Slug-based lookup. |

**Visibility Rules:**
- Unauthenticated: Published courses only
- Student (enrolled): Published content only
- Staff / Admin: All statuses including draft



Lesson-level reads including all child components.

| Method | Description |
|--------|-------------|
| `get_lesson_detail(lesson_id, user)` | Returns lesson + all components. Checks enrollment. |
| `get_lesson_content(lesson_id, user)` | Returns ordered LessonContent items. |
| `get_lesson_homework(lesson_id, user)` | Returns LessonHomework definition or None. |
| `get_lesson_practice(lesson_id, user)` | Returns ordered LessonPractice items. |
| `get_lessons_for_module(module_id, user)` | Ordered lesson list. |



Enrollment reads used internally and by other domains.

| Method | Description |
|--------|-------------|
| `get_enrollment(user_id, course_id)` | Returns single CourseEnrollment or None. |
| `get_enrollments_for_user(user_id, status)` | All enrollments for a student. |
| `get_enrollments_for_course(course_id, status)` | All student enrollments in a course. |
| `is_enrolled(user_id, course_id)` | Fast boolean check for active enrollment. |
| `get_active_enrollment_count(course_id)` | Integer count for course detail. |



Quiz structure reads for Assessment domain.

| Method | Description |
|--------|-------------|
| `get_quiz_with_questions(quiz_id)` | Returns LessonQuiz + ordered questions. |
| `get_quiz_answer_key(quiz_id)` | Returns QuizOption.is_correct per question. |
| `get_quiz_config(quiz_id)` | Returns pass_score, max_attempts, time_limit_minutes. |

---



All state mutations go through services. Services emit domain events after successful commits.



Manages the course category hierarchy (admin-only).

| Method | Description |
|--------|-------------|
| `create_category(data, actor)` | Creates root or subcategory. Validates hierarchy. |
| `update_category(category_id, data, actor)` | Updates name, description, icon, order. |
| `deactivate_category(category_id, actor)` | Sets is_active=False. |

**Business Rules:**
- Max 2 hierarchy levels
- Slug is immutable after creation
- Deactivating parent deactivates children



Manages the full Course lifecycle.

| Method | Description |
|--------|-------------|
| `create_course(data, actor)` | Creates draft course. Auto-generates slug. |
| `update_course(course_id, data, actor)` | Updates metadata. Slug read-only after publish. |
| `publish_course(course_id, actor)` | Transitions draft → published. Emits CoursePublished. |
| `unpublish_course(course_id, actor)` | Transitions published → draft. |
| `archive_course(course_id, actor)` | Transitions to archived. |
| `delete_course(course_id, actor)` | Soft-delete. Sets deleted_at. |

**Business Rules:**
- Publish readiness: ≥1 published module with ≥1 published lesson
- Slug is immutable once published
- Cannot remove supports_offline if active offline enrollments exist
- Cannot delete course with any enrollment (archive instead)

**Events:** CourseCreated, CoursePublished, CourseArchived



Module lifecycle within a course.

| Method | Description |
|--------|-------------|
| `create_module(course_id, data, actor)` | Creates module at end of order. |
| `update_module(module_id, data, actor)` | Updates title, description, estimated_hours, is_published. |
| `reorder_modules(course_id, ordered_ids, actor)` | Accepts list of module UUIDs in order. |
| `delete_module(module_id, actor)` | Soft-delete. |

**Business Rules:**
- Cannot publish a module with zero published lessons
- Reorder list must contain exactly all non-deleted module IDs

**Events:** ModuleCreated, ModulePublished



Lesson lifecycle within a module.

| Method | Description |
|--------|-------------|
| `create_lesson(module_id, data, actor)` | Creates lesson at end of order. |
| `update_lesson(lesson_id, data, actor)` | Updates title, description, estimated_minutes, is_free_preview. |
| `publish_lesson(lesson_id, actor)` | Sets is_published=True. Lesson must have ≥1 component. |
| `unpublish_lesson(lesson_id, actor)` | Sets is_published=False. Warns if module empty. |
| `reorder_lessons(module_id, ordered_ids, actor)` | Standard reorder pattern. |
| `delete_lesson(lesson_id, actor)` | Soft-delete. Blocked if completed progress exists. |

**Business Rules:**
- Cannot publish an empty lesson (no content and no components)
- Soft-deleting does not delete UserProgress records

**Events:** LessonCreated, LessonPublished, LessonDeleted



Content items within a lesson.

| Method | Description |
|--------|-------------|
| `add_content(lesson_id, data, actor)` | Appends content item. Validates type-specific fields. |
| `update_content(content_id, data, actor)` | Updates fields. Type is immutable. |
| `reorder_content(lesson_id, ordered_ids, actor)` | Standard reorder pattern. |
| `delete_content(content_id, actor)` | Hard delete. Preserves UserProgress records. |

**Business Rules:**
- At least one of url or body must be present
- Content type is immutable after creation



1:1 homework definition per lesson.

| Method | Description |
|--------|-------------|
| `set_homework(lesson_id, data, actor)` | Creates or replaces homework. Upsert pattern. |
| `remove_homework(lesson_id, actor)` | Hard-deletes. Blocked if submissions exist. |

**Business Rules:**
- Only one homework per lesson
- Cannot remove homework with existing student submissions



Ordered practice exercises within a lesson.

| Method | Description |
|--------|-------------|
| `add_practice(lesson_id, data, actor)` | Appends practice item. Validates type. |
| `update_practice(practice_id, data, actor)` | Updates instructions, hints, max_score. |
| `reorder_practice(lesson_id, ordered_ids, actor)` | Standard reorder pattern. |
| `delete_practice(practice_id, actor)` | Hard delete. Blocked if attempts exist. |



Quiz definition: settings, questions, options.

| Method | Description |
|--------|-------------|
| `create_quiz(lesson_id, data, actor)` | Creates quiz for lesson. |
| `update_quiz_settings(quiz_id, data, actor)` | Updates pass_score, max_attempts, time_limit. |
| `add_question(quiz_id, data, actor)` | Appends question. Validates type and options. |
| `update_question(question_id, data, actor)` | Updates body, explanation, points. |
| `reorder_questions(quiz_id, ordered_ids, actor)` | Standard reorder pattern. |
| `add_option(question_id, data, actor)` | Adds answer option. Validates single_choice. |
| `delete_quiz(quiz_id, actor)` | Hard-deletes quiz. |

**Business Rules:**
- pass_score must be 0-100
- single_choice: exactly one correct option
- multiple_choice: ≥2 options with ≥1 correct
- Question type is immutable

**Events:** QuizCreated



Enrollment lifecycle - cross-domain write boundary.

| Method | Description |
|--------|-------------|
| `enroll_student(user_id, course_id, delivery_format, actor)` | Creates CourseEnrollment. Validates course and format. |
| `drop_enrollment(enrollment_id, actor)` | Sets status=dropped. Actor must be student or staff. |
| `complete_enrollment(enrollment_id, actor)` | Sets status=completed. Called by UserProgress domain. |
| `change_delivery_format(enrollment_id, new_format, actor)` | Changes online↔offline. Staff/admin only. |

**Business Rules:**
- Cannot enroll in draft or archived course
- Cannot enroll with offline format if course doesn't support it
- Duplicate enrollment rejected
- Only active enrollment can be completed or dropped

**Events:** StudentEnrolled, EnrollmentDropped, EnrollmentCompleted

---



All endpoints use JSON. Auth via Bearer token (JWT). Pagination uses `{ count, next, previous, results }`. Errors use `{ error, code, detail }`.

**URL namespace:** `/api/v1/learning/`





Query Params:
- `category_slug`: string (optional)
- `delivery_format`: online|offline (optional)
- `language`: string (optional)
- `search`: string (optional)
- `page`: int (default 1)
- `page_size`: int (default 20, max 100)

Response:
```json
{
  "count": 10,
  "next": "...",
  "previous": "...",
  "results": [{
    "id": "uuid",
    "title": "string",
    "slug": "string",
    "short_description": "string",
    "thumbnail_url": "string",
    "category": {"id": "uuid", "name": "string", "slug": "string"},
    "supports_online": true,
    "supports_offline": false,
    "estimated_weeks": 12,
    "language": "ru",
    "module_count": 5,
    "enrolled_count": 42
  }]
}
```



Staff see draft content. Students see published only. Unauthenticated: published only.



Returns active categories nested with children. Cacheable (TTL: 5 min).





Permissions: Staff, Admin

Request Body:
```json
{
  "title": "string",
  "description": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "category_id": "uuid",
  "supports_online": true,
  "supports_offline": false,
  "language": "string",
  "estimated_weeks": 12,
  "is_sequential": true
}
```



- slug: immutable once published
- supports_offline: cannot set to false if active offline enrollments exist



400 errors:
- `publish_not_ready`: Course has no published modules
- `publish_not_ready`: Module X has no published lessons



Permissions: Admin only







Requires ordered_ids to include all non-deleted modules.





Permissions: Enrolled student, Staff, Admin. Unauthenticated if `is_free_preview=true`.





Type validation:
- video/pdf/slides/link/recording: url required
- text/code: body required
- Other types: url optional



409: Quiz already exists on this lesson.





Permissions: Authenticated student (self-enroll), Admin (any user)

Request Body:
```json
{
  "course_id": "uuid",
  "delivery_format": "online|offline",
  "user_id": "uuid"
}
```

Errors:
- `Course does not support offline`
- `Course is not published`
- `Student already enrolled`



Query Params: `status` (optional: active|completed|dropped)



400: Enrollment already completed

---



| Action | Student | Mentor | Staff | Admin |
|--------|---------|--------|-------|-------|
| **Catalog** | | | | |
| List published courses | ✓ | ✓ | ✓ | ✓ |
| View published course detail | ✓ | ✓ | ✓ | ✓ |
| View free-preview lesson | ✓ | ✓ | ✓ | ✓ |
| View draft / unpublished course | — | — | OWN | ✓ |
| View unpublished lesson content | — | — | OWN | ✓ |
| **Enrollment** | | | | |
| Enroll self in course | ✓ | — | — | ✓ |
| Drop own enrollment | ✓ | — | — | ✓ |
| Force-drop student enrollment | — | — | — | ✓ |
| View all enrollments for course | — | own groups | ✓ | ✓ |
| **Course Authoring** | | | | |
| Create course | — | — | ✓ | ✓ |
| Edit course metadata | — | — | OWN | ✓ |
| Publish course | — | — | OWN | ✓ |
| Archive course | — | — | — | ✓ |
| Delete course (soft) | — | — | — | ✓ |
| **Module & Lesson Authoring** | | | | |
| Create / edit module | — | — | OWN | ✓ |
| Publish / unpublish module | — | — | OWN | ✓ |
| Reorder modules | — | — | OWN | ✓ |
| Create / edit lesson | — | — | OWN | ✓ |
| Publish / unpublish lesson | — | — | OWN | ✓ |
| Reorder lessons | — | — | OWN | ✓ |
| **Content & Quiz Authoring** | | | | |
| Add / edit / reorder content | — | — | OWN | ✓ |
| Delete content item | — | — | OWN | ✓ |
| Set / edit homework | — | — | OWN | ✓ |
| Add / edit / delete practice | — | — | OWN | ✓ |
| Create / edit quiz + questions | — | — | OWN | ✓ |
| **Admin** | | | | |
| Create / edit category | — | — | — | ✓ |
| View quiz answer key | — | — | OWN | ✓ |

**OWN** = `course.created_by == request.user`

---



All events dispatched after successful DB commits. In the monolith, Django signals serve as the event bus.





**Producer:** CourseEnrollmentService.enroll_student

**Payload:**
```json
{
  "enrollment_id": "uuid",
  "user_id": "uuid",
  "course_id": "uuid",
  "course_title": "string",
  "delivery_format": "string",
  "enrolled_at": "timestamp",
  "enrolled_by_id": "uuid|null"
}
```

**Consumers:**
- UserProgress — initialise progress record
- Notifications — send welcome email
- Analytics — update metrics
- Mentorship — trigger group assignment (offline)



**Producer:** CourseEnrollmentService.drop_enrollment

**Consumers:** UserProgress, Notifications, Mentorship, Analytics



**Producer:** CourseEnrollmentService.complete_enrollment

**Consumers:** Certification, Notifications, Analytics





**Producer:** CourseService.publish_course

**Consumers:** Search index, Notifications, Analytics



**Producer:** CourseService.archive_course

**Consumers:** Search index, Notifications





**Producer:** LessonService.publish_lesson

**Consumers:** UserProgress (unlock lessons), Notifications



**Producer:** LessonService.delete_lesson

**Consumers:** UserProgress, Submissions, Assessment (orphan checks)



**Producer:** LessonQuizService.create_quiz

**Consumers:** Assessment, UserProgress

---



Before designing UserProgress, these questions must be answered:



1. **What is the unit of progress?**
   - Lesson-level (LessonProgress) or content-item level?
   - Determines primary key structure

2. **What unlocks the next lesson?**
   - View all required content → auto-unlock
   - Submit homework → unlock after mentor approval
   - Pass lesson quiz → auto-unlock
   - Mentor manually unlocks

3. **What unlocks the next module?**
   - All lessons completed?
   - End-of-module assessment passed?
   - Both?

4. **Does online progress === offline progress?**
   - Online: student opens lesson → progress
   - Offline: mentor marks attendance → progress



1. **Can a student reset progress?**
   - Re-enroll: carry over or reset?

2. **Who triggers EnrollmentCompleted?**
   - UserProgress (when all modules pass)?
   - Assessment (when final exam passes)?



1. **Progress granularity for Analytics**
   - Store timestamps in UserProgress or Analytics own log?

2. **Handling deleted lessons**
   - Preserve progress records (stale flag) or delete?

---

*End of Application Layer Design Document*
