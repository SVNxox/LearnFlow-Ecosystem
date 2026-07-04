

**Review Type:** Staff Engineer Review  
**Date:** 2026-06-07  
**Status:** Design approved for v2.0 with fixes

---



The v1 architecture is structurally sound — the four-table hierarchy, snapshot strategy, and synchronous cascade are the right foundations. However, there are **20 issues** ranging from correctness bugs that will surface on day one to scalability problems that only appear under load.



| Severity | Count | Description |
|----------|-------|-------------|
| 🔴 Critical | 4 | Data corruption or permanent stuck states |
| 🟠 High | 7 | Breaks at scale or for offline students |
| 🟡 Medium | 6 | Edge cases that produce wrong behavior |
| 🟢 Low | 3 | Improvements worth making before ship |



Three blocking issues:
1. **F2 (race condition)** — Lost counter increments cause permanent stuck state
2. **F8 (ordering bug)** — Cross-module lesson ordering sends students to wrong lesson
3. **F18 (bulk attendance race condition)** — Concurrent module completion calls without row locking

---



| ID | Finding | Area | Severity |
|----|---------|------|----------|
| F1 | O(n) DB fan-out when content deleted | Counters | Critical |
| F2 | Race condition on viewed_required_count | Counters | Critical |
| F3 | Counter drift on completed lessons | Counters | High |
| F4 | No handler for LessonContentAdded | Counters | High |
| F5 | CHECK viewed ≤ required + 1 masks bugs | Counters | Low |
| F6 | Module-granularity percentage misleading | Percentage | High |
| F7 | assessment_pending shows 0% credit | Percentage | Medium |
| F8 | Cross-module lesson_order missing module_order | Continue | Critical |
| F9 | in_progress vs unlocked priority inverted | Continue | High |
| F10 | assessment_pending returns null with no signal | Continue | High |
| F11 | Non-sequential continue returns first-by-order | Continue | Medium |
| F12 | Attendance bypasses homework gate | Offline | High |
| F13 | No AttendanceRevoked path | Offline | Medium |
| F14 | Delivery format change mid-course | Offline | Medium |
| F15 | One API call marks video "viewed" | Content | Medium |
| F16 | is_required flag change not handled | Content | Medium |
| F17 | _unlock_next_module never unlocks first lesson | Content | Critical |
| F18 | Bulk offline attendance race condition | Additional | Critical |
| F19 | Re-enroll progress reset | Additional | Low |
| F20 | Admin override no audit trail | Additional | Low |

---





**Finding:** The `handle_content_deleted` handler updates every `LessonProgress` row for every enrolled student inline. For a course with 10,000 enrollments, this triggers 10,000 reads, updates, and completion checks in one synchronous transaction.

**Impact:** Will hit 30-second DB timeout at a few hundred enrollments.

**Recommendation:** Fan-out operations must be background tasks, not inline event handlers. Enqueue a task; process rows in batches of 500.



**Finding:** The `record_content_view` algorithm uses read-modify-write pattern. Two concurrent requests will both read the same value and both write the same incremented value, losing one increment.

**Result:** `viewed=2, required=3` — content gate never passes. Student is permanently stuck.

**Recommendation:** Use `F('viewed_required_count') + 1` expression (atomic SQL UPDATE). The UNIQUE constraint prevents duplicate rows but does not protect the counter.



**Finding:** When a staff member adds new required content to a lesson where some students have `status=completed`, the counter on those completed rows becomes inconsistent (`viewed < required`).

**Recommendation:** Fan-out handlers must filter out rows where `status = 'completed'`. Completed lessons are frozen.



**Finding:** Learning Domain's `LessonContentService.add_content()` does not emit an event that UserProgress listens to. New required content never increments snapshots.

**Recommendation:** Learning Domain must emit `LessonContentAdded(lesson_id, content_id, is_required)`. UserProgress must handle it.



**Finding:** `CHECK(viewed_required_count <= required_content_count + 1)` was documented as "tolerance for concurrent updates."

**Recommendation:** Remove the `+1` tolerance. With atomic `F()` increments, this constraint will never be violated in normal operation.

---





**Finding:** Formula `completion_percentage = completed_modules_count / total_modules_count` gives equal weight to every module regardless of lesson count.

**Example:** Course with modules [20 lessons, 1 lesson, 1 lesson]. Student finishes M2+M3 → 67%, but has done 2/22 actual lessons.

**Recommendation:** Use lesson-based percentage. Query: `SELECT SUM(completed_lessons_count), SUM(total_lessons_count) FROM progress_moduleprogress WHERE enrollment_id = X AND NOT is_stale`.



**Finding:** A module in `assessment_pending` has `completed_lessons_count == total_lessons_count` but `status != 'completed'`. With module-level percentage, the entire module contributes 0.

**Recommendation:** The lesson-based percentage from F6 naturally resolves this.

---





**Finding:** `get_next_lesson` returns the lesson with `status=unlocked` and lowest `lesson_order`. But `lesson_order` is scoped per module — every module starts at 1.

**Example:** Module 1 lessons: order=1,2,3. Module 2 lessons: order=1,2,3. Comparing raw lesson_order is meaningless.

**Recommendation:** Query must order by `module_order ASC, lesson_order ASC`. Requires `module_order` stored on `LessonProgress`.



**Finding:** v1 returns first `unlocked` lesson, falls back to first `in_progress` if none. This is backwards.

**Recommendation:** Return most recent `in_progress` first (ordered by `started_at DESC`), then first `unlocked`.



**Finding:** When module is in `assessment_pending`, there are no `unlocked` lessons. API returns `next_lesson: null`. Student sees a dead button.

**Recommendation:** Add `next_action` field: `{ type: "take_module_assessment", module_id, module_title, assessment_url }`.



**Finding:** For non-sequential courses, all lessons start as `unlocked`. Current implementation returns Lesson 1 of Module 1 every time.

**Recommendation:** Non-sequential courses should return most recently active lesson (`LessonProgress.started_at DESC`).

---





**Finding:** v1 design states attendance bypasses both content and homework gates. But homework is pedagogically different from watching a video.

**Recommendation:** Attendance should bypass **content gate only**. The homework gate should apply regardless of delivery format.

```python

def handle_attendance_marked(...):
    
    lp.viewed_required_count = lp.required_content_count
    lp.completion_source = 'mentor_attendance'
    
    _check_lesson_completion(enrollment_id, lesson_id)
```



**Finding:** Lesson completion is terminal. But offline attendance can be marked in error.

**Recommendation:** Option A (simple): Add admin-only `POST /progress/enrollments/{id}/lessons/{id}/reset/` endpoint. Requires dual-staff approval.



**Finding:** Admin can change `CourseEnrollment.delivery_format` from offline to online mid-course. But completed lessons remain completed under offline model.

**Recommendation:** Emit `EnrollmentDeliveryFormatChanged` event. Update `delivery_format` snapshot on `CourseProgress`.

---





**Finding:** `POST /progress/lessons/{id}/content/{id}/view/` records a view. For video, opening and immediately closing a 4-hour lecture "completes" the content gate.

**Recommendation:** Add `minimum_watch_ratio` field to `LessonContent` (default 0.0). Content gate check:
```python
watch_ratio = view_record.last_position_seconds / view_record.total_duration_seconds
return watch_ratio >= content.minimum_watch_ratio
```



**Finding:** Learning Domain allows updating `is_required` on existing content.

**Case A (FALSE → TRUE):** Student viewed content before it became required. Counter was not incremented.

**Case B (TRUE → FALSE):** Counter includes this item, now inflated.

**Recommendation:** Learning Domain should emit `LessonContentRequirementChanged`. UserProgress handles it.



**Finding:** `_unlock_next_module` sets `ModuleProgress.status = 'unlocked'` but does NOT unlock the first `LessonProgress` row in that next module.

**Result:** Module unlocked, but all lessons still `status=locked`. Student is stuck.

**Recommendation:** `_unlock_next_module` must also unlock the first lesson of the next module.

---





**Finding:** When mentor marks attendance for 5 lessons concurrently, each calls `_check_module_completion`. They each read the same `completed_lessons_count` before any write lands.

**Result:** Final `completed_lessons_count = 1` (instead of 5). Module never completes.

**Recommendation:**
1. `_check_module_completion` must acquire row-level lock using `SELECT ... FOR UPDATE`
2. Process lesson completions for a single enrollment serially



**Finding:** When student drops and re-enrolls, a new `CourseEnrollment` is created. All progress starts fresh.

**Recommendation:** Make this explicit product decision. If "preserve progress" is desired, add `previous_enrollment_id` FK.



**Finding:** API requires `reason` string but `LessonProgress` has no `override_reason` or `override_by_id` fields.

**Recommendation:** Add two nullable fields to `LessonProgress`:
- `override_by_id UUID NULLABLE`
- `override_reason TEXT NULLABLE`

---



| Table | Change | Reason |
|-------|--------|--------|
| progress_courseprogress | ADD `delivery_format VARCHAR(10)` | F14 - avoid cross-domain read |
| progress_courseprogress | ADD `is_sequential BOOLEAN DEFAULT TRUE` | F11 - non-sequential logic |
| progress_courseprogress | ADD `cached_percentage SMALLINT DEFAULT 0` | F6 - fast dashboard read |
| progress_moduleprogress | ADD `is_stale BOOLEAN DEFAULT FALSE` | Handle lesson deletion |
| progress_lessonprogress | ADD `is_stale BOOLEAN DEFAULT FALSE` | Handle lesson deletion |
| progress_lessonprogress | ADD `is_active BOOLEAN DEFAULT TRUE` | Referenced in services |
| progress_lessonprogress | ADD `override_by_id UUID NULLABLE` | F20 - audit trail |
| progress_lessonprogress | ADD `override_reason TEXT NULLABLE` | F20 - audit trail |
| progress_lessoncontentview | ADD `total_duration_seconds INT NULLABLE` | F15 - video watch threshold |
| courses_lessoncontent (Learning Domain) | ADD `minimum_watch_ratio DECIMAL(3,2) DEFAULT 0.0` | F15 |
| courses_courseenrollment (Learning Domain) | ADD `previous_enrollment_id UUID NULLABLE FK` | F19 |

**New Index Required (F8 fix):**
```sql
CREATE INDEX idx_lp_enr_module_lesson 
ON progress_lessonprogress (enrollment_id, module_order, lesson_order)
WHERE status IN ('unlocked','in_progress') 
  AND is_stale = FALSE 
  AND is_active = TRUE;
```

---



| Algorithm | Change | Fixes |
|-----------|--------|-------|
| `record_content_view` | Use `get_or_create` + `F('viewed_required_count') + 1` + `refresh_from_db()` | F2 |
| `_check_lesson_completion` | Add `select_for_update()` | F18 |
| `_check_module_completion` | Add `select_for_update()` + `F('completed_lessons_count') + 1` | F2, F18 |
| `_check_course_completion` | Add `select_for_update()` + `F('completed_modules_count') + 1` | F2, F18 |
| `_unlock_next_module` | Also unlock first lesson of next module | F17 |
| `get_next_lesson` → `get_next_action` | Rename, change priority, add assessment_pending detection | F8, F9, F10, F11 |
| fan-out handlers | Convert to background tasks with batch processing (500/batch) | F1 |
| `handle_content_deleted`, `handle_content_added` | Add `WHERE status != 'completed'` filter | F3 |
| `handle_attendance_marked` | Bypass content gate only, call `_check_lesson_completion` | F12 |
| `initialise_progress` | Snapshot `delivery_format` and `is_sequential` | F11, F14 |



| New Event | Producer | Handler | Fixes |
|-----------|----------|---------|-------|
| `LessonContentAdded` | Learning Domain | ProgressInitialisationService | F4 |
| `LessonContentRequirementChanged` | Learning Domain | ProgressInitialisationService | F16 |
| `EnrollmentDeliveryFormatChanged` | Learning Domain | CourseProgressService | F14 |
| `AttendanceRevoked` | Mentorship Domain (future) | LessonProgressService | F13 |

---



With the 4 critical findings resolved (F2, F8, F17, F18) and the 7 high-severity findings addressed, the architecture is production-ready.

**Total new events from Learning Domain:** 2 (`LessonContentAdded`, `LessonContentRequirementChanged`)  
**Total schema additions:** 8 columns across 4 tables  
**No existing columns removed or renamed**

---

*End of Architecture Review v2*
