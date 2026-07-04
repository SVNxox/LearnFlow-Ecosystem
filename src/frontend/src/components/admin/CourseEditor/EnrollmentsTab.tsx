'use client';

import { useState, useEffect } from 'react';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { AdminEnrollment } from '@/types/api';
import { StatusBadge } from '@/components/ui';
import { formatDate } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface EnrollmentsTabProps {
  courseId: string;
  courseTitle: string;
}

const STATUS_OPTIONS = [
  { value: 'all', labelKey: 'all' as const },
  { value: 'pending', labelKey: 'pending' as const },
  { value: 'active', labelKey: 'active' as const },
  { value: 'suspended', labelKey: 'suspended' as const },
  { value: 'dropped', labelKey: 'dropped' as const },
  { value: 'completed', labelKey: 'completed' as const },
];

const FORMAT_LABELS = {
  online: '🌐 Online',
  offline: '🏫 Offline',
  hybrid: '🔄 Hybrid',
};

export default function EnrollmentsTab({ courseId, courseTitle }: EnrollmentsTabProps) {
  const { t } = useTranslation();
  const [enrollments, setEnrollments] = useState<AdminEnrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [count, setCount] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchInput, setSearchInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const [showAddForm, setShowAddForm] = useState(false);
  const [addForm, setAddForm] = useState({
    user_email: '',
    delivery_format: 'online',
  });
  const [addingStudent, setAddingStudent] = useState(false);

  useEffect(() => {
    loadEnrollments();
  }, [courseId, page, statusFilter, searchQuery]);

  const loadEnrollments = async () => {
    setLoading(true);
    setError('');
    try {
      const params: any = {
        course_id: courseId,
        page,
      };

      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }

      const data = await adminApi.getAllEnrollments(params);
      setEnrollments(data.results || []);
      setCount(data.count || 0);
      setTotalPages(data.total_pages || Math.ceil((data.count || 0) / 20) || 1);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (enrollmentId: string) => {
    setUpdatingId(enrollmentId);
    setError('');
    setSuccess('');
    try {
      await adminApi.activateEnrollment(enrollmentId);
      setSuccess(t.enrollments.activateSuccess);
      setTimeout(() => setSuccess(''), 3000);
      await loadEnrollments();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setUpdatingId(null);
    }
  };

  const handleComplete = async (enrollmentId: string) => {
    if (!confirm(t.enrollments.completeConfirm)) return;

    setUpdatingId(enrollmentId);
    try {
      await adminApi.completeEnrollment(enrollmentId);
      setSuccess(t.enrollments.completeSuccess);
      setTimeout(() => setSuccess(''), 3000);
      await loadEnrollments();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setUpdatingId(null);
    }
  };

  const handleSuspend = async (enrollmentId: string) => {
    const reason = prompt(t.enrollments.suspendReason);
    if (!reason) return;

    setUpdatingId(enrollmentId);
    try {
      await adminApi.suspendEnrollment(enrollmentId, reason);
      setSuccess(t.enrollments.suspendSuccess);
      setTimeout(() => setSuccess(''), 3000);
      await loadEnrollments();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setUpdatingId(null);
    }
  };

  const handleDrop = async (enrollmentId: string, userName: string) => {
    const reason = prompt(`${t.enrollments.dropReason} "${userName}":`);
    if (!reason) return;

    setUpdatingId(enrollmentId);
    try {
      await adminApi.dropEnrollment(enrollmentId, reason);
      setSuccess(`${userName} ${t.enrollments.dropSuccess}`);
      setTimeout(() => setSuccess(''), 3000);
      await loadEnrollments();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setUpdatingId(null);
    }
  };

  const handleAddStudent = async () => {
    if (!addForm.user_email.trim()) {
      setError(t.enrollments.emailRequired);
      return;
    }

    setAddingStudent(true);
    setError('');
    try {
      const response = await fetch(`/api/v1/identity/users/?email=${encodeURIComponent(addForm.user_email)}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) throw new Error('User not found');

      const users = await response.json();
      if (!users.results || users.results.length === 0) {
        setError(t.enrollments.userNotFound);
        setAddingStudent(false);
        return;
      }

      const user = users.results[0];

      await adminApi.adminEnrollStudent({
        course_id: courseId,
        delivery_format: addForm.delivery_format,
        user_id: user.id,
      });

      setSuccess(`${addForm.user_email} ${t.enrollments.enrollSuccess}`);
      setTimeout(() => setSuccess(''), 3000);
      setShowAddForm(false);
      setAddForm({ user_email: '', delivery_format: 'online' });
      await loadEnrollments();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setAddingStudent(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    setSearchQuery(searchInput);
  };

  const stats = {
    total: count,
    active: enrollments.filter((e) => e.status === 'active').length,
    pending: enrollments.filter((e) => e.status === 'pending').length,
    completed: enrollments.filter((e) => e.status === 'completed').length,
  };

  return (
    <div className="space-y-4">
      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4">
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

      {/* Filters and search */}
      <div className="card p-4">
        <div className="flex gap-3 items-center mb-3">
          {/* Search */}
          <div className="flex-1 flex gap-2">
            <div className="relative flex-1">
              <input
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder={t.enrollments.search}
                className="input pl-10"
              />
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">🔍</span>
            </div>
            <button
              onClick={handleSearch}
              className="btn-primary px-6"
            >
              {t.enrollments.searchButton}
            </button>
            {searchQuery && (
              <button
                onClick={() => {
                  setSearchInput('');
                  setSearchQuery('');
                  setPage(1);
                }}
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                ✕
              </button>
            )}
          </div>

          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="input max-w-xs"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {t.enrollments.statuses[opt.labelKey]}
              </option>
            ))}
          </select>

          {/* Buttons */}
          <button
            onClick={loadEnrollments}
            className="btn-ghost px-3"
            title={t.enrollments.refresh}
          >
            ↻
          </button>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="btn-primary text-sm"
          >
            + {t.enrollments.enrollStudent}
          </button>
        </div>

        {/* Add student form */}
        {showAddForm && (
          <div className="bg-muted border border-border rounded-xl p-4 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.enrollments.studentEmail}
                </label>
                <input
                  type="email"
                  value={addForm.user_email}
                  onChange={(e) => setAddForm((f) => ({ ...f, user_email: e.target.value }))}
                  placeholder="student@example.com"
                  className="input"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.enrollments.deliveryFormat}
                </label>
                <select
                  value={addForm.delivery_format}
                  onChange={(e) => setAddForm((f) => ({ ...f, delivery_format: e.target.value }))}
                  className="input"
                >
                  <option value="online">{t.enrollments.formats.online}</option>
                  <option value="offline">{t.enrollments.formats.offline}</option>
                  <option value="hybrid">{t.enrollments.formats.hybrid}</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleAddStudent}
                disabled={addingStudent}
                className="btn-primary text-sm"
              >
                {addingStudent ? t.enrollments.enrolling : t.enrollments.enrollStudent}
              </button>
              <button
                onClick={() => {
                  setShowAddForm(false);
                  setAddForm({ user_email: '', delivery_format: 'online' });
                }}
                className="btn-ghost text-sm"
              >
                {t.enrollments.cancel}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm">
          {success}
        </div>
      )}

      {/* Table */}
      <div className="bg-card border border-border rounded-2xl overflow-hidden">
        <table className="min-w-full divide-y divide-border">
          <thead>
            <tr className="bg-muted/50">
              {[
                t.enrollments.student,
                t.enrollments.format,
                t.enrollments.status,
                t.enrollments.enrolled,
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
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  <td colSpan={5} className="px-5 py-4">
                    <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                  </td>
                </tr>
              ))
            ) : enrollments.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-12 text-center">
                  <div className="text-3xl mb-3">🎓</div>
                  <p className="text-sm text-muted-foreground font-body">
                    {searchQuery ? t.enrollments.noEnrollmentsFound : t.enrollments.noEnrollments}
                  </p>
                </td>
              </tr>
            ) : (
              enrollments.map((e) => (
                <tr key={e.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-5 py-3.5">
                    <div>
                      <p className="text-sm font-medium text-foreground font-body">
                        {e.user_name || '—'}
                      </p>
                      <p className="text-xs text-muted-foreground font-mono">{e.user_email}</p>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-sm text-foreground font-body">
                    {FORMAT_LABELS[e.delivery_format as keyof typeof FORMAT_LABELS] || e.delivery_format}
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={e.status} />
                  </td>
                  <td className="px-5 py-3.5 text-xs text-muted-foreground font-mono">
                    {e.enrolled_at ? formatDate(e.enrolled_at) : '—'}
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex gap-2">
                      {e.status === 'pending' && (
                        <button
                          onClick={() => handleActivate(e.id)}
                          disabled={updatingId === e.id}
                          className="text-xs text-success hover:text-success/80 font-semibold font-mono disabled:opacity-40"
                        >
                          {updatingId === e.id ? '...' : t.enrollments.activate}
                        </button>
                      )}
                      {e.status === 'active' && (
                        <>
                          <button
                            onClick={() => handleComplete(e.id)}
                            disabled={updatingId === e.id}
                            className="text-xs text-info hover:text-info/80 font-semibold font-mono disabled:opacity-40"
                          >
                            {updatingId === e.id ? '...' : t.enrollments.complete}
                          </button>
                          <button
                            onClick={() => handleSuspend(e.id)}
                            disabled={updatingId === e.id}
                            className="text-xs text-warning hover:text-warning/80 font-semibold font-mono disabled:opacity-40"
                          >
                            {updatingId === e.id ? '...' : t.enrollments.suspend}
                          </button>
                        </>
                      )}
                      {e.status !== 'completed' && e.status !== 'dropped' && (
                        <button
                          onClick={() => handleDrop(e.id, e.user_name || e.user_email)}
                          disabled={updatingId === e.id}
                          className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono disabled:opacity-40"
                        >
                          {updatingId === e.id ? '...' : t.enrollments.drop}
                        </button>
                      )}
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
        <div className="flex items-center justify-center gap-2">
          {page > 1 && (
            <button
              onClick={() => setPage(page - 1)}
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
              onClick={() => setPage(page + 1)}
              className="btn-ghost text-sm"
            >
              {t.enrollments.pagination.next}
            </button>
          )}
        </div>
      )}
    </div>
  );
}