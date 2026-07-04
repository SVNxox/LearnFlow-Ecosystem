

**Created:** 2026-06-15  
**Status:** ✅ Completed



Integrated Progress API endpoints into frontend to show real-time progress tracking for courses, modules, and lessons.





- ✅ **`useCourseProgress(enrollmentId)`** — fetch course progress
- ✅ **`useModuleProgress(enrollmentId, moduleId)`** — fetch module progress
- ✅ **`useLessonProgress(enrollmentId, lessonId)`** — fetch lesson progress with refetch
- ✅ **`useRecordContentView()`** — record content views
- ✅ **`useDashboardStats(enrollmentId)`** — fetch dashboard statistics



**File:** `src/app/dashboard/student/page.tsx`

**Features:**
- Real-time stats:
  - Enrolled courses count
  - Completed modules count
  - Current streak (placeholder)
- Enrolled courses grid with real course data
- Progress bars on course cards
- Loading states with skeletons
- Error handling

**API Calls:**
```typescript
api.enrollment.getMyEnrollments()
api.learning.getCourse(courseId)
api.progress.getCourseProgress(enrollmentId)
```



**File:** `src/app/courses/[slug]/lessons/[lessonId]/page.tsx`

**Features:**
- Real-time lesson progress tracking
- Progress bar showing content completion percentage
- Auto-record content views when user watches video/opens PDF
- "Mark as Complete" button (enabled when 100% viewed)
- Completed badge on completed lessons
- Status tracking in sidebar navigation

**API Calls:**
```typescript
api.progress.getLessonProgress(enrollmentId, lessonId)
api.progress.recordContentView({ enrollment_id, content_id, duration_seconds })
```

**Progress Calculation:**
```typescript
const completionPercentage = 
  (viewed_required_count / required_content_count) * 100
```



| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/progress/course/{enrollmentId}/` | GET | Get course progress |
| `/api/v1/progress/module/{enrollmentId}/{moduleId}/` | GET | Get module progress |
| `/api/v1/progress/lesson/{enrollmentId}/{lessonId}/` | GET | Get lesson progress |
| `/api/v1/progress/content-view/` | POST | Record content view |
| `/api/v1/progress/dashboard/{enrollmentId}/` | GET | Get dashboard stats |



```
1. Student Dashboard
   └─> Shows enrolled courses with progress bars (0-100%)
   
2. Click course → Course Detail
   └─> Shows modules list
   
3. Click lesson → Lesson Viewer
   ├─> Progress bar at top (viewed X / Y content)
   ├─> Watch video → Auto-record view
   ├─> Progress updates in real-time
   └─> When 100% viewed → "Mark as Complete" enabled
   
4. Mark Complete → Navigate to next lesson
   
5. Complete all lessons → Course completed
   └─> Dashboard shows 100% progress
```



For full functionality, the backend must implement:

1. **Progress Initialization** (on `StudentEnrolled` event)
   - Create `CourseProgress`, `ModuleProgress`, `LessonProgress` records
   
2. **Content View Tracking**
   - Increment `viewed_required_count` when content is viewed
   - Update `last_activity_at` timestamp
   
3. **Lesson Completion** (TODO: endpoint needed)
   - `POST /api/v1/progress/lesson/{enrollmentId}/{lessonId}/complete/`
   - Mark lesson as completed
   - Trigger cascade completion (lesson → module → course)
   
4. **Dashboard Stats** (TODO: endpoint needed)
   - Return aggregated stats:
     - Total enrolled courses
     - Completed lessons count
     - Current streak calculation
     - Upcoming deadlines



- **Streak calculation** — currently shows "0 days" (needs backend implementation)
- **Mark as Complete** — shows alert (needs API endpoint)
- **Module progress in sidebar** — not yet showing locked/unlocked states
- **Assignment gate** — not yet integrated (homework_submitted check)



1. Backend: Implement `mark_lesson_complete` endpoint
2. Backend: Implement proper dashboard stats aggregation
3. Frontend: Add streak calculation display
4. Frontend: Show locked/unlocked state in module list
5. Frontend: Integrate assignment submission gate
6. Frontend: Add progress animations/transitions
7. Testing: E2E test for complete flow (enroll → watch → complete)



- [ ] Dashboard shows correct enrolled courses count
- [ ] Course card shows progress bar (0-100%)
- [ ] Lesson viewer tracks content views
- [ ] Progress bar updates when watching video
- [ ] "Mark as Complete" button appears at 100%
- [ ] Next lesson navigation works
- [ ] Progress persists across page reloads
- [ ] Loading states show correctly
- [ ] Error states handled gracefully
