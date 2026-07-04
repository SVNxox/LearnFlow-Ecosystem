'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi } from '@/lib/admin-api';
import { api } from '@/lib/api';
import { useTranslation } from '@/lib/i18n/useTranslation';

export default function StaffDashboardPage() {
  const { t } = useTranslation();
  const [stats, setStats] = useState({
    courses: 0,
    pendingA: 0,
    pendingS: 0,
    loading: true,
  });

  useEffect(() => {
    Promise.all([
      adminApi.getCourses({ page_size: 1 }).catch(() => null),
      api.assessment.getPendingReviews().catch(() => ({ total_count: 0 })),
      api.submissions.getPendingReviews().catch(() => []),
    ]).then(([courses, ar, sr]) => {
      setStats({
        courses: courses?.count || 0,
        pendingA: ar.total_count || 0,
        pendingS: (sr as unknown[]).length,
        loading: false,
      });
    }).catch(() => {
      setStats((s) => ({ ...s, loading: false }));
    });
  }, []);

  const cards = [
    {
      label: t.staffDashboard.courses,
      value: stats.courses,
      href: '/admin/courses',
      icon: '📚',
      color: 'var(--color-primary)',
    },
    {
      label: t.staffDashboard.pendingAssessments,
      value: stats.pendingA,
      href: '/dashboard/mentor/assessments',
      icon: '📋',
      color: 'var(--color-warning)',
    },
    {
      label: t.staffDashboard.pendingSubmissions,
      value: stats.pendingS,
      href: '/dashboard/mentor/submissions',
      icon: '📝',
      color: 'var(--color-info)',
    },
  ];

  return (
    <AdminLayout roles={['staff', 'admin']}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground font-heading">
          {t.staffDashboard.title}
        </h1>
        <p className="text-sm text-muted-foreground mt-1 font-body">
          {t.staffDashboard.subtitle}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {cards.map((card) => (
          <Link
            key={card.label}
            href={card.href}
            className="stat-card hover:border-primary/30 transition-all duration-200 group"
          >
            <div className="flex items-start justify-between mb-3">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                style={{ backgroundColor: card.color + '18' }}
              >
                {card.icon}
              </div>
              {card.value > 0 && (
                <span className="text-[10px] font-semibold font-mono px-1.5 py-0.5 rounded bg-primary/10 text-primary">
                  faol
                </span>
              )}
            </div>
            <p
              className="stat-value"
              style={{ color: card.color }}
            >
              {stats.loading ? (
                <span className="inline-block h-8 w-16 bg-muted rounded animate-pulse" />
              ) : (
                card.value
              )}
            </p>
            <p className="stat-label mt-1 uppercase tracking-wider">{card.label}</p>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-3">
        <Link href="/admin/courses" className="btn-primary inline-flex items-center gap-2">
          {t.staffDashboard.myCourses}
        </Link>
        <Link href="/admin/courses/create" className="btn-ghost inline-flex items-center gap-2">
          {t.staffDashboard.createCourse}
        </Link>
      </div>
    </AdminLayout>
  );
}