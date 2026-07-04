'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { CourseListItem } from '@/types/learning';
import CourseCategoryManager from '@/components/admin/CourseCategoryManager';
import { StatusBadge } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';

function CoursesContent() {
  const { t } = useTranslation();
  const router = useRouter();
  const sp = useSearchParams();

  const status = sp.get('status') || 'all';
  const page = parseInt(sp.get('page') || '1', 10);
  const searchFromUrl = sp.get('search') || '';

  const [courses, setCourses] = useState<CourseListItem[]>([]);
  const [count, setCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [searchInput, setSearchInput] = useState(searchFromUrl);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const updateParam = useCallback((key: string, value: string | null) => {
    const params = new URLSearchParams(sp.toString());
    if (value) params.set(key, value); else params.delete(key);
    if (key !== 'page') params.delete('page');
    router.push(`/admin/courses?${params.toString()}`);
  }, [router, sp]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== searchFromUrl) {
        updateParam('search', searchInput || null);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchInput, searchFromUrl, updateParam]);

  const loadCourses = useCallback(async () => {
    let active = true;
    setLoading(true);
    try {
      const data = await adminApi.getCourses({
        search: searchFromUrl || undefined,
        status: status,
        page,
        page_size: 20
      });
      if (active) {
        setCourses(data.results);
        setCount(data.count);
        setTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      if (active) setError(handleApiError(err));
    } finally {
      if (active) setLoading(false);
    }
    return () => { active = false; };
  }, [searchFromUrl, status, page]);

  useEffect(() => {
    loadCourses();
  }, [loadCourses]);

  const handleDelete = async (courseId: string, courseTitle: string) => {
    if (!confirm(`${t.courses.deleteConfirm}\n\n"${courseTitle}"\n\n${t.courses.deleteWarning}`)) return;

    setDeletingId(courseId);
    setError('');
    try {
      await adminApi.deleteCourse(courseId);
      await loadCourses();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setDeletingId(null);
    }
  };

  const statusTabs = [
    { value: 'all', label: t.courses.filters.all },
    { value: 'draft', label: t.courses.filters.draft },
    { value: 'published', label: t.courses.filters.published },
    { value: 'archived', label: t.courses.filters.archived },
  ];

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-foreground font-heading">
            {t.courses.title} ({count})
          </h1>
          <p className="text-sm text-muted-foreground mt-1 font-body">
            {t.courses.subtitle}
          </p>
        </div>
        <Link
          href="/admin/courses/create"
          className="btn-primary text-sm inline-flex items-center gap-2"
        >
          <span>+</span>
          {t.courses.createCourse}
        </Link>
      </div>

      {/* Status tabs */}
      <div className="filter-pills mb-4">
        {statusTabs.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => updateParam('status', value)}
            className={`filter-pill ${status === value ? 'filter-pill-active' : 'filter-pill-inactive'}`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="mb-4">
        <div className="flex gap-2 max-w-md">
          <div className="relative flex-1">
            <input
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder={t.courses.search}
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
        {searchInput && searchInput !== searchFromUrl && (
          <p className="text-xs text-muted-foreground mt-1 font-body">
            {t.courses.searching}: "{searchInput}"...
          </p>
        )}
      </div>

      {/* Category management */}
      <div className="mb-6 card p-4">
        <h3 className="text-sm font-semibold text-foreground mb-3 font-heading">
          {t.courses.categories}
        </h3>
        <CourseCategoryManager showManagement={true} />
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
                t.courses.titleColumn,
                t.courses.category,
                t.courses.format,
                t.courses.enrollments,
                t.courses.status,
                t.courses.actions,
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
            ) : courses.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center">
                  <div className="text-3xl mb-3">📚</div>
                  <p className="text-sm text-muted-foreground font-body">
                    {searchInput ? t.courses.noCourses : t.courses.noCoursesDesc}
                  </p>
                </td>
              </tr>
            ) : (
              courses.map((c) => (
                <tr key={c.id} className="hover:bg-muted/30 transition-colors">
                  {/* Title */}
                  <td className="px-5 py-3.5">
                    <p className="text-sm font-semibold text-foreground font-body">
                      {c.title}
                    </p>
                  </td>

                  {/* Category */}
                  <td className="px-5 py-3.5 text-sm text-muted-foreground font-body">
                    {c.category?.name || '—'}
                  </td>

                  {/* Format */}
                  <td className="px-5 py-3.5">
                    <div className="flex gap-1">
                      {c.supports_online && (
                        <span className="text-xs px-2 py-0.5 rounded-md bg-info/10 text-info font-mono">
                          {t.courses.online}
                        </span>
                      )}
                      {c.supports_offline && (
                        <span className="text-xs px-2 py-0.5 rounded-md bg-purple/10 text-purple font-mono">
                          {t.courses.offline}
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Enrollments */}
                  <td className="px-5 py-3.5 text-sm font-semibold text-foreground font-mono">
                    {c.active_enrollment_count}
                  </td>

                  {/* Status */}
                  <td className="px-5 py-3.5">
                    <StatusBadge status={c.status || 'draft'} />
                  </td>

                  {/* Actions */}
                  <td className="px-5 py-3.5">
                    <div className="flex gap-3">
                      <Link
                        href={`/admin/courses/${c.id}`}
                        className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                      >
                        {t.courses.edit}
                      </Link>
                      <button
                        onClick={() => handleDelete(c.id, c.title)}
                        disabled={deletingId === c.id}
                        className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono disabled:opacity-40"
                      >
                        {deletingId === c.id ? t.courses.deleting : t.courses.delete}
                      </button>
                    </div>
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
              {t.courses.pagination.previous}
            </button>
          )}
          <span className="text-sm text-muted-foreground font-mono px-4">
            {t.courses.pagination.page} {page} {t.courses.pagination.of} {totalPages}
          </span>
          {page < totalPages && (
            <button
              onClick={() => updateParam('page', String(page + 1))}
              className="btn-ghost text-sm"
            >
              {t.courses.pagination.next}
            </button>
          )}
        </div>
      )}
    </AdminLayout>
  );
}

export default function AdminCoursesPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <CoursesContent />
    </Suspense>
  );
}