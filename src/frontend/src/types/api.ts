// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  error: string;
  code: string;
  details?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Auth Types
export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_blocked: boolean;
  last_login_at: string | null;
  created_at: string;
  info: {
    first_name: string;
    last_name: string;
    avatar_url: string | null;
    phone: string | null;
    bio: string | null;
    date_of_birth: string | null;
    telegram_id: number | null;
    updated_at: string;
  } | null;
  settings: {
    language: string;
    timezone: string;
    notify_email: boolean;
    notify_telegram: boolean;
    notify_web: boolean;
    updated_at: string;
  } | null;
  // Роли: ['student'], ['mentor'], ['admin'], ['staff']
  roles: string[];
}

// Хелпер — получить первичную роль пользователя
export type UserRole = 'student' | 'mentor' | 'staff' | 'admin';

export function getPrimaryRole(user: User): UserRole {
  if (user.roles.includes('admin')) return 'admin';
  if (user.roles.includes('staff')) return 'staff';
  if (user.roles.includes('mentor')) return 'mentor';
  return 'student';
}

export interface LoginRequest {
  email: string;
  password: string;
}

// Бэкенд возвращает access_token / refresh_token (не access / refresh)
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

// Бэкенд при регистрации возвращает только { detail: string }
export interface RegisterResponse {
  detail: string;
}

// Course Types
export interface Course {
  id: string;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  thumbnail_url: string | null;
  category: CourseCategory | null;
  status: 'draft' | 'published' | 'archived';
  supports_online: boolean;
  supports_offline: boolean;
  language: string;
  estimated_weeks: number | null;
  is_sequential: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CourseDetail extends Course {
  modules?: ModuleWithLessons[];
  category?: CourseCategory;
}

import type { ModuleWithLessons } from './learning';

export interface CourseCategory {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  parent: string | null;
}

export interface Module {
  id: string;
  course_id: string;
  title: string;
  description: string | null;
  order: number;
  is_published: boolean;
  estimated_hours: number | null;
  created_at: string;
}

export interface Lesson {
  id: string;
  module_id: string;
  title: string;
  description: string | null;
  order: number;
  is_published: boolean;
  is_free_preview: boolean;
  estimated_minutes: number | null;
  created_at: string;
}

export interface LessonContent {
  id: string;
  lesson_id: string;
  type: 'video' | 'pdf' | 'slides' | 'text' | 'link' | 'recording' | 'code';
  title: string;
  description: string | null;
  url: string | null;
  body: string | null;
  order: number;
  duration_seconds: number | null;
  file_size_bytes: number | null;
  is_required: boolean;
  is_downloadable: boolean;
  metadata: Record<string, unknown>;
}

// Enrollment Types
export interface CourseEnrollment {
  id: string;
  user_id: string;
  course_id: string;
  status: 'pending' | 'active' | 'suspended' | 'dropped' | 'completed';
  delivery_format: 'online' | 'offline' | 'hybrid';
  enrolled_at: string;
  completed_at: string | null;
  dropped_at: string | null;
}

// Progress Types
export interface CourseProgress {
  enrollment_id: string;
  course_id: string;
  user_id: string;
  delivery_format: 'online' | 'offline';
  status: 'not_started' | 'in_progress' | 'completed';
  total_modules_count: number;
  completed_modules_count: number;
  cached_percentage: number;
  started_at: string | null;
  completed_at: string | null;
  last_activity_at: string | null;
}

export interface ModuleProgress {
  enrollment_id: string;
  module_id: string;
  course_id: string;
  module_order: number;
  status: 'locked' | 'unlocked' | 'in_progress' | 'assessment_pending' | 'completed';
  total_lessons_count: number;
  completed_lessons_count: number;
  assessment_required: boolean;
  assessment_passed: boolean;
  unlocked_at: string | null;
  completed_at: string | null;
}

export interface LessonProgress {
  enrollment_id: string;
  lesson_id: string;
  module_id: string;
  course_id: string;
  lesson_order: number;
  module_order: number;
  status: 'locked' | 'unlocked' | 'in_progress' | 'completed';
  completion_source: 'student_activity' | 'mentor_attendance' | 'admin_override' | null;
  required_content_count: number;
  viewed_required_count: number;
  homework_required: boolean;
  homework_submitted: boolean;
  unlocked_at: string | null;
  started_at: string | null;
  completed_at: string | null;
}

// Assessment Types
export interface Assessment {
  id: string;
  module_id: string;
  title: string;
  instructions: string; // Backend returns empty string, not null
  passing_percentage: number;
  max_attempts: number | null;
  time_limit_minutes: number | null;
  shuffle_items: boolean;
  is_published: boolean;
  created_by_id: string;
  created_at: string;
  updated_at: string;
}

// List view (simplified)
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

// Detail view (with items)
export interface AssessmentAttemptDetail {
  attempt_id: string;
  assessment_id: string;
  assessment_title: string;
  attempt_number: number;
  grading_status: 'pending' | 'auto_graded' | 'mentor_review' | 'finalized';
  started_at: string;
  submitted_at: string | null;
  graded_at: string | null;
  expires_at: string | null;
  is_expired: boolean;
  max_score: number;
  final_score: number | null;
  percentage: number | null;
  passed: boolean | null;
  passing_percentage: number;
  total_items: number;
  graded_items: number;
  mentor_note: string | null;
  items: AssessmentItemResponse[];
}

export interface AssessmentItemResponse {
  item_id: string;
  item_type: 'single_choice' | 'multiple_choice' | 'text_answer' | 'coding' | 'project' | 'interview';
  item_title: string;
  order: number;
  max_points: number;
  options?: Array<{ id: string; text: string; order: number }>; // Only for choice types
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

// Submission Types
export interface Assignment {
  id: string;
  lesson_id: string | null;
  assessment_item_id: string | null;
  type: 'theory' | 'coding' | 'project';
  title: string;
  description: string;
  max_score: number;
  deadline_offset_days: number | null;
  submission_types_allowed: string[];
  allowed_file_extensions?: string | null;
  max_file_size_mb?: number;
  auto_check_enabled?: boolean;
  created_at: string;
}

export interface Submission {
  id: string;
  assignment_id: string;
  enrollment_id: string;
  student_id: string;
  status: 'draft' | 'submitted' | 'under_review' | 'changes_requested' | 'approved' | 'rejected';
  current_revision_number: number;
  final_score: number | null;
  created_at: string;
  first_submitted_at: string | null;
  last_submitted_at: string | null;
  reviewed_at: string | null;
  deadline: string | null;
}

// Certificate Types
export interface Certificate {
  id: string;
  user_id: string;
  enrollment_id: string;
  course_id: string;
  user_email: string;
  certificate_number: string;
  verification_code: string;
  student_full_name_snapshot: string;
  course_name_snapshot: string;
  final_score: number | null;
  completion_date: string;
  issued_at: string;
  pdf_url: string | null;
  pdf_generated_at: string | null;
  status: 'pending' | 'issued' | 'revoked';
}

export interface CertificateVerificationResult {
  valid: boolean;
  status?: 'issued' | 'pending' | 'revoked';
  student_name?: string;
  course_title?: string;
  completion_date?: string;
  issued_at?: string;
  final_score: number | null;
  certificate_number?: string;
  detail?: string;
}

// ─── Progress ─────────────────────────────────────────────────────────────────
export interface ProgressDashboardCourse {
  enrollment_id: string;
  course_id: string;
  course_title: string;
  status: 'not_started' | 'in_progress' | 'completed';
  completion_percentage: number;
  completed_lessons: number;
  total_lessons: number;
  enrolled_at: string | null;
  completed_at: string | null;
  last_activity_at: string | null;
}

export interface ProgressDashboard {
  courses: ProgressDashboardCourse[];
}

export interface LessonProgressDetail {
  lesson_id: string;
  lesson_order: number;
  status: 'locked' | 'unlocked' | 'in_progress' | 'completed';
  viewed_required_count: number;
  required_content_count: number;
  has_homework: boolean;
  homework_submitted: boolean;
  completed_at: string | null;
}

export interface ModuleProgressDetail {
  module_id: string;
  module_order: number;
  status: 'locked' | 'unlocked' | 'in_progress' | 'assessment_pending' | 'completed';
  completed_lessons: number;
  total_lessons: number;
  assessment_required: boolean;
  assessment_passed: boolean;
  lessons: LessonProgressDetail[];
}

export interface CourseProgressDetail {
  enrollment_id: string;
  course_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  completion_percentage: number;
  completed_lessons: number;
  total_lessons: number;
  started_at: string | null;
  completed_at: string | null;
  modules: ModuleProgressDetail[];
}

export interface NextAction {
  action_type: 'study_lesson' | 'take_assessment' | 'course_completed' | 'blocked';
  message: string;
  lesson_id?: string;
  module_id?: string;
  assessment_id?: string;
}

export interface RecordViewResult {
  status: 'recorded';
  lesson_completed: boolean;
  viewed_required_count: number;
  required_content_count: number;
}

// ─── Assessment (extended) ────────────────────────────────────────────────────
export interface AssessmentOption {
  id: string;
  text: string;
  order: number;
}

export interface AssessmentItemDetail {
  item_id: string;
  item_type: 'single_choice' | 'multiple_choice' | 'text_answer' | 'coding' | 'project' | 'interview';
  item_title: string;
  order: number;
  max_points: number;
  options: AssessmentOption[] | null;
  starter_code?: string;
  coding_language?: string;
  min_word_count?: number | null;
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

export interface AttemptDetail {
  attempt_id: string;
  assessment_id: string;
  assessment_title: string;
  attempt_number: number;
  grading_status: 'pending' | 'auto_graded' | 'mentor_review' | 'finalized';
  started_at: string;
  submitted_at: string | null;
  graded_at: string | null;
  expires_at: string | null;
  is_expired: boolean;
  max_score: number;
  final_score: number | null;
  percentage: number | null;
  passed: boolean | null;
  passing_percentage: number;
  items: AssessmentItemDetail[];
  total_items: number;
  graded_items: number;
  mentor_note: string;
}

// Mentor pending assessment review
export interface PendingAssessmentReview {
  response_id: string;
  attempt_id: string;
  assessment_id: string;
  assessment_title: string;
  user_id: string;
  item_type: string;
  item_title: string;
  max_points: number;
  text_response: string | null;
  submitted_code: string | null;
  coding_language: string;
  submitted_at: string | null;
}

// ─── Submissions (extended) ───────────────────────────────────────────────────
export interface SubmissionRevision {
  id: string;
  revision_number: number;
  submission_type: 'github_repository' | 'file_upload' | 'text_answer' | 'external_link';
  payload: Record<string, unknown>;
  notes: string;
  submitted_at: string;
}

export interface SubmissionDetail extends Submission {
  assignment: Assignment;
  revisions: SubmissionRevision[];
  reviews: SubmissionReview[];
}

export interface SubmissionReview {
  id: string;
  submission_id: string;
  revision_id: string;
  mentor_id: string;
  score: number;
  max_score: number;
  feedback: string;
  status: 'changes_requested' | 'approved' | 'rejected';
  reviewed_at: string;
}

// Mentor pending submission review
export interface PendingSubmissionReview {
  submission_id: string;
  revision_id: string;
  assignment_title: string;
  student_id: string;
  student_name: string;
  submission_type: string;
  payload: Record<string, unknown>;
  submitted_at: string;
  revision_number: number;
  max_score: number;
}

// ─── Presigned URLs ──────────────────────────────────────────────────────────
export interface PresignedUploadUrl {
  upload_url: string;
  s3_key: string;
  file_id: string;
  expires_at: string;
}

export interface PresignedDownloadUrl {
  download_url: string;
  filename: string;
}

// ─── User Management (admin) ──────────────────────────────────────────────────
export interface AdminUser {
  id: string;
  email: string;
  is_active: boolean;
  is_blocked: boolean;
  blocked_reason: string | null;
  last_login_at: string | null;
  created_at: string;
  info: {
    first_name: string;
    last_name: string;
    avatar_url: string | null;
    phone: string | null;
    bio: string | null;
  } | null;
  roles: string[];
  enrollment_count: number;
}

export interface AdminUserListResponse {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: AdminUser[];
}

export interface CreateUserBody {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: 'student' | 'mentor' | 'staff' | 'admin';
}

// ─── Course Editor ────────────────────────────────────────────────────────────
export interface CreateCourseBody {
  title: string;
  slug?: string; // ✅ ДОБАВЛЕНО
  description?: string;
  short_description?: string;
  thumbnail_url?: string;
  category_id?: string | null;
  status?: 'draft' | 'published' | 'archived'; // ✅ ДОБАВЛЕНО
  supports_online: boolean;
  supports_offline: boolean;
  language: string;
  estimated_weeks?: number;
  is_sequential: boolean;
  price?: string;      // ✅ ДОБАВЛЕНО
  currency?: string;
}

export interface CourseCategory {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  order: number;
  is_active: boolean;
  parent: string | null;
  parent_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateModuleBody {
  course_id: string;
  title: string;
  description?: string;
  estimated_hours?: number;
}

export interface CreateLessonBody {
  module_id: string;
  title: string;
  description?: string;
  estimated_minutes?: number;
  is_free_preview: boolean;
}

export interface AddContentBody {
  type: 'video' | 'pdf' | 'slides' | 'text' | 'link' | 'recording' | 'code';
  title: string;
  description?: string;
  url?: string;
  body?: string;
  duration_seconds?: number;
  is_required?: boolean;
  is_downloadable?: boolean;
}

// ─── Quiz Builder ─────────────────────────────────────────────────────────────
export interface QuizSettings {
  pass_score: number; // 0-100
  max_attempts: number | null;
  time_limit_minutes: number | null;
  shuffle_questions: boolean;
  shuffle_options: boolean;
  show_correct_after_attempt: boolean;
}

export interface QuizOption {
  id: string;
  body: string;
  is_correct: boolean;
}

export interface QuizQuestion {
  id: string;
  type: 'single_choice' | 'multiple_choice' | 'true_false' | 'short_text';
  body: string;
  explanation: string | null;
  points: number;
  order: number;
  options: QuizOption[];
}

export interface CreateQuestionBody {
  type: 'single_choice' | 'multiple_choice' | 'true_false' | 'short_text';
  body: string;
  explanation?: string;
  points: number;
}

export interface CreateOptionBody {
  body: string;
  is_correct: boolean;
}

// ─── Payments ─────────────────────────────────────────────────────────────────
export interface Payment {
  id: string;
  user_id: string;
  enrollment_id: string;
  amount: string; // decimal string e.g. "150000.00"
  currency: string; // 'UZS' | 'USD'
  status: string;
  payment_method: string; // 'click' | 'payme' | 'card' | 'cash'
  idempotency_key: string | null;
  created_at: string;
  completed_at: string | null;
  metadata: Record<string, unknown>;
}

export interface PaymentDetail {
  id: string;
  user_id: string;
  user_email: string;
  user_name: string;
  enrollment_id: string;
  course_title: string;
  amount: string;
  currency: string;
  status: string;
  payment_method: string;
  provider: string;
  provider_payment_id: string;
  idempotency_key: string;
  created_at: string;
  succeeded_at: string | null;
  failed_at: string | null;
  refunded_at: string | null;
  metadata: Record<string, unknown>;
}

export interface Refund {
  id: string;
  payment_id: string;
  amount: string;
  reason: string;
  status: 'pending' | 'completed' | 'failed';
  created_by_id: string;
  created_at: string;
  completed_at: string | null;
}

export interface CreateRefundBody {
  amount: string;
  reason: string;
}

// ─── Certificates (admin) ─────────────────────────────────────────────────────
export interface CertificateTemplate {
  id: string;
  name: string;
  is_active: boolean;
  description?: string;
  background_image?: string;
  is_default: boolean;
  created_at: string;
  preview_url: string | null;
}

export interface GenerateCertificateBody {
  enrollment_id: string;
  template_id?: string;
  completion_date: string; // 'YYYY-MM-DD'
}

export interface RevokeCertificateBody {
  reason: string;
}

// ─── Admin Enrollment ─────────────────────────────────────────────────────────
export interface AdminEnrollment extends CourseEnrollment {
  user_email: string;
  user_name: string;
  course_title: string;
  course_slug: string;
}

export interface AdminEnrollmentListResponse {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: AdminEnrollment[];
}

// ─── Analytics ────────────────────────────────────────────────────────────────
export interface PlatformStats {
  total_users: number;
  total_students: number;
  total_mentors: number;
  total_courses: number;
  published_courses: number;
  total_enrollments: number;
  active_enrollments: number;
  completed_enrollments: number;
  total_revenue: string;
  pending_reviews: number;
}
// ─── Profile / Settings / Sessions ────────────────────────────────────────────
export interface UserSession {
  id: string;
  device_name: string | null;
  ip_address: string | null;
  created_at: string;
  expires_at: string;
}

export interface UserSettings {
  language: string;
  timezone: string;
  notify_email: boolean;
  notify_telegram: boolean;
  notify_web: boolean;
  notify_deadlines: boolean;
  notify_grades: boolean;
  notify_mentor_comments: boolean;
  updated_at: string;
}