'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, handleApiError } from '@/lib/api';
import { Navbar, LoadingSpinner } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';
import { formatDate } from '@/utils/helpers';

interface SubmissionDetail {
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
    description: string;
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
  revisions: Array<{
    id: string;
    revision_number: number;
    submission_type: string;
    payload: any;
    notes: string;
    submitted_at: string;
  }>;
  reviews: Array<{
    id: string;
    status: string;
    score: string;
    max_score: string;
    feedback: string;
    reviewer: {
      id: string;
      email: string;
      first_name: string;
      last_name: string;
    };
    reviewed_at: string;
  }>;
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  draft: { label: 'Loyiha', color: 'bg-muted text-muted-foreground border-border', icon: '📝' },
  submitted: { label: 'Topshirilgan', color: 'bg-info/10 text-info border-info/30', icon: '📤' },
  under_review: { label: 'Ko\'rib chiqilmoqda', color: 'bg-warning/10 text-warning border-warning/30', icon: '🔍' },
  changes_requested: { label: 'O\'zgartirishlar so\'ralgan', color: 'bg-warning/10 text-warning border-warning/30', icon: '🔄' },
  approved: { label: 'Tasdiqlangan', color: 'bg-success/10 text-success border-success/30', icon: '✅' },
  rejected: { label: 'Rad etilgan', color: 'bg-destructive/10 text-destructive border-destructive/30', icon: '❌' },
};

export default function SubmissionDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const { t } = useTranslation();

  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    loadSubmission();
  }, [params.id, user]);

  const loadSubmission = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await api.submissions.getSubmissionDetail(params.id);
      setSubmission(data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const config = STATUS_CONFIG[status] || { label: status, color: 'bg-muted text-muted-foreground', icon: '📋' };
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-semibold border ${config.color}`}>
        <span>{config.icon}</span>
        <span>{config.label}</span>
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <LoadingSpinner fullScreen />
      </div>
    );
  }

  if (error || !submission) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-16 text-center">
          <div className="text-5xl mb-4">📝</div>
          <p className="text-destructive mb-4 font-body">{error || 'Topshiriq topilmadi'}</p>
          <Link href="/admin/submissions" className="text-primary hover:text-primary/80 font-body">
            ← Barcha topshiriqlarga qaytish
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumbs */}
        <nav className="mb-4 text-sm text-muted-foreground font-body">
          <Link href="/admin/submissions" className="hover:text-foreground">
            Barcha topshiriqlar
          </Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">
        </nav>

        {/* Header */}
        <div className="card p-6 mb-6">
          <div className="flex items-start justify-between gap-4 mb-4">
            <div>
              <h1 className="text-2xl font-bold text-foreground font-heading mb-2">
                {submission.assignment.title}
              </h1>
              <div className="flex items-center gap-2">
                {getStatusBadge(submission.status)}
              </div>
            </div>
            {submission.final_score && (
              <div className="text-right">
                <p className="text-3xl font-bold text-primary font-heading">
                  {submission.final_score} / {submission.assignment.max_score}
                </p>
                <p className="text-xs text-muted-foreground font-mono">Ball</p>
              </div>
            )}
          </div>

          {/* Meta info */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">Talaba</p>
              <p className="text-foreground font-semibold font-body">
                {submission.student.first_name} {submission.student.last_name}
              </p>
              <p className="text-xs text-muted-foreground font-mono">{submission.student.email}</p>
            </div>
            {submission.course && (
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">Kurs</p>
                <p className="text-foreground font-semibold font-body">{submission.course.title}</p>
              </div>
            )}
            {submission.module && (
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">Module</p>
                <p className="text-foreground font-semibold font-body">{submission.module.title}</p>
              </div>
            )}
            {submission.lesson && (
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">Dars</p>
                <p className="text-foreground font-semibold font-body">{submission.lesson.title}</p>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4 text-xs text-muted-foreground font-mono mt-4 pt-4 border-t border-border">
            <span>📅 Yaratilgan: {formatDate(submission.created_at)}</span>
            {submission.first_submitted_at && (
              <span>📤 Topshirilgan: {formatDate(submission.first_submitted_at)}</span>
            )}
            {submission.deadline && (
              <span>⏰ Muddat: {formatDate(submission.deadline)}</span>
            )}
          </div>
        </div>

        {/* Assignment Info */}
        <div className="card p-6 mb-6">
          <h2 className="text-lg font-bold text-foreground font-heading mb-3">
            📝 Vazifa haqida
          </h2>
          {submission.assignment.description && (
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">Tavsif</p>
              <p className="text-foreground font-body whitespace-pre-line">
                {submission.assignment.description}
              </p>
            </div>
          )}
        </div>

        {/* Revisions */}
        <div className="card p-6 mb-6">
          <h2 className="text-lg font-bold text-foreground font-heading mb-4">
            📦 Topshiriq versiyalari ({submission.revisions.length})
          </h2>
          <div className="space-y-4">
            {submission.revisions.map((revision) => (
              <div key={revision.id} className="border border-border rounded-xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-foreground font-body">
                    Versiya 
                  </h3>
                  <span className="text-xs text-muted-foreground font-mono">
                    {formatDate(revision.submitted_at)}
                  </span>
                </div>

                {/* Payload */}
                {revision.submission_type === 'text_answer' && revision.payload?.text && (
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">Matn</p>
                    <div className="bg-muted rounded-lg p-3">
                      <p className="text-foreground font-body whitespace-pre-line">
                        {revision.payload.text}
                      </p>
                    </div>
                  </div>
                )}

                {revision.submission_type === 'github_repository' && (
                  <div className="space-y-2">
                    {revision.payload?.github_url && (
                      <div>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">GitHub</p>
                        <a
                          href={revision.payload.github_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:text-primary/80 font-body break-all"
                        >
                          {revision.payload.github_url}
                        </a>
                      </div>
                    )}
                    {revision.payload?.live_url && (
                      <div>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">Live URL</p>
                        <a
                          href={revision.payload.live_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:text-primary/80 font-body break-all"
                        >
                          {revision.payload.live_url}
                        </a>
                      </div>
                    )}
                  </div>
                )}

                {revision.submission_type === 'external_link' && revision.payload?.url && (
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">Havola</p>
                    <a
                      href={revision.payload.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:text-primary/80 font-body break-all"
                    >
                      {revision.payload.url}
                    </a>
                  </div>
                )}

                {revision.notes && (
                  <div className="mt-3">
                    <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">Izoh</p>
                    <p className="text-foreground font-body">{revision.notes}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Reviews History */}
        {submission.reviews.length > 0 && (
          <div className="card p-6">
            <h2 className="text-lg font-bold text-foreground font-heading mb-4">
              📝 Rievlar tarixi ({submission.reviews.length})
            </h2>
            <div className="space-y-4">
              {submission.reviews.map((review) => (
                <div key={review.id} className="border border-border rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getStatusBadge(review.status)}
                      <span className="text-sm font-semibold text-foreground font-body">
                        {review.reviewer.first_name} {review.reviewer.last_name}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-primary font-heading">{review.score} / {review.max_score}</p>
                      <p className="text-xs text-muted-foreground font-mono">
                        {formatDate(review.reviewed_at)}
                      </p>
                    </div>
                  </div>
                  {review.feedback && (
                    <p className="text-foreground font-body mt-2">{review.feedback}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}