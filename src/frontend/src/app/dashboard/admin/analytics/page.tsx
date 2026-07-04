'use client';

import { useEffect, useState } from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, isNotImplemented } from '@/lib/admin-api';
import NotImplementedBanner from '@/components/admin/NotImplementedBanner';
import { useTranslation } from '@/lib/i18n/useTranslation';

interface Stats {
  totalCourses: number;
  publishedCourses: number;
  totalEnrollments: number;
  activeEnrollments: number;
  completedEnrollments: number;
  totalRevenue: string | null;
  revenueAvailable: boolean;
}

export default function AdminAnalyticsPage() {
  const { t } = useTranslation();
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([
      adminApi.getCourses({ page_size: 1 }).catch(() => null),
      adminApi.getCourses({ status: 'published', page_size: 1 }).catch(() => null),
      adminApi.getAllEnrollments({ page: 1 }).catch(() => null),
      adminApi.getAllEnrollments({ status: 'active', page: 1 }).catch(() => null),
      adminApi.getAllEnrollments({ status: 'completed', page: 1 }).catch(() => null),
      adminApi.getAllPayments({ status: 'completed', page: 1 }).catch((err) =>
        isNotImplemented(err) ? 'NOT_IMPLEMENTED' : null
      ),
    ]).then(([all, published, enrollAll, enrollActive, enrollCompleted, payments]) => {
      if (!active) return;
      let totalRevenue: string | null = null;
      let revenueAvailable = false;
      if (payments && payments !== 'NOT_IMPLEMENTED') {
        revenueAvailable = true;
        const sum = (payments as { results: { amount: string }[] }).results.reduce(
          (s, p) => s + parseFloat(p.amount), 0
        );
        totalRevenue = sum.toLocaleString();
      }
      setStats({
        totalCourses: all?.count || 0,
        publishedCourses: published?.count || 0,
        totalEnrollments: enrollAll?.count || 0,
        activeEnrollments: enrollActive?.count || 0,
        completedEnrollments: enrollCompleted?.count || 0,
        totalRevenue,
        revenueAvailable,
      });
    }).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  return (
    <AdminLayout roles={['admin']}>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-foreground font-heading">
          {t.analytics.title}
        </h1>
        <p className="text-sm text-muted-foreground mt-1 font-body">
          {t.analytics.subtitle}
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="stat-card animate-pulse">
              <div className="h-3 bg-muted rounded w-1/2 mb-3" />
              <div className="h-8 bg-muted rounded w-1/3" />
            </div>
          ))}
        </div>
      ) : stats ? (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            <StatCard
              label={t.analytics.totalCourses}
              value={stats.totalCourses}
              color="var(--color-primary)"
              icon="📚"
            />
            <StatCard
              label={t.analytics.publishedCourses}
              value={stats.publishedCourses}
              color="var(--color-success)"
              icon="✅"
            />
            <StatCard
              label={t.analytics.totalEnrollments}
              value={stats.totalEnrollments}
              color="var(--color-info)"
              icon="🎓"
            />
            <StatCard
              label={t.analytics.activeEnrollments}
              value={stats.activeEnrollments}
              color="var(--color-warning)"
              icon="⚡"
            />
            <StatCard
              label={t.analytics.completedEnrollments}
              value={stats.completedEnrollments}
              color="var(--color-success)"
              icon="🏆"
            />
            <StatCard
              label={t.analytics.totalRevenue}
              value={stats.revenueAvailable ? `${stats.totalRevenue} UZS` : '—'}
              color="var(--color-accent)"
              icon="💰"
            />
          </div>

          {!stats.revenueAvailable && <NotImplementedBanner />}
        </>
      ) : null}
    </AdminLayout>
  );
}

// ── Stat Card Component ──────────────────────────────────────────────────────

function StatCard({
  label,
  value,
  color,
  icon,
}: {
  label: string;
  value: string | number;
  color: string;
  icon: string;
}) {
  return (
    <div className="stat-card hover:border-primary/30 transition-all duration-200">
      <div className="flex items-start justify-between mb-3">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
          style={{ backgroundColor: color + '15' }}
        >
          {icon}
        </div>
      </div>
      <p className="stat-value" style={{ color }}>
        {value}
      </p>
      <p className="stat-label mt-1 uppercase tracking-wider">{label}</p>
    </div>
  );
}