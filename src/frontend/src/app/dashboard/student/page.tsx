'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { api, handleApiError } from '@/lib/api';
import { resolveContinueUrl } from '@/lib/progress-api';
import { CourseEnrollment, ProgressDashboardCourse } from '@/types/api';
import { LoadingSpinner, EmptyState, StatusBadge, ProgressBar } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';

interface EnrichedCourse extends ProgressDashboardCourse {
  slug: string | null;
}

export default function StudentDashboardPage() {
  const router = useRouter();
  const { t } = useTranslation();
  const [enrollments, setEnrollments] = useState<CourseEnrollment[]>([]);
  const [courses, setCourses] = useState<EnrichedCourse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [continuingId, setContinuingId] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [enrollmentsData, dashboard, courseList] = await Promise.all([
          api.enrollment.getMyEnrollments(),
          api.progress.getDashboard(),
          api.learning.getCourses({ page_size: 100 }).catch(() => null),
        ]);
        if (!active) return;

        const slugMap = new Map<string, string>();
        courseList?.results.forEach((c) => slugMap.set(c.id, c.slug));

        const enriched: EnrichedCourse[] = dashboard.courses
          .map((c) => ({ ...c, slug: slugMap.get(c.course_id) || null }))
          .sort((a, b) => {
            const ta = a.last_activity_at ? new Date(a.last_activity_at).getTime() : 0;
            const tb = b.last_activity_at ? new Date(b.last_activity_at).getTime() : 0;
            return tb - ta;
          });

        setEnrollments(enrollmentsData);
        setCourses(enriched);
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => {
      active = false;
    };
  }, []);

  const stats = useMemo(() => {
    return {
      enrolled: enrollments.filter((e) => e.status !== 'dropped').length,
      completed: courses.filter((c) => c.status === 'completed').length,
      inProgress: courses.filter((c) => c.status === 'in_progress').length,
    };
  }, [enrollments, courses]);

  const handleContinue = async (course: EnrichedCourse) => {
    if (!course.slug) return;
    setContinuingId(course.enrollment_id);
    try {
      const { url } = await resolveContinueUrl(course.enrollment_id, course.slug);
      router.push(url);
    } catch {
      router.push(`/courses/${course.slug}`);
    } finally {
      setContinuingId(null);
    }
  };

  return (
    <DashboardLayout allowedRoles={['student']}>
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      ) : (
        <div className="space-y-8">
          {/* Header */}
          <div className="mt-10">
            <h1 className="text-2xl font-bold text-foreground font-heading">
              {t.studentDashboard.title}
            </h1>
            <p className="text-sm text-muted-foreground mt-1 font-body">
              {t.studentDashboard.subtitle}
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="stat-card">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
                  style={{ backgroundColor: 'var(--color-info-bg)' }}
                >
                  📚
                </div>
                <div>
                  <p className="stat-label uppercase tracking-wider">
                    {t.studentDashboard.enrolledCourses}
                  </p>
                  <p className="stat-value" style={{ color: 'var(--color-info)' }}>
                    {stats.enrolled}
                  </p>
                </div>
              </div>
            </div>
            <div className="stat-card">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
                  style={{ backgroundColor: 'var(--color-success-bg)' }}
                >
                  ✅
                </div>
                <div>
                  <p className="stat-label uppercase tracking-wider">
                    {t.studentDashboard.completedCourses}
                  </p>
                  <p className="stat-value" style={{ color: 'var(--color-success)' }}>
                    {stats.completed}
                  </p>
                </div>
              </div>
            </div>
            <div className="stat-card">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
                  style={{ backgroundColor: 'var(--color-warning-bg)' }}
                >
                  ⚡
                </div>
                <div>
                  <p className="stat-label uppercase tracking-wider">
                    {t.studentDashboard.inProgressCourses}
                  </p>
                  <p className="stat-value" style={{ color: 'var(--color-warning)' }}>
                    {stats.inProgress}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* My Courses */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-foreground font-heading">
                {t.studentDashboard.myCourses}
              </h2>
              <Link
                href="/my-courses"
                className="text-sm font-semibold text-primary hover:text-primary/80 font-body"
              >
                {t.studentDashboard.viewAll} →
              </Link>
            </div>

            {courses.length === 0 ? (
              <div className="card p-12 text-center">
                <div className="text-5xl mb-4">📚</div>
                <h3 className="text-lg font-semibold text-foreground mb-2 font-heading">
                  {t.studentDashboard.noCourses}
                </h3>
                <p className="text-sm text-muted-foreground mb-6 max-w-sm mx-auto font-body">
                  {t.studentDashboard.noCoursesDesc}
                </p>
                <Link href="/courses" className="btn-primary inline-flex items-center gap-2">
                  🔍 {t.studentDashboard.browseCourses}
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {courses.slice(0, 4).map((course) => (
                  <div
                    key={course.enrollment_id}
                    className="card p-5 hover:border-primary/30 transition-all duration-200"
                  >
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <h3 className="font-semibold text-foreground leading-snug font-body">
                        {course.course_title}
                      </h3>
                      <StatusBadge status={course.status} />
                    </div>
                    <ProgressBar value={course.completion_percentage} size="sm" />
                    <div className="flex items-center justify-between mt-3">
                      <p className="text-xs text-muted-foreground font-mono">
                        {course.completed_lessons}/{course.total_lessons} {t.studentDashboard.lessons}
                      </p>
                      <button
                        onClick={() => handleContinue(course)}
                        disabled={continuingId === course.enrollment_id || !course.slug}
                        className="text-sm font-semibold text-primary hover:text-primary/80 font-body disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {continuingId === course.enrollment_id
                          ? t.studentDashboard.loading
                          : t.studentDashboard.continue}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div>
            <h2 className="text-lg font-semibold text-foreground mb-4 font-heading">
              {t.studentDashboard.quickActions}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Link
                href="/courses"
                className="card p-5 hover:border-primary/30 hover:-translate-y-0.5 transition-all duration-200 group"
              >
                <div className="text-3xl mb-3">🔍</div>
                <p className="font-semibold text-foreground font-body group-hover:text-primary transition-colors">
                  {t.studentDashboard.viewCourses}
                </p>
                <p className="text-xs text-muted-foreground mt-1 font-body">
                  Yangi kurslarni kashf eting
                </p>
              </Link>
              <Link
                href="/certificates"
                className="card p-5 hover:border-primary/30 hover:-translate-y-0.5 transition-all duration-200 group"
              >
                <div className="text-3xl mb-3">🎓</div>
                <p className="font-semibold text-foreground font-body group-hover:text-primary transition-colors">
                  {t.studentDashboard.myCertificates}
                </p>
                <p className="text-xs text-muted-foreground mt-1 font-body">
                  Sertifikatlaringizni ko'ring
                </p>
              </Link>
              <Link
                href="/profile"
                className="card p-5 hover:border-primary/30 hover:-translate-y-0.5 transition-all duration-200 group"
              >
                <div className="text-3xl mb-3">👤</div>
                <p className="font-semibold text-foreground font-body group-hover:text-primary transition-colors">
                  {t.studentDashboard.myProfile}
                </p>
                <p className="text-xs text-muted-foreground mt-1 font-body">
                  Profilingizni tahrirlang
                </p>
              </Link>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}