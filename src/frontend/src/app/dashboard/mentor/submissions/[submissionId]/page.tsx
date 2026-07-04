'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { api, handleApiError } from '@/lib/api';
import { SubmissionDetail } from '@/types/api';
import { LoadingSpinner } from '@/components/ui';
import { StatusBadge } from '@/components/ui';
import { formatDateTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

function RevisionPayloadView({ submissionType, payload }: { submissionType: string; payload: Record<string, unknown> }) {
  const { t } = useTranslation();
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    const fileId = payload.file_id as string | undefined;
    if (!fileId) return;
    setDownloading(true);
    try {
      const { download_url } = await api.submissions.getPresignedDownloadUrl(fileId);
      window.open(download_url, '_blank');
    } catch {
      // ignore
    } finally {
      setDownloading(false);
    }
  };

  if (submissionType === 'github_repository') {
    return (
      <a
        href={payload.github_url as string}
        target="_blank"
        rel="noopener noreferrer"
        className="text-primary hover:text-primary/80 break-all font-mono text-sm font-body"
      >
        🐙 {payload.github_url as string}
      </a>
    );
  }
  if (submissionType === 'file_upload') {
    return (
      <button
        onClick={handleDownload}
        disabled={downloading}
        className="text-primary hover:text-primary/80 disabled:opacity-50 font-body text-sm"
      >
        📁 {(payload.filename as string) || t.mentor.reviewSubmission.file} — {t.mentor.reviewSubmission.download}
      </button>
    );
  }
  if (submissionType === 'text_answer') {
    return (
      <p className="text-foreground whitespace-pre-line font-body">
        {(payload.text as string) || (payload.answer as string)}
      </p>
    );
  }
  if (submissionType === 'external_link') {
    return (
      <a
        href={payload.url as string}
        target="_blank"
        rel="noopener noreferrer"
        className="text-primary hover:text-primary/80 break-all font-mono text-sm font-body"
      >
        🔗 {payload.url as string}
      </a>
    );
  }
  return null;
}

export default function MentorReviewSubmissionPage() {
  const params = useParams<{ submissionId: string }>();
  const { t } = useTranslation();

  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [score, setScore] = useState(0);
  const [status, setStatus] = useState<'approved' | 'changes_requested' | 'rejected'>('approved');
  const [feedback, setFeedback] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let active = true;
    api.submissions
      .getSubmission(params.submissionId)
      .then((data) => {
        if (active) setSubmission(data);
      })
      .catch((err) => active && setError(handleApiError(err)))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [params.submissionId]);

  const latestRevision = submission?.revisions[submission.revisions.length - 1];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!submission || !latestRevision) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.submissions.submitReview({
        submission_id: submission.id,
        revision_id: latestRevision.id,
        status,
        score,
        feedback,
      });
      setDone(true);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <DashboardLayout allowedRoles={['mentor']}>
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : error && !submission ? (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
          {error}
        </div>
      ) : !submission || !latestRevision ? (
        <div className="card p-8 text-center">
          <div className="text-4xl mb-3">🔍</div>
          <p className="text-sm text-muted-foreground font-body">
            {t.mentor.reviewSubmission.notFound}
          </p>
        </div>
      ) : done ? (
        <div className="max-w-md">
          <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm mb-4 font-body">
            {t.mentor.reviewSubmission.submitted}
          </div>
          <Link
            href="/dashboard/mentor/submissions"
            className="text-sm text-primary hover:text-primary/80 font-semibold font-body"
          >
            {t.mentor.reviewSubmission.backToQueue}
          </Link>
        </div>
      ) : (
        <div className="max-w-2xl">
          {/* Back link */}
          <Link
            href="/dashboard/mentor/submissions"
            className="text-sm text-muted-foreground hover:text-foreground mb-4 inline-block font-body"
          >
            {t.mentor.reviewSubmission.backToQueue}
          </Link>

          {/* Assignment Card */}
          <div className="card p-6 mb-6">
            <div className="flex items-start justify-between gap-4 mb-3">
              <h1 className="text-lg font-bold text-foreground font-heading">
                {submission.assignment.title}
              </h1>
              <StatusBadge status={submission.status} />
            </div>
            <p className="text-sm text-muted-foreground whitespace-pre-line mb-4 font-body">
              {submission.assignment.description}
            </p>
            <p className="text-xs text-muted-foreground font-mono">
              {t.mentor.reviewSubmission.maxScore}: {submission.assignment.max_score}
            </p>
          </div>

          {/* Previous Versions */}
          {submission.revisions.length > 1 && (
            <div className="mb-6">
              <h2 className="text-sm font-semibold text-foreground mb-2 font-heading">
                {t.mentor.reviewSubmission.previousVersions}
              </h2>
              <div className="space-y-2">
                {submission.revisions.slice(0, -1).map((rev) => (
                  <div
                    key={rev.id}
                    className="bg-muted border border-border rounded-xl p-3 text-xs text-muted-foreground font-mono"
                  >
                    {t.mentor.reviewSubmission.version} 
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Current Version */}
          <div className="card p-6 mb-6">
            <h2 className="text-sm font-semibold text-foreground mb-3 font-heading">
              {t.mentor.reviewSubmission.currentVersion} (
            </h2>
            <RevisionPayloadView submissionType={latestRevision.submission_type} payload={latestRevision.payload} />
            {latestRevision.notes && (
              <p className="text-sm text-muted-foreground mt-3 font-body">{latestRevision.notes}</p>
            )}
          </div>

          {/* Review Form */}
          <form onSubmit={handleSubmit} className="card p-6 space-y-5">
            <h2 className="text-sm font-semibold text-foreground font-heading">
              {t.mentor.reviewSubmission.reviewTitle}
            </h2>

            {/* Score */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.mentor.reviewSubmission.score}
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min={0}
                  max={submission.assignment.max_score}
                  value={score}
                  onChange={(e) => setScore(Number(e.target.value))}
                  className="input w-32"
                />
                <span className="text-sm text-muted-foreground font-mono">
                  / {submission.assignment.max_score}
                </span>
              </div>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2 font-body">
                {t.mentor.reviewSubmission.status}
              </label>
              <div className="flex gap-4 flex-wrap">
                {([
                  { value: 'changes_requested', labelKey: 'changes_requested' as const, icon: '🔄' },
                  { value: 'approved', labelKey: 'approved' as const, icon: '✅' },
                  { value: 'rejected', labelKey: 'rejected' as const, icon: '❌' },
                ] as const).map((opt) => (
                  <label
                    key={opt.value}
                    className={`flex items-center gap-2 text-sm cursor-pointer px-3 py-2 rounded-xl border-2 transition-all font-body ${
                      status === opt.value
                        ? 'border-primary bg-primary/10 text-foreground font-semibold'
                        : 'border-border hover:border-primary/50 text-muted-foreground'
                    }`}
                  >
                    <input
                      type="radio"
                      name="status"
                      checked={status === opt.value}
                      onChange={() => setStatus(opt.value)}
                      className="sr-only"
                    />
                    <span>{opt.icon}</span>
                    <span>{t.mentor.reviewSubmission.statuses[opt.labelKey]}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Feedback */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.mentor.reviewSubmission.feedback}
              </label>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                rows={4}
                required
                placeholder={t.mentor.reviewSubmission.feedbackPlaceholder}
                className="input resize-none"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={submitting}
              className="btn-primary"
            >
              {submitting ? (
                <span className="inline-flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  {t.mentor.reviewSubmission.submitting}
                </span>
              ) : (
                `📤 ${t.mentor.reviewSubmission.submit}`
              )}
            </button>
          </form>
        </div>
      )}
    </DashboardLayout>
  );
}