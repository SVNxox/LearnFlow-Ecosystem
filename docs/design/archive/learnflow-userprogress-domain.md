

**Domain:** UserProgress  
**Status:** Archived - superseded by v2 review

---



The UserProgress Domain owns the complete state of a student's journey through a course. It is a **consumer domain**: it owns no content definitions, no enrollments, no assessments. It only tracks state.



| Component | Description |
|-----------|-------------|
| Course Level | progress_courseprogress (1 row per enrollment) |
| Module Level | progress_moduleprogress (1 row per module per enrollment) |
| Lesson Level | progress_lessonprogress (1 row per lesson per enrollment) |
| View Tracking | progress_lessoncontentview (1 row per content item per enrollment) |



1. Progress unit = `LessonProgress` (not content-item level)
2. Lesson complete when: all required content viewed **AND** required homework submitted
3. Next lesson unlocks automatically on lesson completion
4. Next module unlocks when: all lessons complete **AND** module assessment passed
5. Online and offline share the same model — `completion_source` records the difference
6. UserProgress triggers `EnrollmentCompleted` after all modules pass



| Owns | Reads (cross-domain) | Consumes Events | Produces Events |
|------|---------------------|-----------------|-----------------|
| CourseProgress, ModuleProgress, LessonProgress, LessonContentView | Learning Domain tables at init (snapshots) | Learning, Submissions, Assessment, Mentorship | Notification, Analytics, Certification |



At enrollment time, UserProgress snapshots structural counts from the Learning Domain. After that, progress checks read only UserProgress tables.

---





One row per enrollment. The top-level progress aggregate.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| enrollment | ForeignKey | NOT NULL UNIQUE | → courses_courseenrollment.id, PROTECT |
| course_id | UUID | NOT NULL | Denormalized for fast lookup |
| user_id | UUID | NOT NULL | Denormalized for dashboard |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'not_started' | not_started | in_progress | completed |
| total_modules_count | SMALLINT | NOT NULL | Snapshot of published module count |
| completed_modules_count | SMALLINT | NOT NULL | Incremented when module completes |
| started_at | TIMESTAMPTZ | NULLABLE | First content view |
| completed_at | TIMESTAMPTZ | NULLABLE | All modules completed |
| last_activity_at | TIMESTAMPTZ | NULLABLE | Used for continue learning |
| created_at | TIMESTAMPTZ | NOT NULL | StudentEnrolled event processed |



One row per module per enrollment. Owns the assessment gate.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| enrollment | ForeignKey | NOT NULL | |
| module_id | UUID | FK NOT NULL | → courses_module.id, PROTECT |
| course_id | UUID | NOT NULL | Denormalized |
| status | VARCHAR(25) | NOT NULL | locked | unlocked | in_progress | assessment_pending | completed |
| total_lessons_count | SMALLINT | NOT NULL | Snapshot of published lesson count |
| completed_lessons_count | SMALLINT | NOT NULL | Source of truth for module completion |
| assessment_required | BOOLEAN | NOT NULL | Module has end-of-module exam |
| assessment_passed | BOOLEAN | NOT NULL | |
| assessment_passed_at | TIMESTAMPTZ | NULLABLE | |
| module_order | SMALLINT | NOT NULL | Snapshot of Module.order |
| unlocked_at | TIMESTAMPTZ | NULLABLE | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| last_activity_at | TIMESTAMPTZ | NULLABLE | |



The primary progress unit. One row per lesson per enrollment.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| enrollment | ForeignKey | NOT NULL | |
| lesson_id | UUID | FK NOT NULL | → courses_lesson.id, PROTECT |
| module_id | UUID | NOT NULL | Denormalized |
| course_id | UUID | NOT NULL | Denormalized |
| status | VARCHAR(20) | NOT NULL | locked | unlocked | in_progress | completed |
| completion_source | VARCHAR(30) | NULLABLE | student_activity | mentor_attendance | admin_override |
| lesson_order | SMALLINT | NOT NULL | Snapshot of Lesson.order |
| required_content_count | SMALLINT | NOT NULL | Snapshot of required content items |
| viewed_required_count | SMALLINT | NOT NULL | Incremented when content viewed |
| homework_required | BOOLEAN | NOT NULL | |
| homework_submitted | BOOLEAN | NOT NULL | |
| homework_submitted_at | TIMESTAMPTZ | NULLABLE | |
| unlocked_at | TIMESTAMPTZ | NULLABLE | |
| started_at | TIMESTAMPTZ | NULLABLE | First view |
| completed_at | TIMESTAMPTZ | NULLABLE | |



A lightweight tracking record - not a progress entity.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| enrollment | ForeignKey | NOT NULL | → courses_courseenrollment.id, CASCADE |
| content_id | UUID | NOT NULL | Soft reference (no FK) |
| lesson_progress | ForeignKey | NOT NULL | → progress_lessonprogress.id, CASCADE |
| is_required | BOOLEAN | NOT NULL | Snapshot at first view |
| first_viewed_at | TIMESTAMPTZ | NOT NULL | Immutable |
| last_viewed_at | TIMESTAMPTZ | NOT NULL | Updated on re-view |
| view_count | SMALLINT | NOT NULL | |
| last_position_seconds | INT | NULLABLE | Video resume |

---





**LessonProgress:**
- locked → unlocked (prev completed OR first in module)
- unlocked → in_progress (first content view)
- in_progress → completed (content gate AND homework gate pass)

**ModuleProgress:**
- locked → unlocked (prev completed OR first module)
- unlocked → in_progress (any lesson starts)
- in_progress → assessment_pending (all lessons done + assessment_required)
- assessment_pending → completed (assessment_passed)

**CourseProgress:**
- not_started → in_progress (first lesson view)
- in_progress → completed (all modules completed)



| Gate | Online | Offline |
|------|--------|---------|
| Content Gate | viewed_required_count >= required_content_count | Bypassed via mentor_attendance |
| Homework Gate | homework_submitted == TRUE | Bypassed via mentor_attendance |
| Assessment Gate | assessment_passed == TRUE | N/A |



**Algorithm 1 - record_content_view:**
1. UPSERT LessonContentView
2. Update progress counters
3. Call _check_lesson_completion

**Algorithm 2 - _check_lesson_completion:**
- Check content gate AND homework gate
- Set status = completed
- Emit LessonCompleted
- Unlock next lesson
- Check module completion

**Algorithm 3 - _check_module_completion:**
- Increment completed_lessons_count
- If all lessons done:
  - If assessment_required and not assessment_passed → assessment_pending
  - Else → completed
- Unlock next module
- Check course completion

**Algorithm 4 - _check_course_completion:**
- Increment completed_modules_count
- If all modules complete:
  - Set status = completed
  - Emit CourseCompleted
  - Call CourseEnrollmentService.complete_enrollment



Called by ProgressInitialisationService when StudentEnrolled event received.

1. Create CourseProgress (get_or_create)
2. For each module: create ModuleProgress
3. For each lesson: create LessonProgress

Snapshot counts from Learning Domain at init time:
- total_lessons_count
- required_content_count
- homework_required

---





| Method | Description |
|--------|-------------|
| get_dashboard(user_id) | Returns active CourseProgress rows for user |
| get_course_progress(enrollment_id) | Full progress tree |
| get_next_lesson(enrollment_id) | Drives "Continue" button |
| get_completion_percentage(enrollment_id) | 0-100 integer |



| Method | Description |
|--------|-------------|
| get_lesson_progress(enrollment_id, lesson_id) | Single lesson state |
| get_module_lessons_progress(enrollment_id, module_id) | All lessons in module |
| get_viewed_content_ids(enrollment_id, lesson_id) | Set of viewed content IDs |
| get_video_position(enrollment_id, content_id) | Resume position |
| is_lesson_accessible(enrollment_id, lesson_id) | Fast boolean check |



| Method | Description |
|--------|-------------|
| get_course_completion_stats(course_id) | Course-level metrics |
| get_lesson_funnel(course_id) | Per-lesson funnel |
| get_student_progress_snapshot(enrollment_id) | Single student timeline |

---





| Method | Description |
|--------|-------------|
| initialise_progress(enrollment_id) | Full initialisation |
| handle_lesson_published(enrollment_id, lesson_id) | Add progress row |
| handle_lesson_deleted(lesson_id) | Mark as stale |
| handle_content_deleted(lesson_id, content_id, was_required) | Update counters |
| handle_assessment_added(module_id) | Set assessment_required |



| Method | Description |
|--------|-------------|
| record_content_view(enrollment_id, content_id, position_seconds) | Core hot-path |
| handle_homework_submitted(enrollment_id, lesson_id) | Homework gate |
| handle_attendance_marked(enrollment_id, lesson_id, session_id) | Offline completion |
| override_lesson_complete(enrollment_id, lesson_id, actor) | Admin override |



| Method | Description |
|--------|-------------|
| handle_assessment_passed(enrollment_id, module_id) | Assessment gate |
| handle_module_completed(enrollment_id, module_id) | Internal cascade |



| Method | Description |
|--------|-------------|
| handle_course_completed(enrollment_id) | Call Learning Domain |
| handle_enrollment_dropped(enrollment_id) | Mark as inactive |

---




- StudentEnrolled → initialise_progress
- EnrollmentDropped → handle_enrollment_dropped
- LessonPublished → handle_lesson_published
- LessonDeleted → handle_lesson_deleted


- HomeworkSubmitted → handle_homework_submitted


- ModuleAssessmentPassed → handle_assessment_passed


- AttendanceMarked → handle_attendance_marked

---



- LessonStarted
- LessonCompleted
- LessonUnlocked
- ModuleAssessmentUnlocked
- ModuleCompleted
- CourseCompleted

---



All endpoints require authentication. Students access own data only.



Student dashboard with course list and next lesson.



Full progress tree for course.



Lesson progress state (pre-load before lesson view).



Core progress write - student views content.



Admin/Staff override - requires reason.



All student progress for a course.

---



| Decision | Reason |
|----------|--------|
| Synchronous cascade, not event-driven | Avoid race conditions, guarantee order |
| Snapshot counters, not live cross-domain queries | Zero cross-domain queries in hot path |
| completion_source = single differentiator for online/offline | Same model handles both formats |
| Stale flag instead of delete on lesson removal | Preserve analytics history |
| Assessment gate at module level | Keep lesson-level completion simple |
| EnrollmentCompleted called post-commit | Ensure UserProgress fully committed first |

---



Analytics builds read models from UserProgress events.

| Metric | Source | How computed |
|--------|--------|--------------|
| Lesson completion rate | LessonCompleted events | count / enrolled |
| Avg time to complete lesson | LessonStarted + LessonCompleted | avg(completed_at - started_at) |
| Lesson dropout rate | LessonStarted without LessonCompleted | Students in in_progress > N days |
| Module completion funnel | ModuleCompleted | How many reach each module |
| Online vs offline completion | LessonCompleted.completion_source | Group by source |
| Video re-watch rate | LessonContentView.view_count | From UserProgress selector |

---

*Document version: v1.0 - Archived*
*Superseded by: [learnflow-userprogress-review-v2.md](./learnflow-userprogress-review-v2.md)*
