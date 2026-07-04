

**Date:** 2026-06-15  
**Status:** Analysis Complete  
**Reviewer:** Claude (Sonnet 4)

---



После полного анализа документации, бэкенд API, фронтенд кода и компонентов выявлено **18 критичных несоответствий** между фронтендом и бэкендом, которые блокируют MVP.

**Основные проблемы:**
1. ❌ API endpoints в `src/lib/api.ts` не соответствуют реальным бэкенд URL
2. ❌ Assessment UI создан, но не протестирован с реальным API
3. ❌ Missing endpoint: `POST /progress/lesson/complete/` (не реализован в бэкенде)
4. ❌ Enrollment flow не завершён (нет integration с Payment)
5. ❌ TypeScript types не соответствуют реальным API responses

---





**Frontend (`src/lib/api.ts`):**
```typescript
startAttempt: async (assessmentId: string): Promise<AssessmentAttempt> => {
  const response = await apiClient.post<AssessmentAttempt>('/assessment/attempts/start/', {
    assessment_id: assessmentId,
  });
  return response.data;
}
```

**Backend Reality (`src/backend/assessment/presentation/rest/v1/urls.py`):**
```python
path('attempts/', StartAttemptView.as_view(), name='start-attempt'),


```

**Problem:**
- ❌ Frontend не передаёт `enrollment_id` (обязательное поле)
- ❌ Endpoint URL неверный: `/assessment/attempts/start/` → должен быть `/assessment/attempts/`

**Fix Required:**
```typescript
startAttempt: async (enrollmentId: string, assessmentId: string): Promise<AssessmentAttempt> => {
  const response = await apiClient.post<AssessmentAttempt>('/assessment/attempts/', {
    enrollment_id: enrollmentId,
    assessment_id: assessmentId,
  });
  return response.data;
}
```

---



**Frontend:**
```typescript
submitResponse: async (data: {
  attempt_id: string;
  item_id: string;
  selected_option_ids?: string[];
  text_response?: string;
  submitted_code?: string;
}): Promise<void> => {
  await apiClient.post('/assessment/attempts/submit-response/', data);
}
```

**Backend:**
```python
path('attempts/<uuid:attempt_id>/responses/', SubmitResponseView.as_view(), name='submit-response'),

```

**Problem:**
- ❌ URL structure неверный
- ❌ Frontend передаёт `attempt_id` в body, бэкенд ждёт в URL path

**Fix Required:**
```typescript
submitResponse: async (attemptId: string, data: {
  item_id: string;
  selected_option_ids?: string[];
  text_response?: string;
  submitted_code?: string;
}): Promise<void> => {
  await apiClient.post(`/assessment/attempts/${attemptId}/responses/`, data);
}
```

---



**Frontend:**
```typescript
finalizeAttempt: async (attemptId: string): Promise<AssessmentAttempt> => {
  const response = await apiClient.post<AssessmentAttempt>(
    `/assessment/attempts/${attemptId}/finalize/`
  );
  return response.data;
}
```

**Backend:**
```python
path('attempts/<uuid:attempt_id>/finalize/', FinalizeAttemptView.as_view(), name='finalize-attempt'),

```

**Status:** ✅ Correct (один из немногих!)

---



**Frontend (`src/app/courses/[slug]/lessons/[lessonId]/page.tsx:109`):**
```typescript
const handleMarkComplete = async () => {
  // TODO: API endpoint to mark lesson as completed
  // await api.progress.markLessonComplete(enrollment.id, lesson.id);
  alert('Mark complete functionality will be implemented with Progress API integration.');
}
```

**Backend Reality:**
```
❌ NO SUCH ENDPOINT EXISTS
```

**Expected API (from docs/API.md):**
```
POST /api/v1/progress/enrollments/{id}/lessons/{id}/complete/  
```

**Problem:**
- Backend только поддерживает **admin override**, не student self-completion
- Student completion должен происходить автоматически через `recordContentView`
- Frontend пытается создать manual completion, которого не существует

**Fix Required:**
1. Backend: Добавить `POST /api/v1/progress/lessons/{lesson_id}/complete/` для студентов
2. Frontend: Убрать кнопку "Mark Complete" — делать auto-complete через content views

---





**Frontend expects (`src/app/assessments/[id]/attempt/[attemptId]/page.tsx`):**
```typescript
interface AssessmentAttempt {
  items: Array<{
    item_id: string;
    type: string;
    title: string;
    description: string;
    max_points: number;
    options?: Array<{
      id: string;
      text: string;
      order: number;
    }>;
  }>;
}
```

**Backend returns (`src/backend/assessment/presentation/rest/v1/attempts/detail.py`):**
```python
'items': [
  {
    'item_id': str(item.item_id),
    'item_type': item.item_type,
    'item_title': item.item_title,
    'order': item.order,
    'max_points': float(item.max_points),
    'selected_option_ids': [...],  
    
    
  }
]
```

**Problem:**
- Frontend нужен список `options` для рендеринга quiz interface
- Backend не возвращает `options` в attempt detail
- Нужен отдельный endpoint для получения items с options

**Fix Required:**
Backend должен возвращать:
```python
'items': [
  {
    'item_id': '...',
    'item_type': 'single_choice',
    'item_title': 'What is Python?',
    'description': 'Choose the correct answer',
    'max_points': 10.00,
    'options': [  
      {'id': 'uuid', 'text': 'Programming language', 'order': 1},
      {'id': 'uuid', 'text': 'Snake', 'order': 2},
    ],
    'selected_option_ids': ['uuid'],  
  }
]
```

---



**Frontend needs (`src/app/assessments/[id]/page.tsx:48`):**
```typescript
const attemptsData = await api.assessment.getStudentAttempts(assessmentId);
```

**Backend provides:**
```python
path('assessments/<uuid:assessment_id>/attempts/', StudentAttemptsListView.as_view(), name='student-attempts'),

```

**Problem:**
- Endpoint существует, но фронтенд передаёт только `assessment_id`
- Бэкенд проверяет `user_id` из request.user
- Но как получить `assessment_id` для модуля? Frontend не знает assessment_id до загрузки

**Flow Problem:**
1. Student на странице модуля
2. Хочет начать assessment
3. Но не знает `assessment_id` (только `module_id`)
4. Нужен endpoint: `GET /api/v1/assessment/modules/{module_id}/` → returns assessment

**Fix Required:**
```python

path('modules/<uuid:module_id>/', GetModuleAssessmentView.as_view(), name='module-assessment'),


```

---





**Frontend (`src/types/api.ts`):**
```typescript
export interface Assessment {
  id: string;
  module_id: string;
  title: string;
  instructions: string | null;
  passing_percentage: number;
  max_attempts: number | null;
  time_limit_minutes: number | null;
  shuffle_items: boolean;
  is_published: boolean;
  created_at: string;
}
```

**Backend (`src/backend/assessment/domain/models/assessment.py`):**
```python
class ModuleAssessment(models.Model):
    id = UUIDField
    module_id = UUIDField
    title = CharField(max_length=255)
    instructions = TextField(blank=True)  
    passing_percentage = DecimalField
    max_attempts = SmallIntegerField(null=True)
    time_limit_minutes = SmallIntegerField(null=True)
    shuffle_items = BooleanField(default=False)
    is_published = BooleanField(default=False)
    created_by_id = UUIDField  
    created_at = DateTimeField
    updated_at = DateTimeField  
```

**Fix Required:**
```typescript
export interface Assessment {
  id: string;
  module_id: string;
  title: string;
  instructions: string;  // NOT null — empty string
  passing_percentage: number;
  max_attempts: number | null;
  time_limit_minutes: number | null;
  shuffle_items: boolean;
  is_published: boolean;
  created_by_id: string;  // ADD
  created_at: string;
  updated_at: string;  // ADD
}
```

---



**Frontend:**
```typescript
export interface AssessmentAttempt {
  id: string;
  enrollment_id: string;
  assessment_id: string;
  user_id: string;
  attempt_number: number;
  grading_status: 'pending' | 'auto_graded' | 'mentor_review' | 'finalized';
  started_at: string;
  submitted_at: string | null;
  graded_at: string | null;
  expires_at: string | null;
  max_score: number;
  final_score: number | null;
  percentage: number | null;
  passed: boolean | null;
}
```

**Backend Response (`detail.py`):**
```python
{
  'attempt_id': str(result.attempt_id),  
  'assessment_id': str(result.assessment_id),
  'assessment_title': result.assessment_title,  
  'attempt_number': result.attempt_number,
  'grading_status': result.grading_status,
  'started_at': result.started_at.isoformat(),
  'submitted_at': ...,
  'graded_at': ...,  
  'expires_at': ...,
  'is_expired': result.is_expired,  
  'max_score': float(result.max_score),
  'final_score': float(result.final_score) if result.final_score else None,
  'percentage': float(result.percentage) if result.percentage else None,
  'passed': result.passed,
  'passing_percentage': float(result.passing_percentage),  
  'total_items': result.total_items,  
  'graded_items': result.graded_items,  
  'mentor_note': result.mentor_note,  
}
```

**Fix Required:**
```typescript
export interface AssessmentAttemptDetail {
  attempt_id: string;  // NOT 'id'
  assessment_id: string;
  assessment_title: string;  // ADD
  attempt_number: number;
  grading_status: 'pending' | 'auto_graded' | 'mentor_review' | 'finalized';
  started_at: string;
  submitted_at: string | null;
  graded_at: string | null;  // ADD
  expires_at: string | null;
  is_expired: boolean;  // ADD
  max_score: number;
  final_score: number | null;
  percentage: number | null;
  passed: boolean | null;
  passing_percentage: number;  // ADD
  total_items: number;  // ADD
  graded_items: number;  // ADD
  mentor_note: string | null;  // ADD
  items: AssessmentItemResponse[];  // ADD
}

export interface AssessmentItemResponse {
  item_id: string;
  item_type: 'single_choice' | 'multiple_choice' | 'text_answer' | 'coding' | 'project' | 'interview';
  item_title: string;
  item_description?: string;
  order: number;
  max_points: number;
  options?: Array<{ id: string; text: string; order: number }>;  // For choice types
  selected_option_ids: string[];
  text_response: string | null;
  submitted_code: string | null;
  is_graded: boolean;
  auto_points: number | null;
  mentor_points: number | null;
  final_points: number | null;
  is_correct: boolean | null;
  review_comment: string | null;
}
```

---





**Current Flow:**
1. Student browse courses → `/courses`
2. Click course → `/courses/[slug]`
3. Click "Enroll" → calls `enrollmentApi.enroll()`
4. Navigate to dashboard

**Problem:**
- No `enrollment_id` stored in component state
- When starting assessment, frontend doesn't know which `enrollment_id` to use
- Need to fetch enrollments every time

**Fix Required:**
```typescript
// After enrollment, redirect with enrollment_id
router.push(`/courses/${slug}?enrollment=${enrollmentId}`);

// Or store in localStorage/context
setCurrentEnrollment(enrollmentData);
```

---



**From CLAUDE.md:**
```
Payment ──emits──► PaymentSucceeded (Outbox) ──► Enrollment (activate)
```

**Current Frontend:**
- Directly calls `enrollmentApi.enroll()` without payment
- No payment flow implemented
- Free courses work, but paid courses should block

**Fix Required:**
1. Add `Course.price` field to types
2. If price > 0, redirect to payment page
3. After payment success, auto-enroll via backend event handler

---





**Current Implementation (`useRecordContentView`):**
```typescript
const recordView = async (enrollmentId: string, contentId: string, durationSeconds?: number) => {
  await api.progress.recordContentView({
    enrollment_id: enrollmentId,
    content_id: contentId,
    duration_seconds: durationSeconds,
  });
};
```

**Backend Endpoint:**
```python
POST /api/v1/progress/content-view/
Body: { "enrollment_id": "uuid", "content_id": "uuid", "duration_seconds": 120 }
```

**Problem:**
- ❌ Endpoint URL mismatch
- ❌ Frontend не отслеживает `duration_seconds` для video/recording content
- ❌ No retry logic if request fails

**Fix Required:**
1. Add video player time tracking
2. Implement retry with exponential backoff
3. Queue failed requests in localStorage

---



**Frontend (`useDashboardStats`):**
```typescript
const data = await api.progress.getDashboard(enrollmentId);
setStats({
  enrolledCourses: data.enrolled_courses || 0,
  completedLessons: data.completed_lessons || 0,
  currentStreak: data.current_streak || 0,
});
```

**Problem:**
- ❌ Dashboard endpoint ожидает один `enrollment_id`
- ❌ Но stats должны быть по всем enrollments пользователя
- ❌ Неверная логика — нужен user-level endpoint, не enrollment-level

**Expected API:**
```python
GET /api/v1/progress/me/dashboard/
Returns:
{
  "enrolled_courses": 3,
  "completed_courses": 1,
  "completed_lessons": 45,
  "current_streak": 7,
  "enrollments": [
    { "enrollment_id": "...", "course_title": "...", "percentage": 75 }
  ]
}
```

---





**Created:** `src/components/features/assessments/QuestionCard.tsx`

**Issues:**
1. ❌ No keyboard navigation (arrow keys)
2. ❌ No accessibility attributes (aria-labels)
3. ❌ Countdown timer не отображается (только в странице)
4. ❌ No support for `explanation` field (shown after grading)

---



**Created:** `src/components/features/assessments/ResultsDisplay.tsx`

**Issues:**
1. ❌ Не показывает `mentor_note` (общий комментарий ментора)
2. ❌ Не показывает разницу между `auto_points` и `mentor_points` (mentor override)
3. ❌ No visual indicator for mentor-reviewed items

---



**File:** `src/components/features/lessons/LessonContentViewer.tsx`

**Issues:**
1. ❌ Video content не отслеживает `position_seconds`
2. ❌ PDF viewer не отслеживает scroll position
3. ❌ No "Mark as viewed" button for non-auto-trackable content

---





**Status:** ❌ NOT STARTED

**Required Pages:**
1. `/assignments/[id]` — assignment detail
2. `/assignments/[id]/submit` — submission form
3. `/submissions/[id]` — submission detail + revisions
4. `/submissions/[id]/revisions/[revisionId]` — revision detail

**Components Needed:**
1. `AssignmentCard` — show assignment info
2. `SubmissionForm` — file upload + text + GitHub link
3. `RevisionHistory` — timeline of revisions
4. `ReviewFeedback` — mentor feedback display

---



**Status:** ❌ NOT STARTED

**Required Pages:**
1. `/dashboard/mentor` — work queue overview
2. `/dashboard/mentor/assessments` — pending assessment reviews
3. `/dashboard/mentor/submissions` — pending submission reviews
4. `/dashboard/mentor/students` — my students list

**Components Needed:**
1. `WorkQueue` — list of pending reviews
2. `AssessmentReviewInterface` — grade responses, add comments
3. `SubmissionReviewInterface` — grade submission, request changes

---



**Status:** ❌ NOT STARTED

**Required Pages:**
1. `/certificates` — my certificates list
2. `/certificates/[id]` — certificate detail + download
3. `/certificates/verify/[code]` — public verification (no auth)

**Components Needed:**
1. `CertificateCard` — show certificate preview
2. `CertificateViewer` — display certificate with download button
3. `VerificationResult` — public verification result

---



**Status:** ❌ NOT STARTED

**Required Pages:**
1. `/profile` — view/edit profile
2. `/profile/settings` — notification settings

---





**Current State:**
- ❌ No E2E tests
- ❌ No API integration tests
- ❌ No component tests
- ❌ Only manual testing

**Required:**
1. Playwright/Cypress E2E tests for critical flows
2. MSW (Mock Service Worker) for API mocking
3. React Testing Library for component tests

---



**Problem:**
- No seed script for test data
- Manual creation via Django Admin
- Inconsistent test environments

**Fix Required:**
```bash

python manage.py seed_test_data
```

---





**Current State:**
- Every page load fetches fresh data
- No React Query / SWR
- No stale-while-revalidate

**Fix Required:**
```typescript
import { useQuery } from '@tanstack/react-query';

const { data: course } = useQuery({
  queryKey: ['course', slug],
  queryFn: () => api.learning.getCourse(slug),
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

---



**Problem:**
- All components load eagerly
- Large bundle size
- Slow initial load

**Fix Required:**
```typescript
const AssessmentPage = dynamic(() => import('./AssessmentPage'), {
  loading: () => <LoadingScreen />,
});
```

---





**Current Implementation:**
```typescript
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refreshToken);
```

**Problem:**
- XSS vulnerability (localStorage accessible via JavaScript)
- Better: httpOnly cookies

**Recommendation:**
- Keep current approach for MVP
- Document as known issue
- Migrate to httpOnly cookies in Phase 2

---



**Problem:**
- API has rate limiting, but frontend doesn't handle 429 responses
- No retry with exponential backoff
- No user feedback on rate limit

**Fix Required:**
```typescript
if (error.response?.status === 429) {
  const retryAfter = error.response.headers['retry-after'];
  toast.error(`Too many requests. Retry in ${retryAfter}s`);
}
```

---





**Problem:**
- Quiz interface not keyboard-accessible
- No focus management
- No aria-labels

**Fix Required:**
```typescript
<button
  aria-label={`Option ${index + 1}: ${option.text}`}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleSelect(option.id);
    }
  }}
>
```

---



**Problem:**
- No ARIA landmarks
- No live regions for dynamic content
- No skip links

---





**Problem:**
- Long questions overflow on mobile
- Options too small to tap
- Timer overlaps content

**Fix Required:**
```css
@media (max-width: 640px) {
  .question-card {
    padding: 1rem;
  }
  .option {
    min-height: 48px; /* Touch target size */
  }
}
```

---





**Current State:**
- Errors crash app
- No fallback UI
- No error reporting

**Fix Required:**
```typescript
<ErrorBoundary fallback={<ErrorFallback />}>
  <App />
</ErrorBoundary>
```

---



**Problem:**
- Some errors show alert()
- Some show inline text
- Some don't show at all

**Fix Required:**
- Implement toast notification system
- Standardize error display

---





**Problem:**
- No Storybook
- No usage examples
- No prop documentation

**Fix Required:**
- Add JSDoc comments
- Create Storybook stories

---



**Problem:**
- Developers don't know which API functions exist
- No examples of usage

---





**Current `.env.example`:**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Problem:**
- No validation
- App fails silently if missing

**Fix Required:**
```typescript
const requiredEnvVars = ['NEXT_PUBLIC_API_URL'];
requiredEnvVars.forEach((key) => {
  if (!process.env[key]) {
    throw new Error(`Missing env var: ${key}`);
  }
});
```

---



**Problem:**
- No bundle size analysis
- No tree shaking verification
- No compression

---





1. ✅ **Fix Assessment API endpoints** (2-3 hours)
   - Update `src/lib/api.ts` to match real backend URLs
   - Add missing parameters (`enrollment_id`)
   - Fix response type mappings

2. ✅ **Add missing Assessment endpoint** (1 hour)
   - `GET /api/v1/assessment/modules/{module_id}/` → returns assessment info

3. ✅ **Fix TypeScript types** (1-2 hours)
   - Update `src/types/api.ts` to match backend responses
   - Add missing fields
   - Create separate types for list vs detail

4. ❌ **Implement Submissions UI** (6-8 hours)
   - 4 pages, 4 components
   - File upload, revision history, review feedback

5. ❌ **Implement Mentor Dashboard** (4-6 hours)
   - Work queue, review interfaces

6. ❌ **Fix Progress tracking** (2 hours)
   - User-level dashboard endpoint
   - Remove "Mark Complete" button
   - Auto-complete via content views

7. ❌ **Add enrollment context** (1 hour)
   - Store current enrollment in state/context
   - Pass to assessment pages



8. ❌ **Certificates UI** (3-4 hours)
9. ❌ **Add React Query** (2 hours)
10. ❌ **Implement toast notifications** (1 hour)
11. ❌ **Add error boundaries** (1 hour)
12. ❌ **Fix mobile responsiveness** (2-3 hours)



13. ❌ **Add E2E tests** (4-6 hours)
14. ❌ **Improve accessibility** (3-4 hours)
15. ❌ **Add Storybook** (2-3 hours)
16. ❌ **Optimize performance** (2-3 hours)

---



**MVP Completion:**
- P0 fixes: **18-24 hours**
- P1 fixes: **9-12 hours**
- **Total: 27-36 hours (3.5-4.5 days)**

**Current MVP Status:**
- Backend: 100% ✅
- Frontend: 60% 🟡 (was 70%, downgraded after analysis)
- Overall MVP: 70% → 65%

---





1. **Fix Assessment API client** (highest ROI)
   - Update `src/lib/api.ts`
   - Fix all endpoint URLs
   - Add missing parameters
   - Test with real backend

2. **Create integration test script**
   - Seed test data via Django management command
   - Test full flow: register → enroll → lesson → assessment → submission

3. **Implement Submissions UI**
   - Blocks mentor workflow
   - Blocks assessment completion (project type)



1. **Add React Query**
   - Better caching
   - Automatic refetching
   - Loading/error states

2. **Implement global state management**
   - Store current enrollment
   - Store user profile
   - Avoid prop drilling

3. **Add toast notification system**
   - Replace alert()
   - Consistent UX



1. **Test against real backend regularly**
   - Don't assume API contracts
   - Verify responses match types

2. **Create E2E test for critical flows**
   - Student enrollment → course completion
   - Assessment attempt → grading → pass

3. **Document API changes**
   - Update `docs/API.md` when backend changes
   - Keep frontend types in sync

---



Frontend имеет **solid foundation** (компоненты, структура, типы), но **critical integration gaps** блокируют MVP:

1. API client не совпадает с реальным backend
2. Assessment UI создан, но не протестирован
3. Submissions UI полностью отсутствует
4. Mentor Dashboard отсутствует

**Next Priority:** Fix P0 issues в следующем порядке:
1. Assessment API fixes (3 hours)
2. Submissions UI (8 hours)
3. Mentor Dashboard (6 hours)
4. Integration testing (3 hours)

После этого MVP будет **feature-complete** и готов к тестированию.
