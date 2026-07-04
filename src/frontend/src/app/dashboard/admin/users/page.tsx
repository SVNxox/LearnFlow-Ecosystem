'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { AdminUser } from '@/types/api';
import { StatusBadge } from '@/components/ui';
import { formatRelativeTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

const ROLE_TABS = ['all', 'student', 'mentor', 'staff', 'admin'] as const;

function UsersContent() {
  const { t } = useTranslation();
  const router = useRouter();
  const sp = useSearchParams();
  const role = sp.get('role') || '';
  const page = parseInt(sp.get('page') || '1', 10);

  const [users, setUsers] = useState<AdminUser[]>([]);
  const [count, setCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [searchInput, setSearchInput] = useState(sp.get('search') || '');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const updateParam = useCallback((key: string, value: string | null) => {
    const params = new URLSearchParams(sp.toString());
    if (value) params.set(key, value); else params.delete(key);
    params.delete('page');
    router.push(`/dashboard/admin/users?${params.toString()}`);
  }, [router, sp]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    adminApi.getUsers({ search: sp.get('search') || undefined, role: role || undefined, page })
      .then((data) => {
        if (!active) return;
        setUsers(data.results);
        setCount(data.count);
        setTotalPages(data.total_pages || 1);
      })
      .catch((err) => active && setError(handleApiError(err)))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [sp.toString(), role, page]);

  return (
    <AdminLayout roles={['admin']}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-foreground font-heading">
            {t.users.title} ({count})
          </h1>
          <p className="text-sm text-muted-foreground mt-1 font-body">
            {t.users.subtitle}
          </p>
        </div>
        <Link
          href="/dashboard/admin/users/create"
          className="btn-primary text-sm inline-flex items-center gap-2"
        >
          <span>+</span>
          {t.users.createUser}
        </Link>
      </div>

      {/* Role tabs */}
      <div className="filter-pills mb-4">
        {ROLE_TABS.map((r) => (
          <button
            key={r}
            onClick={() => updateParam('role', r === 'all' ? null : r)}
            className={`filter-pill ${
              (r === 'all' ? !role : role === r) ? 'filter-pill-active' : 'filter-pill-inactive'
            }`}
          >
            {t.users.roles[r]}
          </button>
        ))}
      </div>

      {/* Search */}
      <form onSubmit={(e) => { e.preventDefault(); updateParam('search', searchInput || null); }} className="mb-6">
        <div className="flex gap-2 max-w-md">
          <div className="relative flex-1">
            <input
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder={t.users.search}
              className="input pl-10"
            />
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              🔍
            </span>
            {searchInput && (
              <button
                type="button"
                onClick={() => {
                  setSearchInput('');
                  updateParam('search', null);
                }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                ✕
              </button>
            )}
          </div>
          <button type="submit" className="btn-primary px-6">
            {t.users.searchButton}
          </button>
        </div>
      </form>

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
                t.users.nameEmail,
                t.users.role,
                t.users.status,
                t.users.enrollments,
                t.users.lastLogin,
                t.users.actions,
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
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center">
                  <div className="text-3xl mb-3">👥</div>
                  <p className="text-sm text-muted-foreground font-body">
                    {t.users.noUsers}
                  </p>
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.id} className="hover:bg-muted/30 transition-colors">
                  {/* Name / Email */}
                  <td className="px-5 py-3.5">
                    <div>
                      <p className="text-sm font-medium text-foreground font-body">
                        {user.info?.first_name} {user.info?.last_name}
                      </p>
                      <p className="text-xs text-muted-foreground font-mono mt-0.5">
                        {user.email}
                      </p>
                    </div>
                  </td>

                  {/* Role */}
                  <td className="px-5 py-3.5">
                    <div className="flex flex-wrap gap-1">
                      {user.roles.map((r) => (
                        <StatusBadge key={r} status={r} />
                      ))}
                    </div>
                  </td>

                  {/* Status */}
                  <td className="px-5 py-3.5">
                    <StatusBadge
                      status={user.is_blocked ? 'blocked' : 'active'}
                    />
                  </td>

                  {/* Enrollments */}
                  <td className="px-5 py-3.5 text-sm font-semibold text-foreground font-mono">
                    {user.enrollment_count}
                  </td>

                  {/* Last Login */}
                  <td className="px-5 py-3.5 text-xs text-muted-foreground font-mono">
                    {user.last_login_at ? formatRelativeTime(user.last_login_at) : '—'}
                  </td>

                  {/* Actions */}
                  <td className="px-5 py-3.5">
                    <Link
                      href={`/dashboard/admin/users/${user.id}`}
                      className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                    >
                      {t.users.view}
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
              {t.users.pagination.previous}
            </button>
          )}
          <span className="text-sm text-muted-foreground font-mono px-4">
            {t.users.pagination.page} {page} {t.users.pagination.of} {totalPages}
          </span>
          {page < totalPages && (
            <button
              onClick={() => updateParam('page', String(page + 1))}
              className="btn-ghost text-sm"
            >
              {t.users.pagination.next}
            </button>
          )}
        </div>
      )}
    </AdminLayout>
  );
}

export default function UsersPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <UsersContent />
    </Suspense>
  );
}