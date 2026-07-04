'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, handleApiError } from '@/lib/api';
import { Navbar, LoadingSpinner } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';
import { formatDate } from '@/utils/helpers';

interface SubmissionItem {
  id: string;
  status: string;
  final_score: string | null;
  created_at: string;
  first_submitted_at: string | null;
  last_submitted_at: string | null;
  reviewed_at: string | null;
  deadline: string | null;
  assignment: {
    id: string;
    title: string;
    type: string;
    max_score: string;
  };
  lesson: {
    id: string;
    title: string;
  } | null;
  module: {
    id: string;
    title: string;
  } | null;
  course: {
    id: string;
    title: string;
    slug: string;
  } | null;
  student: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  draft: { label: 'Loyiha', color: 'bg-muted text-muted-foreground border-border', icon: '📝' },
  submitted: { label: 'Topshirilgan', color: 'bg-info/10 text-info border-info/30', icon: '📤' },
  under_review: { label: 'Ko\'rib chiqilmoqda', color: 'bg-warning/10 text-warning border-warning/30', icon: '🔍' },
  changes_requested: { label: 'O\'zgartirishlar so\'ralgan', color: 'bg-warning/10 text-warning border-warning/30', icon: '🔄' },
  approved: { label: 'Tasdiqlangan', color: 'bg-success/10 text-success border-success/30', icon: '✅' },
  rejected: { label: 'Rad etilgan', color: 'bg-destructive/10 text-destructive border-destructive/30', icon: '❌' },
};

export default function AllSubmissionsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const { t } = useTranslation();

  const [submissions, setSubmissions] = useState<SubmissionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Filters
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '');
  const [courseFilter, setCourseFilter] = useState(searchParams.get('course_id') || '');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    // Проверка роли
    const userRoles = user.roles || [];
    const canView = userRoles.some((role: any) =>
      ['admin', 'staff', 'mentor'].includes(role.name || role)
    );

    if (!canView) {
      router.push('/');
      return;
    }

    loadSubmissions();
  }, [user, page, statusFilter, courseFilter]);

  const loadSubmissions = async () => {
    setLoading(true);
    setError('');

    try {
      const params: any = {
        page,
        page_size: pageSize,
      };

      if (statusFilter) params.status = statusFilter;
      if (courseFilter) params.course_id = courseFilter;

      const data = await api.submissions.getAllSubmissions(params);
      setSubmissions(data.results);
      setTotalCount(data.count);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const config = STATUS_CONFIG[status] || { label: status, color: 'bg-muted text-muted-foreground', icon: '📋' };
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold border ${config.color}`}>
        <span>{config.icon}</span>
        <span>{config.label}</span>
      </span>
    );
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-foreground font-heading mb-2">
            📝 Barcha topshiriqlar
          </h1>
          <p className="text-muted-foreground font-body">
            Jami: {totalCount} ta topshiriq
          </p>
        </div>

        {/* Filters */}
        <div className="card p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1);
                }}
                className="input"
              >
                <option value="">Barchasi</option>
                <option value="draft">📝 Loyiha</option>
                <option value="submitted">📤 Topshirilgan</option>
                <option value="under_review">🔍 Ko'rib chiqilmoqda</option>
                <option value="changes_requested">🔄 O'zgartirishlar so'ralgan</option>
                <option value="approved">✅ Tasdiqlangan</option>
                <option value="rejected">❌ Rad etilgan</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Kurs
              </label>
              <input
                type="text"
                value={courseFilter}
                onChange={(e) => {
                  setCourseFilter(e.target.value);
                  setPage(1);
                }}
                placeholder="Kurs ID"
                className="input"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={() => {
                  setStatusFilter('');
                  setCourseFilter('');
                  setPage(1);
                }}
                className="btn-ghost w-full"
              >
                🔄 Tozalash
              </button>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading ? (
          <div className="card p-12 text-center">
            <LoadingSpinner />
          </div>
        ) : submissions.length === 0 ? (
          <div className="card p-12 text-center">
            <div className="text-5xl mb-4">📭</div>
            <p className="text-muted-foreground font-body">
              Topshiriqlar topilmadi
            </p>
          </div>
        ) : (
          <>
            {/* Submissions List */}
            <div className="space-y-3">
              {submissions.map((submission) => (
                <Link
                  key={submission.id}
                  href={`/admin/submissions/${submission.id}`}
                  className="card p-4 hover:shadow-lg transition-shadow block"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        {getStatusBadge(submission.status)}
                        <span className="text-xs text-muted-foreground font-mono">
                          {submission.assignment.type}
                        </span>
                      </div>

                      <h3 className="font-semibold text-foreground font-heading mb-1 truncate">
                        {submission.assignment.title}
                      </h3>

                      <div className="flex items-center gap-3 text-xs text-muted-foreground font-body flex-wrap">
                        <span>👤 {submission.student.first_name} {submission.student.last_name}</span>
                        {submission.course && <span>📚 {submission.course.title}</span>}
                        {submission.module && <span>📖 {submission.module.title}</span>}
                        {submission.lesson && <span>📝 {submission.lesson.title}</span>}
                      </div>

                      <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono mt-2">
                        <span>📅 {formatDate(submission.created_at)}</span>
                        {submission.final_score && (
                          <span>🎯 {submission.final_score} / {submission.assignment.max_score}</span>
                        )}
                      </div>
                    </div>

                    <div className="flex-shrink-0">
                      <span className="text-primary font-semibold">→</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="btn-ghost"
                >
                  ← Oldingi
                </button>

                <span className="text-sm text-muted-foreground font-mono">
                  {page} / {totalPages}
                </span>

                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="btn-ghost"
                >
                  Keyingi →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}