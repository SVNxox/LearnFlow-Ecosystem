

**Version:** v2.0  
**Date:** 2026-06-07  
**Status:** Current

---



1. **Enrollment → CourseEnrollment** — explicit name anticipating future MentorGroupEnrollment, EventEnrollment
2. **Course.mode removed** — replaced with `supports_online` / `supports_offline` flags. Delivery format moved to `CourseEnrollment.delivery_format`. One course, no duplication.
3. **Cross-domain soft UUIDs replaced with real ForeignKey** — monolith, one DB, no reason to pay complexity cost early
4. **CourseCategory added** — hierarchical catalog taxonomy (2 levels). Single FK on Course

---



The Learning Domain owns the complete course structure — from catalog to lesson content. It defines *what* students learn. It does not own *how far* they've gotten (UserProgress), *how well* they did (Assessment), or *who taught them* (Mentorship).



| Component | Description |
|-----------|-------------|
| Core Structure | Course, Module, Lesson, CourseEnrollment |
| Content | LessonContent (video, pdf, slides, text, link, recording, code) |
| Practice | LessonHomework, LessonPractice |
| Quiz | LessonQuiz, QuizQuestion, QuizOption |
| Bridge | CourseEnrollment (User → Course, delivery_format) |
| Catalog | CourseCategory (parent/children, slug/order) |

**12 tables total.** Every table has a single, well-defined responsibility.

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



1. **CourseEnrollment** — Student enrolls in Course → `CourseEnrollment` row created. Delivery format locked here.
2. **Lesson Study** — Student views LessonContent items.
3. **Lesson Practice + Quiz** — In-lesson check.
4. **Homework Submission** — Student submits work.
5. **Module Assessment** — End-of-module exam.

---





Top-level learning container. Delivery mode is **not** stored on Course — it is a property of each `CourseEnrollment`.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | gen_random_uuid() |
| title | VARCHAR(255) | NOT NULL | Display title |
| slug | VARCHAR(255) | NOT NULL UNIQUE | URL-safe identifier |
| description | TEXT | NULLABLE | Long-form description |
| short_description | VARCHAR(500) | NULLABLE | Catalog cards |
| thumbnail_url | TEXT | NULLABLE | S3/CDN URL |
| category_id | UUID | FK NULLABLE | → courses_coursecategory.id, SET NULL |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'draft' | draft | published | archived |
| supports_online | BOOLEAN | NOT NULL, DEFAULT true | Self-paced delivery |
| supports_offline | BOOLEAN | NOT NULL, DEFAULT false | Mentor-led delivery |
| language | VARCHAR(10) | NOT NULL, DEFAULT 'ru' | BCP-47 tag |
| estimated_weeks | SMALLINT | CHECK > 0 | Expected duration |
| is_sequential | BOOLEAN | NOT NULL, DEFAULT true | Module ordering |
| created_by | ForeignKey | NOT NULL | → AUTH_USER_MODEL, SET NULL |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | Soft delete |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_course_slug ON courses_course (slug);
CREATE INDEX idx_course_status ON courses_course (status) WHERE deleted_at IS NULL;
CREATE INDEX idx_course_category ON courses_course (category_id) WHERE deleted_at IS NULL;

-- Constraint: must support at least one format
ALTER TABLE courses_course
    ADD CONSTRAINT chk_course_delivery CHECK (supports_online = TRUE OR supports_offline = TRUE);
```

**Why no mode on Course?** A course like "Python Backend" is one course — its content is identical for online and offline students. `supports_online`/`supports_offline` flags declare capability; `CourseEnrollment.delivery_format` records student's choice.



Ordered lesson grouping within a course.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| course_id | UUID | FK NOT NULL | → courses_course.id, CASCADE DELETE |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULLABLE | Module overview |
| order | SMALLINT | NOT NULL, CHECK > 0 | Position within course |
| is_published | BOOLEAN | NOT NULL, DEFAULT false | |
| estimated_hours | SMALLINT | CHECK > 0 | Informational |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | Soft delete |

**Unique constraint:** `UNIQUE(course_id, order) WHERE deleted_at IS NULL`



Atomic learning container. May contain content, homework, practice, and quiz.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| module_id | UUID | FK NOT NULL | → courses_module.id, CASCADE DELETE |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULLABLE | Lesson overview |
| order | SMALLINT | NOT NULL, CHECK > 0 | Position within module |
| is_published | BOOLEAN | NOT NULL, DEFAULT false | |
| is_free_preview | BOOLEAN | NOT NULL, DEFAULT false | Marketing |
| estimated_minutes | SMALLINT | CHECK > 0 | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | Soft delete |



User × Course membership. Named explicitly to distinguish from future MentorGroupEnrollment.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| user | ForeignKey | NOT NULL | → AUTH_USER_MODEL, PROTECT |
| course | ForeignKey | NOT NULL | → courses_course.id, RESTRICT DELETE |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | active | completed | dropped |
| delivery_format | VARCHAR(10) | NOT NULL | online | offline |
| enrolled_at | TIMESTAMPTZ | NOT NULL | Immutable |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| dropped_at | TIMESTAMPTZ | NULLABLE | |
| enrolled_by | ForeignKey | NULLABLE | → AUTH_USER_MODEL, SET NULL |

**Indexes:**
```sql
CREATE UNIQUE INDEX uq_courseenrollment_user_course ON courses_courseenrollment (user_id, course_id);
CREATE INDEX idx_courseenrollment_user_status ON courses_courseenrollment (user_id, status);
CREATE INDEX idx_courseenrollment_course_status ON courses_courseenrollment (course_id, status);
```

**Why real FK to User?** We are building a Django monolith with one PostgreSQL database. Real ForeignKey gives cascade semantics, ORM select_related, and DB-level integrity for free. When extracting to microservices, remove FKs in one migration.

---





Hierarchical catalog taxonomy — max 2 levels (root + subcategory).

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | gen_random_uuid() |
| name | VARCHAR(100) | NOT NULL | Display name |
| slug | VARCHAR(100) | NOT NULL UNIQUE | URL-safe |
| parent | ForeignKey | NULLABLE | Self-referential, SET NULL |
| description | VARCHAR(500) | NULLABLE | |
| icon | VARCHAR(50) | NULLABLE | Icon identifier |
| order | SMALLINT | NOT NULL, DEFAULT 0 | Display order |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_category_slug ON courses_coursecategory (slug);
CREATE INDEX idx_category_root ON courses_coursecategory (parent_id, order) WHERE is_active = TRUE;
CREATE INDEX idx_category_children ON courses_coursecategory (parent_id, order) WHERE parent_id IS NOT NULL AND is_active = TRUE;
```

**Max depth = 2.** Application-level validation: `if parent.parent_id is not None: raise ValidationError`

**Example hierarchy:**
```
Backend (root)
  ├── Django (sub)
  ├── FastAPI (sub)
Frontend (root)
  ├── React (sub)
```

---





Unified content model with discriminator.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| lesson_id | UUID | FK NOT NULL | → courses_lesson.id, CASCADE |
| type | VARCHAR(20) | NOT NULL | video | pdf | slides | text | link | recording | code |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULLABLE | |
| order | SMALLINT | NOT NULL, CHECK > 0 | Display order |
| url | TEXT | NULLABLE | For remote content |
| body | TEXT | NULLABLE | For inline text/code |
| duration_seconds | INTEGER | CHECK > 0 | |
| file_size_bytes | BIGINT | CHECK > 0 | |
| metadata | JSONB | NOT NULL, DEFAULT '{}' | Type-specific extras |
| is_required | BOOLEAN | NOT NULL, DEFAULT true | Progress gate |
| is_downloadable | BOOLEAN | NOT NULL, DEFAULT false | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

**metadata by type:**
- `video`: `{ provider, thumbnail_url, is_hls }`
- `pdf`: `{ page_count }`
- `slides`: `{ slide_count, embed_url }`
- `text`: `{}` (body is markdown)
- `link`: `{ open_in_new_tab, link_text }`
- `recording`: `{ recorded_at, session_title }`
- `code`: `{ language, is_runnable, theme }`

**Constraint:** `url IS NOT NULL OR body IS NOT NULL`



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
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |



| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| quiz_id | UUID | FK NOT NULL | → courses_lessonquiz.id, CASCADE |
| type | VARCHAR(20) | NOT NULL | single_choice | multiple_choice | true_false | short_text |
| body | TEXT | NOT NULL | Question text |
| explanation | TEXT | NULLABLE | Feedback |
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
accounts_user
  ├── FK created_by ──▶ Course (SET NULL)
  ├── FK user ────────▶ CourseEnrollment (PROTECT)
  └── FK enrolled_by ─▶ CourseEnrollment (SET NULL)

CourseCategory (self-referential, max 2 levels)
  └── 1 ───── N ──▶ Course (SET NULL)

Course ─── N Module ─── N Lesson
  │                       │
  │                       ├── N LessonContent
  │                       ├── 0..1 LessonHomework
  │                       ├── N LessonPractice
  │                       └── 0..1 LessonQuiz
  │                                ├── N QuizQuestion
  │                                │        └── N QuizOption
  └── N CourseEnrollment (RESTRICT)

Cross-domain (IDs referenced, no DB FK):
  - Lesson.id → UserProgress
  - LessonHomework.id → Submissions
  - LessonQuiz.id, LessonPractice.id → Assessment
  - CourseEnrollment.id → Analytics, Certificates
```

---



| Decision | Reason |
|----------|--------|
| Single LessonContent table | Simpler queries, easier to add types |
| UNIQUE(parent_id, order) with gaps | Simple reordering with DB integrity |
| LessonHomework 1:1, LessonPractice 1:N | Different interaction patterns |
| Soft delete on Course/Module/Lesson only | Children hidden automatically |
| Real DB FK while in monolith | One DB, FK gives cascade/ORM benefits for free |
| delivery_format on CourseEnrollment | One course supports both online/offline |
| CourseCategory as single FK | One course has one primary category |
| is_sequential on Course | Simple default |
| pass_score/max_attempts in LessonQuiz | Content config, not runtime state |
| deadline_offset_days (not absolute date) | Maintainable across course runs |

---



| Table | Index | Purpose |
|-------|-------|---------|
| courses_course | UNIQUE(slug) | URL routing |
| courses_course | partial(status) WHERE not deleted | Catalog listing |
| courses_course | (category_id) WHERE not deleted | Catalog by category |
| courses_coursecategory | UNIQUE(slug) | Category URLs |
| courses_coursecategory | (parent_id, order) WHERE active | Category listing |
| courses_module | UNIQUE(course_id, order) WHERE not deleted | Module ordering |
| courses_module | partial(course_id, order) WHERE published | Student module list |
| courses_lesson | UNIQUE(module_id, order) WHERE not deleted | Lesson ordering |
| courses_lesson | partial(module_id, order) WHERE published | Student lesson list |
| courses_courseenrollment | UNIQUE(user_id, course_id) | Prevent duplicates |
| courses_courseenrollment | (user_id, status) | Student dashboard |
| courses_courseenrollment | (course_id, status) | Course student list |
| courses_lessoncontent | UNIQUE(lesson_id, order) | Content ordering |
| courses_lessoncontent | (type, lesson_id) | Filter by type |
| courses_lessonhomework | UNIQUE(lesson_id) | One per lesson |
| courses_lessonquiz | UNIQUE(lesson_id) | One per lesson |

---



| Field | References | Direction | on_delete |
|-------|------------|-----------|-----------|
| Course.created_by | accounts_user.id | Learning → Identity | SET NULL |
| CourseEnrollment.user | accounts_user.id | Learning → Identity | PROTECT |
| CourseEnrollment.enrolled_by | accounts_user.id | Learning → Identity | SET NULL |
| Course.category | courses_coursecategory.id | Internal | SET NULL |

---



- Prerequisites (ModulePrerequisite junction)
- Lesson Versioning (snapshots)
- Localization (translation tables)
- Content Release Scheduling (publish_at)
- Learning Paths (ordered course sequences)
- Multi-Category Tagging (CourseCategoryAssignment junction)
- Branching Lessons (adaptive routing)
- Co-authoring (CourseAuthor junction)
- Content Approval Workflow (review_status)

---

*Version: v2.0 - Current design document*
