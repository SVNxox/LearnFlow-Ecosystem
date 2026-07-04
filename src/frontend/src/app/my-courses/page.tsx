'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, handleApiError } from '@/lib/api';
import { resolveContinueUrl } from '@/lib/progress-api';
import { CourseEnrollment, Certificate, ProgressDashboardCourse } from '@/types/api';
import { Navbar, LoadingSpinner, EmptyState, StatusBadge, ProgressBar, ConfirmModal } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';

type Tab = 'all' | 'active' | 'completed' | 'dropped' | 'pending';

interface EnrichedEnrollment {
  enrollment: CourseEnrollment;
  progress: ProgressDashboardCourse | null;
  slug: string | null;
  title: string;
  certificate: Certificate | null;
}

export default function MyCoursesPage() {
  const router = useRouter();
  const { t } = useTranslation();
  const [items, setItems] = useState<EnrichedEnrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>('all');
  const [continuingId, setContinuingId] = useState<string | null>(null);
  const [dropTarget, setDropTarget] = useState<EnrichedEnrollment | null>(null);
  const [dropping, setDropping] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [enrollments, dashboard, certificates, courseList] = await Promise.all([
        api.enrollment.getMyEnrollments(),
        api.progress.getDashboard().catch(() => ({ courses: [] })),
        api.certificates.getMyCertificates().catch(() => []),
        api.learning.getCourses({ page_size: 100 }).catch(() => null),
      ]);

      const slugMap = new Map<string, { slug: string; title: string }>();
      courseList?.results.forEach((c) => slugMap.set(c.id, { slug: c.slug, title: c.title }));

      const enriched: EnrichedEnrollment[] = enrollments.map((enrollment) => {
        const progress = dashboard.courses.find((p) => p.enrollment_id === enrollment.id) || null;
        const courseInfo = slugMap.get(enrollment.course_id);
        const certificate = certificates.find((c) => c.enrollment_id === enrollment.id) || null;
        return {
          enrollment,
          progress,
          slug: courseInfo?.slug || null,
          title: progress?.course_title || courseInfo?.title || 'Kurs',
          certificate,
        };
      });

      enriched.sort((a, b) => {
        const ta = a.progress?.last_activity_at ? new Date(a.progress.last_activity_at).getTime() : 0;
        const tb = b.progress?.last_activity_at ? new Date(b.progress.last_activity_at).getTime() : 0;
        return tb - ta;
      });

      setItems(enriched);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtered = useMemo(() => {
    if (tab === 'all') return items;
    return items.filter((i) => i.enrollment.status === tab);
  }, [items, tab]);

  const handleContinue = async (item: EnrichedEnrollment) => {
    if (!item.slug) return;
    setContinuingId(item.enrollment.id);
    try {
      const { url } = await resolveContinueUrl(item.enrollment.id, item.slug);
      router.push(url);
    } catch {
      router.push(`/courses/${item.slug}`);
    } finally {
      setContinuingId(null);
    }
  };

  const handleDrop = async () => {
    if (!dropTarget) return;
    setDropping(true);
    try {
      await api.enrollment.dropEnrollment(dropTarget.enrollment.id, "Talaba tomonidan tark etildi");
      setDropTarget(null);
      load();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setDropping(false);
    }
  };

  const tabs: { key: Tab; labelKey: keyof typeof t.myCourses.tabs }[] = [
    { key: 'all', labelKey: 'all' },
    { key: 'active', labelKey: 'active' },
    { key: 'pending', labelKey: 'pending' },
    { key: 'completed', labelKey: 'completed' },
    { key: 'dropped', labelKey: 'dropped' },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6 mt-10">
          <h1 className="text-2xl font-bold text-foreground font-heading">
            {t.myCourses.title}
          </h1>
          <p className="text-sm text-muted-foreground mt-1 font-body">
            {t.myCourses.subtitle}
          </p>
        </div>

        {/* Tabs */}
        <div className="filter-pills mb-6">
          {tabs.map(({ key, labelKey }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`filter-pill ${tab === key ? 'filter-pill-active' : 'filter-pill-inactive'}`}
            >
              {t.myCourses.tabs[labelKey]}
            </button>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-6 font-body">
            {error}
          </div>
        )}

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="card p-12 text-center">
            <div className="text-5xl mb-4">📚</div>
            <h3 className="text-lg font-semibold text-foreground mb-2 font-heading">
              {t.myCourses.noCourses}
            </h3>
            <p className="text-sm text-muted-foreground mb-6 max-w-sm mx-auto font-body">
              {t.myCourses.noCoursesDesc}
            </p>
            <Link href="/courses" className="btn-primary inline-flex items-center gap-2">
              🔍 {t.myCourses.browseCourses}
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {filtered.map((item) => (
              <div
                key={item.enrollment.id}
                className="card p-5 hover:border-primary/30 transition-all duration-200"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  {/* Title & Status */}
                  <div className="flex-1 min-w-[200px]">
                    {item.slug ? (
                      <Link
                        href={`/courses/${item.slug}`}
                        className="font-semibold text-foreground hover:text-primary transition-colors font-body"
                      >
                        {item.title}
                      </Link>
                    ) : (
                      <span className="font-semibold text-foreground font-body">
                        {item.title}
                      </span>
                    )}
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      <StatusBadge status={item.enrollment.status} />
                      <span className="text-xs px-2 py-0.5 rounded-md bg-muted text-muted-foreground font-mono">
                        {t.myCourses.formats[item.enrollment.delivery_format as keyof typeof t.myCourses.formats] || item.enrollment.delivery_format}
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-3 flex-shrink-0">
                    {/* Payment button for pending */}
                    {item.enrollment.status === 'pending' && item.slug && (
                      <Link
                        href={`/courses/${item.slug}/checkout`}
                        className="btn-primary text-sm"
                      >
                        {t.myCourses.completePayment}
                      </Link>
                    )}

                    {/* Certificate link for completed */}
                    {item.enrollment.status === 'completed' && item.certificate && (
                      <Link
                        href="/certificates"
                        className="text-sm font-semibold text-primary hover:text-primary/80 font-body"
                      >
                        🎓 {t.myCourses.viewCertificate}
                      </Link>
                    )}

                    {/* Continue button for active */}
                    {item.enrollment.status === 'active' && (
                      <>
                        <button
                          onClick={() => handleContinue(item)}
                          disabled={continuingId === item.enrollment.id || !item.slug}
                          className="btn-primary text-sm"
                        >
                          {continuingId === item.enrollment.id
                            ? t.myCourses.loading
                            : t.myCourses.continue}
                        </button>
                        <button
                          onClick={() => setDropTarget(item)}
                          className="text-sm text-muted-foreground hover:text-destructive transition-colors font-body"
                        >
                          {t.myCourses.leave}
                        </button>
                      </>
                    )}
                  </div>
                </div>

                {/* Progress */}
                {item.progress && (
                  <div className="mt-4">
                    <ProgressBar value={item.progress.completion_percentage} size="sm" />
                    <p className="text-xs text-muted-foreground mt-1.5 font-mono">
                      {item.progress.completed_lessons}/{item.progress.total_lessons} {t.myCourses.lessons} ·{' '}
                      {Math.round(item.progress.completion_percentage)}%
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Leave confirmation modal */}
      <ConfirmModal
        open={!!dropTarget}
        title={t.myCourses.confirmLeave}
        description={t.myCourses.leaveDescription.replace('{course}', dropTarget?.title || '')}
        confirmLabel={t.myCourses.confirmLeaveButton}
        danger
        loading={dropping}
        onConfirm={handleDrop}
        onCancel={() => setDropTarget(null)}
      />
    </div>
  );
}