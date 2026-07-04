'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, handleApiError } from '@/lib/api';
import { CourseDetail } from '@/types/learning';
import { CourseEnrollment } from '@/types/api';
import { Navbar, LoadingSpinner } from '@/components/ui';
import { EnrollModal } from '@/components/course';
import { useTranslation } from '@/lib/i18n/useTranslation';

const CONTENT_ICON: Record<string, string> = {
  video: '🎥',
  homework: '📝',
  quiz: '❓',
  practice: '💻',
};

export default function CourseDetailPage() {
  const params = useParams<{ slug: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const { t } = useTranslation();

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [enrollment, setEnrollment] = useState<CourseEnrollment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [enrollOpen, setEnrollOpen] = useState(false);
  const [enrolling, setEnrolling] = useState(false);
  const [enrollError, setEnrollError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.learning.getCourse(params.slug);
        if (!active) return;
        setCourse(data);

        if (user) {
          const enrollments = await api.enrollment.getMyEnrollments().catch(() => []);
          const mine = enrollments.find((e) => e.course_id === data.id && e.status !== 'dropped');
          if (active) setEnrollment(mine || null);
        }
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => { active = false; };
  }, [params.slug, user]);

  const handleEnroll = async (format: 'online' | 'offline') => {
    if (!course) return;

    if (parseFloat(course.price) > 0) {
      router.push(`/courses/${course.slug}/checkout`);
      return;
    }

    setEnrolling(true);
    setEnrollError(null);
    try {
      const enr = await api.enrollment.enroll({ course_id: course.id, delivery_format: format });
      setEnrollment(enr);
      setEnrollOpen(false);
      router.push(`/courses/${course.slug}?enrolled=1`);
    } catch (err) {
      setEnrollError(handleApiError(err));
    } finally {
      setEnrolling(false);
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen message={t.courseDetail.loading} />;
  }

  if (error || !course) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-16 text-center">
          <div className="text-5xl mb-4">📚</div>
          <p className="text-destructive mb-4 font-body">{error || t.courseDetail.notFound}</p>
          <Link href="/courses" className="text-primary hover:text-primary/80 font-body">
            {t.courseDetail.backToList}
          </Link>
        </div>
      </div>
    );
  }

  const justEnrolled = searchParams.get('enrolled') === '1';
  const isPaidCourse = parseFloat(course.price) > 0;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <div className="relative overflow-hidden border-b border-border">
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse at top, rgba(129,140,248,0.15) 0%, transparent 70%)',
          }}
        />

        <div className="mt-10 relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {justEnrolled && (
            <div className="mb-6 bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm font-body">
              {t.courseDetail.enrolled}
            </div>
          )}

          <div className="flex flex-col lg:flex-row gap-10">
            {/* Course Info */}
            <div className="flex-1">
              {course.category_name && (
                <span className="text-sm font-semibold text-primary font-mono">
                  {course.category_name}
                </span>
              )}
              <h1 className="text-3xl md:text-4xl font-bold text-foreground mt-2 mb-4 font-heading">
                {course.title}
              </h1>
              <p className="text-muted-foreground max-w-2xl mb-6 whitespace-pre-line font-body">
                {course.short_description}
              </p>

              {/* ✅ Meta info с форматом */}
              <div className="flex flex-wrap gap-6 text-sm text-muted-foreground font-body">
                {course.created_by_name && (
                  <span className="flex items-center gap-1.5">
                    <span className="text-primary">👤</span> {course.created_by_name}
                  </span>
                )}
                {course.estimated_weeks && (
                  <span className="flex items-center gap-1.5">
                    <span className="text-primary">⏱</span> {course.estimated_weeks} {t.courses.weeks}
                  </span>
                )}
                <span className="flex items-center gap-1.5">
                  <span className="text-primary">👥</span> {course.active_enrollment_count} {t.courseDetail.students}
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="text-primary">🌐</span> {course.language?.toUpperCase()}
                </span>
                {/* ✅ Формат обучения */}
                <span className="flex items-center gap-1.5">
                  <span className="text-primary">📚</span>
                  {[course.supports_online && t.courses.online, course.supports_offline && t.courses.offline]
                    .filter(Boolean)
                    .join(' / ')}
                </span>
              </div>
            </div>

            {/* Enrollment Card */}
            <div className="lg:w-80 card p-6 self-start">
              {enrollment ? (
                <>
                  {/* Статистика курса */}
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    <div className="bg-muted rounded-lg p-2 text-center">
                      <p className="text-lg font-bold text-primary font-heading">{course.modules.length}</p>
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-mono">Modul</p>
                    </div>
                    <div className="bg-muted rounded-lg p-2 text-center">
                      <p className="text-lg font-bold text-primary font-heading">
                        {course.modules.reduce((sum, m) => sum + m.lesson_count, 0)}
                      </p>
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-mono">Dars</p>
                    </div>
                    <div className="bg-muted rounded-lg p-2 text-center">
                      <p className="text-lg font-bold text-primary font-heading">{course.estimated_weeks || '—'}</p>
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-mono">Hafta</p>
                    </div>
                  </div>

                  {/* ✅ Кнопка "Darsni davom ettirish" — ведёт на страницу модулей */}
                  <Link
                    href={`/courses/${course.slug}/modules`}
                    className="btn-primary w-full block text-center"
                  >
                    📚 {t.courseDetail.continueLearning}
                  </Link>
                </>
              ) : user ? (
                <>
                  {/* Прогресс бар для платных курсов */}
                  {isPaidCourse && (
                    <div className="mb-4">
                      <p className="text-3xl font-bold text-primary font-heading">
                        {parseFloat(course.price).toLocaleString()} {course.currency}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1 font-body">
                        {t.courseDetail.oneTimePayment}
                      </p>
                    </div>
                  )}

                  <p className="text-sm text-muted-foreground mb-4 font-body">
                    {isPaidCourse ? t.courseDetail.paidPrompt : t.courseDetail.enrollPrompt}
                  </p>

                  <button
                    onClick={() => setEnrollOpen(true)}
                    className="btn-primary w-full"
                  >
                    {isPaidCourse ? `💳 ${t.courseDetail.buy}` : `✨ ${t.courseDetail.enroll}`}
                  </button>
                </>
              ) : (
                <>
                  <p className="text-sm text-muted-foreground mb-4 font-body">
                    {t.courseDetail.loginRequired}
                  </p>
                  <Link
                    href={`/login?next=/courses/${course.slug}`}
                    className="btn-primary w-full block text-center"
                  >
                    {t.courseDetail.login}
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ✅ Main Content — без табов */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-3xl space-y-12">
          {/* ✅ Umumiy ma'lumot */}
          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4 font-heading">
              {t.courseDetail.tabs.overview}
            </h2>
            <div className="card p-6">
              <p className="text-foreground whitespace-pre-line font-body leading-relaxed">
                {course.description}
              </p>
            </div>
          </section>

          {/* ✅ O'quv dasturi */}
          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4 font-heading">
              {t.courseDetail.tabs.curriculum}
            </h2>
            <div className="space-y-4">
              {course.modules.map((module) => (
                <details
                  key={module.id}
                  className="card overflow-hidden group"
                  open
                >
                  <summary className="flex items-center justify-between px-5 py-4 cursor-pointer list-none">
                    <div>
                      <h3 className="font-semibold text-foreground font-heading">
                        {module.title}
                      </h3>
                      <p className="text-xs text-muted-foreground mt-0.5 font-mono">
                        {module.lesson_count} {t.courseDetail.lessons}
                        {module.estimated_hours ? ` · ${module.estimated_hours} ${t.courseDetail.hours}` : ''}
                      </p>
                    </div>
                    <span className="text-muted-foreground group-open:rotate-180 transition-transform">
                      ▾
                    </span>
                  </summary>
                  <div className="border-t border-border divide-y divide-border">
                    {module.lessons.map((lesson) => {
                      const accessible = lesson.is_free_preview || !!enrollment;
                      const icons = [
                        'video',
                        lesson.has_homework && 'homework',
                        lesson.has_quiz && 'quiz',
                        lesson.has_practice && 'practice',
                      ].filter(Boolean) as string[];

                      const row = (
                        <div className="flex items-center justify-between px-5 py-3">
                          <div className="flex items-center gap-3">
                            <span className="text-sm text-muted-foreground w-5 font-mono">
                              {lesson.order}.
                            </span>
                            <span
                              className={`text-sm font-body ${
                                accessible ? 'text-foreground' : 'text-muted-foreground'
                              }`}
                            >
                              {lesson.title}
                            </span>
                            <span className="flex gap-1 text-xs">
                              {icons.map((i) => (
                                <span key={i}>{CONTENT_ICON[i]}</span>
                              ))}
                            </span>
                            {lesson.is_free_preview && (
                              <span className="text-xs text-info font-semibold font-mono">
                                {t.courseDetail.free}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono">
                            {lesson.estimated_minutes && (
                              <span>{lesson.estimated_minutes} {t.courseDetail.minutes}</span>
                            )}
                            {!accessible && <span>{t.courseDetail.locked}</span>}
                          </div>
                        </div>
                      );

                      return accessible ? (
                        <Link
                          key={lesson.id}
                          href={`/courses/${course.slug}/lessons/${lesson.id}`}
                          className="block hover:bg-muted/30 transition-colors"
                        >
                          {row}
                        </Link>
                      ) : (
                        <div key={lesson.id} className="cursor-not-allowed">
                          {row}
                        </div>
                      );
                    })}
                  </div>
                </details>
              ))}
            </div>
          </section>
        </div>
      </div>

      <EnrollModal
        open={enrollOpen}
        courseTitle={course.title}
        supportsOnline={course.supports_online}
        supportsOffline={course.supports_offline}
        loading={enrolling}
        error={enrollError}
        onConfirm={handleEnroll}
        onCancel={() => setEnrollOpen(false)}
      />
    </div>
  );
}