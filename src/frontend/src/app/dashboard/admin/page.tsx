'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi } from '@/lib/admin-api';
import { api } from '@/lib/api';
import { AdminEnrollment } from '@/types/api';
import { StatusBadge } from '@/components/ui';

interface DashStats {
  totalCourses: number;
  totalEnrollments: number;
  activeEnrollments: number;
  pendingAssessments: number;
  pendingSubmissions: number;
}

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<DashStats | null>(null);
  const [recentEnrollments, setRecentEnrollments] = useState<AdminEnrollment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([
      adminApi.getCourses({ page_size: 100 }).catch(() => null),
      adminApi.getAllEnrollments({ page: 1 }).catch(() => null),
      api.assessment.getPendingReviews().catch(() => ({ items: [], total_count: 0 })),
      api.submissions.getPendingReviews().catch(() => []),
    ]).then(([courses, enrollments, assessmentReviews, submissionReviews]) => {
      if (!active) return;
      setStats({
        totalCourses: courses?.count || 0,
        totalEnrollments: enrollments?.count || 0,
        activeEnrollments: enrollments?.results.filter((e) => e.status === 'active').length || 0,
        pendingAssessments: assessmentReviews.total_count || 0,
        pendingSubmissions: submissionReviews.length || 0,
      });
      setRecentEnrollments(enrollments?.results.slice(0, 5) || []);
    }).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  const statCards = stats ? [
    { label: 'Jami kurslar', value: stats.totalCourses, href: '/admin/courses', color: 'var(--color-info)' },
    { label: 'Jami o\'quvchilar', value: stats.totalEnrollments, href: '/dashboard/admin/enrollments', color: 'var(--color-success)' },
    { label: 'Faol o\'quvchilar', value: stats.activeEnrollments, href: '/dashboard/admin/enrollments', color: 'var(--color-primary)' },
    { label: 'Kutilayotgan tekshiruvlar', value: stats.pendingAssessments + stats.pendingSubmissions, href: '/dashboard/mentor', color: 'var(--color-warning)' },
  ] : [];

  return (
    <AdminLayout roles={['admin']}>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-foreground font-heading">Admin boshqaruv paneli</h1>
      </div>

      {/* Stat cards */}
      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[1,2,3,4].map((i) => (
            <div key={i} className="bg-card rounded-2xl border border-border p-5 animate-pulse h-24" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statCards.map((card) => (
            <Link
              key={card.label}
              href={card.href}
              className="stat-card hover:border-primary/30 hover:-translate-y-0.5 transition-all duration-200 group"
            >
              <p className="stat-label uppercase tracking-wider">{card.label}</p>
              <p className="stat-value mt-2" style={{ color: card.color }}>{card.value}</p>
            </Link>
          ))}
        </div>
      )}

      {/* Two columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Enrollments */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-border">
            <h2 className="text-sm font-semibold text-foreground font-body">So'nggi ro'yxatdan o'tganlar</h2>
            <Link
              href="/dashboard/admin/enrollments"
              className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
            >
              Barchasini ko'rish →
            </Link>
          </div>
          {loading ? (
            <div className="space-y-3">
              {[1,2,3].map((i) => (
                <div key={i} className="h-12 bg-muted rounded-xl animate-pulse" />
              ))}
            </div>
          ) : recentEnrollments.length === 0 ? (
            <p className="text-sm text-muted-foreground font-body">Hali ro'yxatdan o'tganlar yo'q.</p>
          ) : (
            <div className="space-y-3">
              {recentEnrollments.map((e) => (
                <div key={e.id} className="flex items-center justify-between text-sm p-2 rounded-lg hover:bg-muted transition-colors">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-foreground truncate font-body">
                      {e.user_name || e.user_email}
                    </p>
                    <p className="text-xs text-muted-foreground truncate font-body">
                      {e.course_title}
                    </p>
                  </div>
                  <div className="flex-shrink-0 ml-3">
                    <StatusBadge status={e.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pending Reviews */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-border">
            <h2 className="text-sm font-semibold text-foreground font-body">Kutilayotgan tekshiruvlar</h2>
          </div>
          {loading ? (
            <div className="space-y-3">
              {[1,2].map((i) => (
                <div key={i} className="h-12 bg-muted rounded-xl animate-pulse" />
              ))}
            </div>
          ) : stats ? (
            <div className="space-y-3">
              <Link
                href="/dashboard/mentor/assessments"
                className="flex items-center justify-between p-3 rounded-xl hover:bg-muted transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'var(--color-warning-bg)' }}>
                    <span style={{ color: 'var(--color-warning)' }}>📝</span>
                  </div>
                  <span className="text-sm text-foreground font-body">Testlarni tekshirish</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold font-heading" style={{ color: 'var(--color-warning)' }}>
                    {stats.pendingAssessments}
                  </span>
                  <span className="text-primary opacity-0 group-hover:opacity-100 transition-opacity">→</span>
                </div>
              </Link>

              <Link
                href="/dashboard/mentor/submissions"
                className="flex items-center justify-between p-3 rounded-xl hover:bg-muted transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'var(--color-info-bg)' }}>
                    <span style={{ color: 'var(--color-info)' }}>💻</span>
                  </div>
                  <span className="text-sm text-foreground font-body">Ishlarni tekshirish</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold font-heading" style={{ color: 'var(--color-info)' }}>
                    {stats.pendingSubmissions}
                  </span>
                  <span className="text-primary opacity-0 group-hover:opacity-100 transition-opacity">→</span>
                </div>
              </Link>
            </div>
          ) : null}
        </div>
      </div>
    </AdminLayout>
  );
}