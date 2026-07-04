// ─── Learning domain types ─────────────────────────────────────────────────
// These mirror the exact shapes returned by the Learning domain REST API
// (see learning/presentation/rest/v1/courses/{list,detail}.py).

export interface CourseListItem {
  id: string;
  title: string;
  slug: string;
  short_description: string;
  description: string;
  thumbnail_url: string | null;
  category?: {
    id: string;
    name: string;
    slug: string;
  };
  supports_online: boolean;
  supports_offline: boolean;
  language: string;
  estimated_weeks?: number;
  active_enrollment_count: number;
  status: string;
  price?: string;        // ✅ Убедитесь, что есть
  currency?: string;     // ✅ Убедитесь, что есть
}

export interface CourseListResponse {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: CourseListItem[];
}

export interface LessonSummary {
  id: string;
  title: string;
  order: number;
  estimated_minutes: number | null;
  is_published: boolean;
  is_free_preview: boolean;
  has_homework: boolean;
  has_quiz: boolean;
  has_practice: boolean;
}

export interface ModuleWithLessons {
  id: string;
  title: string;
  description: string | null;
  order: number;
  estimated_hours: number | null;
  is_published: boolean;
  lesson_count: number;
  lessons: LessonSummary[];
}

export interface CourseDetail {
  id: string;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  thumbnail_url: string;
  category_name: string;
  status: string;
  supports_online: boolean;
  supports_offline: boolean;
  language: string;
  estimated_weeks: number;
  is_sequential: boolean;
  active_enrollment_count: number;
  created_by_name: string;
  created_at: string;
  updated_at: string;
  modules: ModuleWithLessons[];
  // ✅ Новые поля
  price: string;
  currency: string;
}

export type ContentItemType = 'video' | 'recording' | 'text' | 'code' | 'pdf' | 'slides' | 'link';

export interface ContentItem {
  id: string;
  type: ContentItemType;
  title: string;
  description: string;
  url: string;
  body: string;
  duration_seconds: number | null;
  file_size_bytes: number | null;
  metadata: Record<string, any>;
  is_required: boolean;
  is_downloadable: boolean;
  order: number;
  created_at?: string;
  updated_at?: string;
}

export interface HomeworkInfo {
  id: string;
  title: string;
  description: string;
  instructions: string;
  max_score: number;
  type: string;
  submission_types_allowed: string[];
  allowed_file_extensions: string;
  max_file_size_mb: number;
  deadline_offset_days?: number;
}

export interface QuizQuestionInfo {
  id: string;
  item_type?: string;
  title?: string;
  [key: string]: unknown;
}

export interface QuizInfo {
  id: string;
  title: string;
  pass_score: number;
  max_attempts: number | null;
  time_limit_minutes: number | null;
  questions: QuizQuestionInfo[];
}

export interface PracticeItemInfo {
  id: string;
  title: string;
  description?: string;  // ✅ ДОБАВЛЕНО
  instructions?: string;
  practice_type: string;
  starter_code?: string;  // ✅ ДОБАВЛЕНО
  solution_code?: string;  // ✅ ДОБАВЛЕНО
  language?: string;  // ✅ ДОБАВЛЕНО
  hints?: string[];
  max_score: number;
  time_limit_minutes?: number;  // ✅ ДОБАВЛЕНО
  order: number;
}

export interface LessonDetail {
  id: string;
  title: string;
  description: string | null;
  order: number;
  estimated_minutes: number | null;
  is_free_preview: boolean;
  is_published: boolean;
  module_id: string;
  module_title: string;
  course_id: string;
  course_title: string;
  created_at: string;
  updated_at: string;
  content_items: ContentItem[];
  homework: HomeworkInfo | null;
  practice_items: PracticeItemInfo[];
  quiz: QuizInfo | null;
}
