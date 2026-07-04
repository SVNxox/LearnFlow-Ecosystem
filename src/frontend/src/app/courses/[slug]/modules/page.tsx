'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, handleApiError } from '@/lib/api';
import { CourseDetail } from '@/types/learning';
import { CourseEnrollment } from '@/types/api';
import { Navbar, LoadingSpinner } from '@/components/ui';
import CourseSidebar from '@/components/course/CourseSidebar';
import { useTranslation } from '@/lib/i18n/useTranslation';

export default function CourseModulesPage() {
  const params = useParams<{ slug: string }>();
  const { user } = useAuth();
  const { t } = useTranslation();

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [enrollment, setEnrollment] = useState<CourseEnrollment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
          const mine = enrollments.find((e: any) => e.course_id === data.id && e.status !== 'dropped');
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

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (error || !course) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-16 text-center">
          <div className="text-5xl mb-4">📚</div>
          <p className="text-destructive mb-4 font-body">{error || 'Kurs topilmadi'}</p>
          <Link href="/courses" className="text-primary hover:text-primary/80 font-body">
            ← Kurslarga qaytish
          </Link>
        </div>
      </div>
    );
  }

  const totalLessons = course.modules.reduce((sum, m) => sum + m.lesson_count, 0);
  const totalHours = course.modules.reduce((sum, m) => sum + (m.estimated_hours || 0), 0);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="flex pt-14">
        {/* Sidebar */}
        <div className="w-80 flex-shrink-0 h-[calc(100vh-3.5rem)] sticky top-14">
          <CourseSidebar
            course={course}
            enrollment={enrollment}
          />
        </div>

        {/* Main content */}
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-3xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              {course.category_name && (
                <span className="text-sm font-semibold text-primary font-mono">
                  {course.category_name}
                </span>
              )}
              <h1 className="text-3xl font-bold text-foreground mt-2 mb-3 font-heading">
                {course.title}
              </h1>
              <p className="text-muted-foreground font-body">
                {course.short_description}
              </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="card p-4 text-center">
                <div className="text-2xl mb-1">📚</div>
                <p className="text-2xl font-bold text-primary font-heading">{course.modules.length}</p>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mt-1">Modullar</p>
              </div>
              <div className="card p-4 text-center">
                <div className="text-2xl mb-1">📖</div>
                <p className="text-2xl font-bold text-primary font-heading">{totalLessons}</p>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mt-1">Darslar</p>
              </div>
              <div className="card p-4 text-center">
                <div className="text-2xl mb-1">⏱</div>
                <p className="text-2xl font-bold text-primary font-heading">{totalHours || '—'}</p>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mt-1">Soatlar</p>
              </div>
              <div className="card p-4 text-center">
                <div className="text-2xl mb-1">👥</div>
                <p className="text-2xl font-bold text-primary font-heading">{course.active_enrollment_count}</p>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mt-1">Talabalar</p>
              </div>
            </div>

            {/* Content */}
            {enrollment ? (
              <div className="card p-6">
                <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm font-semibold mb-4 font-body">
                  ✅ Siz ushbu kursga yozildingiz
                </div>
                <p className="text-foreground mb-6 font-body leading-relaxed">
                  Chap tomondagi modullardan darsni tanlang va o'qishni boshlang.
                  Har bir modulda mavzular ketma-ket joylashgan.
                </p>

                {/* Быстрый старт — первый урок */}
                {course.modules.length > 0 && course.modules[0].lessons.length > 0 && (
                  <Link
                    href={`/courses/${course.slug}/lessons/${course.modules[0].lessons[0].id}`}
                    className="btn-primary inline-flex items-center gap-2"
                  >
                    ▶ Boshlash: {course.modules[0].lessons[0].title}
                  </Link>
                )}
              </div>
            ) : (
              <div className="card p-6">
                <div className="bg-warning/10 border border-warning/30 text-warning px-4 py-3 rounded-xl text-sm font-semibold mb-4 font-body">
                  ⚠️ Siz hali kursga yozilmadingiz
                </div>
                <p className="text-foreground mb-6 font-body leading-relaxed">
                  Kursga yozilish uchun kurs sahifasiga qayting va "Ro'yxatdan o'tish" tugmasini bosing.
                </p>
                <Link
                  href={`/courses/${course.slug}`}
                  className="btn-primary inline-flex items-center gap-2"
                >
                  ← Kurs sahifasiga qaytish
                </Link>
              </div>
            )}

            {/* Описание курса */}
            <div className="mt-8">
              <h2 className="text-xl font-bold text-foreground mb-4 font-heading">
                {t.courseDetail.tabs.overview}
              </h2>
              <div className="card p-6">
                <p className="text-foreground whitespace-pre-line font-body leading-relaxed">
                  {course.description}
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}