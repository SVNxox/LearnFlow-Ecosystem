

**Version:** v1.0  
**Status:** Archived - superseded by v2.0

---



The Learning Domain owns the complete course structure — from catalog to lesson content. It defines *what* students learn. It does not own *how far* they've gotten (UserProgress), *how well* they did (Assessment), or *who taught them* (Mentorship).



| Component | Description |
|-----------|-------------|
| Core Structure | Course, Module, Lesson, Enrollment |
| Content | LessonContent (video, pdf, slides, text, link, recording, code) |
| Practice | LessonHomework, LessonPractice |
| Quiz | LessonQuiz, QuizQuestion, QuizOption |
| Bridge | Enrollment (connects Identity → Learning) |

**10 tables total.** Every table has a single, well-defined responsibility.

---





```
Course → Module → Lesson → Content + Homework + Practice + Quiz
```


- UserProgress
- Analytics
- Assessment/Exams
- Certificates
- Mentorship groups
- Notifications
- Submissions review


- `Lesson.id` → UserProgress tracks completion
- `LessonHomework.id` → Submissions domain handles uploads
- `LessonQuiz.id` → Assessment domain records attempts

---



1. **Enrollment** — Student enrolls in Course → `Enrollment` row created. Delivery mode (online/offline) locked here.
2. **Lesson Study** — Student views LessonContent items in order.
3. **Lesson Practice + Quiz** — In-lesson check: exercises and knowledge check.
4. **Homework Submission** — Student submits work defined by LessonHomework.
5. **Module Assessment** — End-of-module exam. Pass → unlock next Module.

**Key principle:** The Learning Domain defines the *structure and content*. All *student interaction with that content* (progress, attempts, submissions, grades) lives in separate domains.

---





Top-level learning container. Defines delivery capability (supports_online/offline), sequencing rules, and publication status.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | gen_random_uuid() |
| title | VARCHAR(255) | NOT NULL | Display title |
| slug | VARCHAR(255) | UNIQUE | URL-safe identifier |
| description | TEXT | NULLABLE | Long-form description |
| short_description | VARCHAR(500) | NULLABLE | Catalog preview |
| thumbnail_url | TEXT | NULLABLE | S3/CDN URL |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'draft' | draft | published | archived |
| mode | VARCHAR(10) | NOT NULL, DEFAULT 'online' | online | offline | hybrid |
| language | VARCHAR(10) | NOT NULL, DEFAULT 'ru' | BCP-47 tag |
| estimated_weeks | SMALLINT | CHECK > 0 | Expected duration |
| is_sequential | BOOLEAN | NOT NULL, DEFAULT true | Module ordering requirement |
| created_by_id | UUID | FK to accounts_user | Application-enforced |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | Soft delete |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_course_slug ON courses_course (slug);
CREATE INDEX idx_course_status ON courses_course (status) WHERE deleted_at IS NULL;
CREATE INDEX idx_course_mode ON courses_course (mode, status) WHERE deleted_at IS NULL;
```



Ordered lesson grouping within a course.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| course_id | UUID | FK NOT NULL | → courses_course.id, CASCADE |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULLABLE | Module overview |
| order | SMALLINT | NOT NULL, CHECK > 0 | Position within course |
| is_published | BOOLEAN | NOT NULL, DEFAULT false | |
| estimated_hours | SMALLINT | CHECK > 0 | Informational only |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | Soft delete |

**Unique constraint:** `UNIQUE(course_id, order) WHERE deleted_at IS NULL`



Atomic learning container. May contain content, homework, practice, and quiz.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| module_id | UUID | FK NOT NULL | → courses_module.id, CASCADE |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULLABLE | Lesson overview |
| order | SMALLINT | NOT NULL, CHECK > 0 | Position within module |
| is_published | BOOLEAN | NOT NULL, DEFAULT false | |
| is_free_preview | BOOLEAN | NOT NULL, DEFAULT false | Marketing content |
| estimated_minutes | SMALLINT | CHECK > 0 | Expected completion time |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | Soft delete |



Domain bridge between Identity and Learning.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | NOT NULL | → accounts_user.id (no DB FK) |
| course_id | UUID | FK NOT NULL | → courses_course.id, RESTRICT |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | active | completed | dropped |
| delivery_mode | VARCHAR(10) | NOT NULL | online | offline |
| enrolled_at | TIMESTAMPTZ | NOT NULL | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| dropped_at | TIMESTAMPTZ | NULLABLE | |
| enrolled_by_id | UUID | NULLABLE | Audit field |

---





Unified table for all content types via discriminator.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| lesson_id | UUID | FK NOT NULL | → courses_lesson.id, CASCADE |
| type | VARCHAR(20) | NOT NULL | video | pdf | slides | text | link | recording | code |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULLABLE | Context below title |
| order | SMALLINT | NOT NULL, CHECK > 0 | Display order |
| url | TEXT | NULLABLE | For remote content |
| body | TEXT | NULLABLE | For inline text/code |
| duration_seconds | INTEGER | CHECK > 0 | For video/recording |
| file_size_bytes | BIGINT | CHECK > 0 | For downloadable files |
| metadata | JSONB | NOT NULL, DEFAULT '{}' | Type-specific extras |
| is_required | BOOLEAN | NOT NULL, DEFAULT true | Progress gate |
| is_downloadable | BOOLEAN | NOT NULL, DEFAULT false | |



1:1 per lesson - assignment definition.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| lesson_id | UUID | FK UNIQUE | → courses_lesson.id, CASCADE |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NOT NULL | Full task description |
| instructions | TEXT | NULLABLE | Step-by-step guide |
| max_score | SMALLINT | NOT NULL, DEFAULT 100 | |
| deadline_offset_days | SMALLINT | CHECK > 0 | Relative deadline |
| submission_type | VARCHAR(20) | NOT NULL, DEFAULT 'file' | file | link | text | mixed |
| allowed_file_types | TEXT[] | NOT NULL, DEFAULT '{}' | PostgreSQL array |
| max_file_size_mb | SMALLINT | NOT NULL, DEFAULT 20 | |



1:N per lesson - in-platform exercises.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| lesson_id | UUID | FK NOT NULL | → courses_lesson.id, CASCADE |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULLABLE | |
| order | SMALLINT | NOT NULL, CHECK > 0 | |
| type | VARCHAR(20) | NOT NULL, DEFAULT 'coding' | coding | written | interactive |
| instructions | TEXT | NOT NULL | |
| starter_code | TEXT | NULLABLE | |
| solution_code | TEXT | NULLABLE | |
| language | VARCHAR(30) | NULLABLE | |
| hints | JSONB | NOT NULL, DEFAULT '[]' | Progressive hints |
| max_score | SMALLINT | NOT NULL, DEFAULT 100 | |
| time_limit_minutes | SMALLINT | CHECK > 0 | |



0:1 per lesson - knowledge check.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| lesson_id | UUID | FK UNIQUE | → courses_lesson.id, CASCADE |
| title | VARCHAR(255) | NOT NULL | |
| instructions | TEXT | NULLABLE | |
| time_limit_minutes | SMALLINT | CHECK > 0 | |
| pass_score | SMALLINT | NOT NULL, DEFAULT 70, CHECK 0-100 | |
| max_attempts | SMALLINT | CHECK > 0 | |
| shuffle_questions | BOOLEAN | NOT NULL, DEFAULT false | |
| shuffle_options | BOOLEAN | NOT NULL, DEFAULT false | |
| show_correct_after_attempt | BOOLEAN | NOT NULL, DEFAULT true | |



| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| quiz_id | UUID | FK NOT NULL | → courses_lessonquiz.id, CASCADE |
| type | VARCHAR(20) | NOT NULL | single_choice | multiple_choice | true_false | short_text |
| body | TEXT | NOT NULL | Question text |
| explanation | TEXT | NULLABLE | Feedback after answering |
| order | SMALLINT | NOT NULL, CHECK > 0 | |
| points | SMALLINT | NOT NULL, DEFAULT 1 | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |



| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| question_id | UUID | FK NOT NULL | → courses_quizquestion.id, CASCADE |
| body | TEXT | NOT NULL | Option text |
| is_correct | BOOLEAN | NOT NULL | Multiple can be correct |
| order | SMALLINT | NOT NULL, CHECK > 0 | |
| created_at | TIMESTAMPTZ | NOT NULL | |

---



```
Course ─── N Module ─── N Lesson
   │                       │
   │                       ├── N LessonContent
   │                       ├── 0..1 LessonHomework
   │                       ├── N LessonPractice
   │                       └── 0..1 LessonQuiz
   │                                ├── N QuizQuestion
   │                                │        └── N QuizOption
   └── N Enrollment (RESTRICT delete)
```

Cross-domain references (no DB FK):
- `Course.created_by_id` → `accounts_user.id`
- `Enrollment.user_id` → `accounts_user.id`

---



| Decision | Reason |
|----------|--------|
| Single LessonContent table (no table-per-type) | Simpler queries, easier to add types |
| UNIQUE(parent_id, order) with gaps | Simple reordering with DB integrity |
| LessonHomework 1:1, LessonPractice 1:N | Different interaction patterns |
| Soft delete on Course/Module/Lesson only | Children hidden automatically |
| No DB FK from Enrollment to User | Cross-domain boundary, application enforcement |
| is_sequential on Course | Simple default, module-level overrides deferred |
| pass_score/max_attempts in LessonQuiz | Content config, not runtime state |
| deadline_offset_days (not absolute date) | Maintainable across course runs |

---



| Table | Index | Purpose |
|-------|-------|---------|
| courses_course | UNIQUE(slug) | URL routing |
| courses_course | partial(status) WHERE not deleted | Catalog listing |
| courses_module | UNIQUE(course_id, order) WHERE not deleted | Ordered listing |
| courses_lesson | UNIQUE(module_id, order) WHERE not deleted | Ordered listing |
| courses_enrollment | UNIQUE(user_id, course_id) | Prevent duplicates |
| courses_lessoncontent | UNIQUE(lesson_id, order) | Ordered content |
| courses_lessonhomework | UNIQUE(lesson_id) | One per lesson |
| courses_lessonquiz | UNIQUE(lesson_id) | One per lesson |

---



| Field | References | Direction | Integrity |
|-------|------------|-----------|-----------|
| Course.created_by_id | accounts_user.id | Learning → Identity | Read-only, no cascade |
| Enrollment.user_id | accounts_user.id | Learning → Identity | Service-layer validation |
| Enrollment.enrolled_by_id | accounts_user.id | Learning → Identity | Audit field |
| Lesson.id | UserProgress domain | UserProgress → Learning | Read-only |
| LessonHomework.id | Submissions domain | Submissions → Learning | Definition read-only |
| LessonQuiz.id | Assessment domain | Assessment → Learning | Definition read-only |

---



- Prerequisites (ModulePrerequisite junction)
- Lesson Versioning (snapshots)
- Localization (translation tables)
| Content Release Scheduling (publish_at)
| Learning Paths (ordered course sequences)
| Branching Lessons (adaptive routing)
| Co-authoring (CourseAuthor junction)
| Content Approval Workflow (review_status)

---

*Document version: v1.0. Superseded by [learnflow-learning-domain-v2.md](./learnflow-learning-domain-v2.md).*
