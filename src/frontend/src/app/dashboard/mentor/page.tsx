'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { api, handleApiError } from '@/lib/api';
import { PendingAssessmentReview } from '@/types/api';
import { LoadingSpinner } from '@/components/ui';
import { AssessmentQueueList } from '@/components/mentor/WorkQueueList';
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

export default function MentorDashboardPage() {
  const { t } = useTranslation();
  const [assessments, setAssessments] = useState<PendingAssessmentReview[]>([]);
  const [submissions, setSubmissions] = useState<SubmissionItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'assessments' | 'submissions'>('submissions');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [assessmentRes, submissionRes] = await Promise.all([
          api.assessment.getPendingReviews().catch(() => ({ items: [] })),
          api.submissions.getAllSubmissions({
            page,
            page_size: pageSize,
            status: statusFilter || undefined,
          }),
        ]);
        if (!active) return;
        setAssessments(assessmentRes.items || []);
        setSubmissions(submissionRes.results || []);
        setTotalCount(submissionRes.count || 0);
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => { active = false; };
  }, [page, statusFilter]);

  const getStatusBadge = (status: string) => {
    const config = STATUS_CONFIG[status] || { label: status, color: 'bg-muted text-muted-foreground', icon: '📋' };
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${config.color}`}>
        {config.icon} {config.label}
      </span>
    );
  };

  // Статистика по статусам
  const pendingCount = submissions.filter(s => ['submitted', 'under_review'].includes(s.status)).length;
  const changesCount = submissions.filter(s => s.status === 'changes_requested').length;
  const approvedCount = submissions.filter(s => s.status === 'approved').length;

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <DashboardLayout allowedRoles={['mentor', 'admin', 'staff']}>
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
          {error}
        </div>
      ) : (
        <div className="space-y-8">
          {/* Header */}
          <div>
            <h1 className="mt-10 text-2xl font-bold text-foreground font-heading">
              {t.mentor.dashboard.title}
            </h1>
            <p className="text-sm text-muted-foreground mt-1 font-body">
              {t.mentor.dashboard.subtitle}
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Link
              href="
              onClick={(e) => { e.preventDefault(); setStatusFilter(''); setTab('submissions'); setPage(1); }}
              className="stat-card hover:border-primary/30 transition-all duration-200"
            >
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl mb-3" style={{ backgroundColor: 'var(--color-info-bg)' }}>
                📝
              </div>
              <p className="stat-value">{totalCount}</p>
              <p className="stat-label mt-1 uppercase tracking-wider">Jami</p>
            </Link>

            <Link
              href="
              onClick={(e) => { e.preventDefault(); setStatusFilter('submitted'); setTab('submissions'); setPage(1); }}
              className="stat-card hover:border-primary/30 transition-all duration-200"
            >
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl mb-3" style={{ backgroundColor: 'var(--color-warning-bg)' }}>
                ⏳
              </div>
              <p className="stat-value" style={{ color: 'var(--color-warning)' }}>{pendingCount}</p>
              <p className="stat-label mt-1 uppercase tracking-wider">Kutilmoqda</p>
            </Link>

            <Link
              href="
              onClick={(e) => { e.preventDefault(); setStatusFilter('changes_requested'); setTab('submissions'); setPage(1); }}
              className="stat-card hover:border-primary/30 transition-all duration-200"
            >
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl mb-3" style={{ backgroundColor: 'var(--color-warning-bg)' }}>
                🔄
              </div>
              <p className="stat-value" style={{ color: 'var(--color-warning)' }}>{changesCount}</p>
              <p className="stat-label mt-1 uppercase tracking-wider">O'zgartirishlar</p>
            </Link>

            <Link
              href="
              onClick={(e) => { e.preventDefault(); setStatusFilter('approved'); setTab('submissions'); setPage(1); }}
              className="stat-card hover:border-primary/30 transition-all duration-200"
            >
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl mb-3" style={{ backgroundColor: 'var(--color-success-bg, rgba(34,197,94,0.1))' }}>
                ✅
              </div>
              <p className="stat-value" style={{ color: 'var(--color-success)' }}>{approvedCount}</p>
              <p className="stat-label mt-1 uppercase tracking-wider">Tasdiqlangan</p>
            </Link>
          </div>

          {/* Tabs */}
          <div>
            <div className="filter-pills mb-4">
              <button
                onClick={() => setTab('submissions')}
                className={`filter-pill ${tab === 'submissions' ? 'filter-pill-active' : 'filter-pill-inactive'}`}
              >
                📝 Topshiriqlar ({totalCount})
              </button>
              <button
                onClick={() => setTab('assessments')}
                className={`filter-pill ${tab === 'assessments' ? 'filter-pill-active' : 'filter-pill-inactive'}`}
              >
                📋 Baholashlar ({assessments.length})
              </button>
            </div>

            {tab === 'submissions' ? (
              <div className="space-y-4">
                {/* Status Filter */}
                <div className="flex flex-wrap gap-2">
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

                {/* Submissions List */}
                {submissions.length === 0 ? (
                  <div className="card p-12 text-center">
                    <div className="text-4xl mb-3">📭</div>
                    <p className="text-muted-foreground font-body">Topshiriqlar topilmadi</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {submissions.map((submission) => (
                      <Link
                        key={submission.id}
                        href={`/mentor/submissions/${submission.id}`}
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
                              {submission.deadline && (
                                <span>⏰ Muddat: {formatDate(submission.deadline)}</span>
                              )}
                            </div>
                          </div>
                          <span className="text-primary font-semibold flex-shrink-0">→</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-2 mt-4">
                    <button
                      onClick={() => setPage(Math.max(1, page - 1))}
                      disabled={page === 1}
                      className="btn-ghost text-sm"
                    >
                      ← Oldingi
                    </button>
                    <span className="text-sm text-muted-foreground font-mono">{page} / {totalPages}</span>
                    <button
                      onClick={() => setPage(Math.min(totalPages, page + 1))}
                      disabled={page === totalPages}
                      className="btn-ghost text-sm"
                    >
                      Keyingi →
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <AssessmentQueueList items={assessments} />
            )}
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}