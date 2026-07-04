'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
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
  assignment: { id: string; title: string; type: string; max_score: string };
  lesson: { id: string; title: string } | null;
  module: { id: string; title: string } | null;
  course: { id: string; title: string; slug: string } | null;
  student: { id: string; email: string; first_name: string; last_name: string };
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  draft: { label: 'Loyiha', color: 'bg-muted text-muted-foreground border-border', icon: '📝' },
  submitted: { label: 'Topshirilgan', color: 'bg-info/10 text-info border-info/30', icon: '📤' },
  under_review: { label: 'Ko\'rib chiqilmoqda', color: 'bg-warning/10 text-warning border-warning/30', icon: '🔍' },
  changes_requested: { label: 'O\'zgartirishlar', color: 'bg-warning/10 text-warning border-warning/30', icon: '🔄' },
  approved: { label: 'Tasdiqlangan', color: 'bg-success/10 text-success border-success/30', icon: '✅' },
  rejected: { label: 'Rad etilgan', color: 'bg-destructive/10 text-destructive border-destructive/30', icon: '❌' },
};

export default function AllSubmissionsPage() {
  const params = useParams<{ role: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const { t } = useTranslation();

  const role = params.role; // mentor, staff, или admin
  const basePath = `/${role}/submissions`;

  const [submissions, setSubmissions] = useState<SubmissionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    loadSubmissions();
  }, [user, page, statusFilter]);

  const loadSubmissions = async () => {
    setLoading(true);
    setError('');
    try {
      const params: any = { page, page_size: pageSize };
      if (statusFilter) params.status = statusFilter;
      const data = await api.submissions.getAllSubmissions(params);
      setSubmissions(data.results || []);
      setTotalCount(data.count || 0);
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
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-foreground font-heading mb-2">
            📝 Barcha topshiriqlar
          </h1>
          <p className="text-muted-foreground font-body">
            Jami: {totalCount} ta topshiriq
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2 mb-4">
          {[
            { value: '', label: 'Barchasi' },
            { value: 'submitted', label: '📤 Topshirilgan' },
            { value: 'under_review', label: '🔍 Ko\'rib chiqilmoqda' },
            { value: 'changes_requested', label: '🔄 O\'zgartirishlar' },
            { value: 'approved', label: '✅ Tasdiqlangan' },
            { value: 'rejected', label: '❌ Rad etilgan' },
          ].map((filter) => (
            <button
              key={filter.value}
              onClick={() => { setStatusFilter(filter.value); setPage(1); }}
              className={`text-xs px-3 py-1.5 rounded-full font-semibold transition-all ${
                statusFilter === filter.value
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {error && (
          <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="card p-12 text-center"><LoadingSpinner /></div>
        ) : submissions.length === 0 ? (
          <div className="card p-12 text-center">
            <div className="text-5xl mb-4">📭</div>
            <p className="text-muted-foreground font-body">Topshiriqlar topilmadi</p>
          </div>
        ) : (
          <>
            <div className="space-y-3">
              {submissions.map((submission) => (
                <Link
                  key={submission.id}
                  href={`${basePath}/${submission.id}`}
                  className="card p-4 hover:shadow-md transition-shadow block"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        {getStatusBadge(submission.status)}
                        <span className="text-xs text-muted-foreground font-mono">{submission.assignment.type}</span>
                      </div>
                      <h3 className="font-semibold text-foreground font-heading truncate mb-1">
                        {submission.assignment.title}
                      </h3>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground font-body flex-wrap">
                        <span>👤 {submission.student.first_name} {submission.student.last_name}</span>
                        {submission.course && <span>📚 {submission.course.title}</span>}
                        {submission.lesson && <span>📖 {submission.lesson.title}</span>}
                      </div>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono mt-1.5">
                        <span>📅 {formatDate(submission.created_at)}</span>
                        {submission.final_score && (
                          <span>🎯 {submission.final_score} / {submission.assignment.max_score}</span>
                        )}
                      </div>
                    </div>
                    <span className="text-primary font-semibold flex-shrink-0">→</span>
                  </div>
                </Link>
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-4">
                <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="btn-ghost text-sm">
                  ← Oldingi
                </button>
                <span className="text-sm text-muted-foreground font-mono">{page} / {totalPages}</span>
                <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="btn-ghost text-sm">
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