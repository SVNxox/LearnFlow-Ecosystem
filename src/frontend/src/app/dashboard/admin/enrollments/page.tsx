'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { AdminEnrollment } from '@/types/api';
import { StatusBadge } from '@/components/ui';
import { formatDate } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

const STATUS_TABS = [
  { value: '', labelKey: 'all' as const },
  { value: 'pending', labelKey: 'pending' as const },
  { value: 'active', labelKey: 'active' as const },
  { value: 'suspended', labelKey: 'suspended' as const },
  { value: 'completed', labelKey: 'completed' as const },
  { value: 'dropped', labelKey: 'dropped' as const },
];

function EnrollmentsContent() {
  const { t } = useTranslation();
  const router = useRouter();
  const sp = useSearchParams();
  const status = sp.get('status') || '';
  const page = parseInt(sp.get('page') || '1', 10);
  const searchFromUrl = sp.get('search') || '';

  const [enrollments, setEnrollments] = useState<AdminEnrollment[]>([]);
  const [count, setCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchInput, setSearchInput] = useState(searchFromUrl);

  const updateParam = useCallback((key: string, value: string | null) => {
    const params = new URLSearchParams(sp.toString());
    if (value) params.set(key, value); else params.delete(key);
    if (key !== 'page') params.delete('page');
    router.push(`/dashboard/admin/enrollments?${params.toString()}`);
  }, [router, sp]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== searchFromUrl) {
        updateParam('search', searchInput || null);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchInput, searchFromUrl, updateParam]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    adminApi.getAllEnrollments({
      status: status || undefined,
      search: searchFromUrl || undefined,
      page,
    })
      .then((data) => {
        if (!active) return;
        setEnrollments(data?.results || []);
        setCount(data?.count || 0);
        setTotalPages(data?.total_pages || 1);
      })
      .catch((err) => {
        if (active) {
          setEnrollments([]);
          setError(handleApiError(err));
        }
      })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [status, page, searchFromUrl]);

  // Статистика
  const stats = {
    total: count,
    active: enrollments.filter((e) => e.status === 'active').length,
    pending: enrollments.filter((e) => e.status === 'pending').length,
    completed: enrollments.filter((e) => e.status === 'completed').length,
  };

  return (
    <AdminLayout roles={['admin']}>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-foreground font-heading">
          {t.enrollments.title} ({count})
        </h1>
        <p className="text-sm text-muted-foreground mt-1 font-body">
          {t.enrollments.subtitle}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.enrollments.total}</p>
          <p className="stat-value mt-2">{stats.total}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.enrollments.active}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-success)' }}>{stats.active}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.enrollments.pending}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-warning)' }}>{stats.pending}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.enrollments.completed}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-info)' }}>{stats.completed}</p>
        </div>
      </div>

      {/* Status tabs */}
      <div className="filter-pills mb-4">
        {STATUS_TABS.map(({ value, labelKey }) => (
          <button
            key={value}
            onClick={() => updateParam('status', value || null)}
            className={`filter-pill ${status === value ? 'filter-pill-active' : 'filter-pill-inactive'}`}
          >
            {t.enrollments.filters[labelKey]}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder={t.enrollments.search}
            className="input pl-10"
          />
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            🔍
          </span>
          {searchInput && (
            <button
              type="button"
              onClick={() => setSearchInput('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-card border border-border rounded-2xl overflow-hidden">
        <table className="min-w-full divide-y divide-border">
          <thead>
            <tr className="bg-muted/50">
              {[
                t.enrollments.student,
                t.enrollments.course,
                t.enrollments.format,
                t.enrollments.status,
                t.enrollments.enrolledAt,
                t.enrollments.actions,
              ].map((h) => (
                <th
                  key={h}
                  className="px-5 py-3 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider font-mono"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <tr key={i}>
                  <td colSpan={6} className="px-5 py-4">
                    <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                  </td>
                </tr>
              ))
            ) : enrollments.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center">
                  <div className="text-3xl mb-3">🎓</div>
                  <p className="text-sm text-muted-foreground font-body">
                    {searchFromUrl ? t.enrollments.noEnrollmentsFound : t.enrollments.noEnrollments}
                  </p>
                </td>
              </tr>
            ) : (
              enrollments.map((e) => (
                <tr key={e.id} className="hover:bg-muted/30 transition-colors">
                  {/* Student */}
                  <td className="px-5 py-3.5">
                    <p className="text-sm font-medium text-foreground font-body">
                      {e.user_name || e.user_email}
                    </p>
                    {e.user_name && (
                      <p className="text-xs text-muted-foreground font-mono mt-0.5">
                        {e.user_email}
                      </p>
                    )}
                  </td>

                  {/* Course */}
                  <td className="px-5 py-3.5 text-sm text-foreground font-body">
                    {e.course_title}
                  </td>

                  {/* Format */}
                  <td className="px-5 py-3.5">
                    <span className="text-xs px-2 py-0.5 rounded-md bg-muted text-muted-foreground font-mono">
                      {t.enrollments.formats[e.delivery_format as keyof typeof t.enrollments.formats] || e.delivery_format}
                    </span>
                  </td>

                  {/* Status */}
                  <td className="px-5 py-3.5">
                    <StatusBadge status={e.status} />
                  </td>

                  {/* Enrolled at */}
                  <td className="px-5 py-3.5 text-xs text-muted-foreground font-mono">
                    {formatDate(e.enrolled_at)}
                  </td>

                  {/* Actions */}
                  <td className="px-5 py-3.5">
                    <Link
                      href={`/admin/enrollments/${e.id}`}
                      className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                    >
                      {t.enrollments.actions.view}
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-6">
          {page > 1 && (
            <button
              onClick={() => updateParam('page', String(page - 1))}
              className="btn-ghost text-sm"
            >
              {t.enrollments.pagination.previous}
            </button>
          )}
          <span className="text-sm text-muted-foreground font-mono px-4">
            {t.enrollments.pagination.page} {page} {t.enrollments.pagination.of} {totalPages}
          </span>
          {page < totalPages && (
            <button
              onClick={() => updateParam('page', String(page + 1))}
              className="btn-ghost text-sm"
            >
              {t.enrollments.pagination.next}
            </button>
          )}
        </div>
      )}
    </AdminLayout>
  );
}

export default function AdminEnrollmentsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <EnrollmentsContent />
    </Suspense>
  );
}