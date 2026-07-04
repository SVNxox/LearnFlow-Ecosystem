'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, handleApiError } from '@/lib/api';
import { SubmissionDetail } from '@/types/api';
import { Navbar, LoadingSpinner, StatusBadge } from '@/components/ui';
import { formatDateTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

function RevisionPayload({ submissionType, payload }: { submissionType: string; payload: Record<string, unknown> }) {
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
      <div className="space-y-2">
        <a
          href={payload.github_url as string}
          target="_blank"
          rel="noopener noreferrer"
          className="block bg-muted border border-border rounded-xl p-3 text-sm text-primary hover:text-primary/80 transition-colors break-all font-mono"
        >
          🐙 {payload.github_url as string}
        </a>
        {payload.live_url && (
          <a
            href={payload.live_url as string}
            target="_blank"
            rel="noopener noreferrer"
            className="block bg-muted border border-border rounded-xl p-3 text-sm text-primary hover:text-primary/80 transition-colors break-all font-mono"
          >
            🔗 {payload.live_url as string}
          </a>
        )}
      </div>
    );
  }

  if (submissionType === 'file_upload') {
    return (
      <button
        onClick={handleDownload}
        disabled={downloading}
        className="bg-muted border border-border rounded-xl p-3 text-sm text-primary hover:text-primary/80 transition-colors flex items-center gap-2 disabled:opacity-50 font-body"
      >
        📁 {(payload.filename as string) || t.submissionDetail.file}{' '}
        {downloading ? `(${t.submissionDetail.downloading})` : `— ${t.submissionDetail.download}`}
      </button>
    );
  }

  if (submissionType === 'text_answer') {
    return (
      <div className="bg-muted border border-border rounded-xl p-4 text-sm text-foreground whitespace-pre-line font-body">
        {(payload.text as string) || (payload.answer as string)}
      </div>
    );
  }

  if (submissionType === 'external_link') {
    return (
      <a
        href={payload.url as string}
        target="_blank"
        rel="noopener noreferrer"
        className="block bg-muted border border-border rounded-xl p-3 text-sm text-primary hover:text-primary/80 transition-colors break-all font-mono"
      >
        🔗 {payload.url as string}
      </a>
    );
  }

  return null;
}

export default function SubmissionDetailPage() {
  const params = useParams<{ submissionId: string }>();
  const router = useRouter();
  const { t } = useTranslation();

  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.submissions.getSubmission(params.submissionId);
        if (active) setSubmission(data);
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => { active = false; };
  }, [params.submissionId]);

  if (loading) return <LoadingSpinner fullScreen />;

  if (error || !submission) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 py-16 text-center">
          <div className="text-5xl mb-4">🔍</div>
          <p className="text-destructive font-body">{error || t.submissionDetail.notFound}</p>
        </div>
      </div>
    );
  }

  const latestRevision = submission.revisions[submission.revisions.length - 1];
  const canResubmit = submission.status === 'changes_requested' || submission.status === 'draft';

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Card */}
        <div className="card p-6 mb-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h1 className="text-xl font-bold text-foreground font-heading">
                {submission.assignment.title}
              </h1>
              <p className="text-sm text-muted-foreground mt-1 whitespace-pre-line font-body">
                {submission.assignment.description}
              </p>
            </div>
            <StatusBadge status={submission.status} />
          </div>

          {submission.final_score != null && (
            <div className="flex items-center gap-2 mt-4">
              <span className="text-sm text-muted-foreground font-body">
                {t.submissionDetail.score}:
              </span>
              <span className="text-lg font-bold text-foreground font-heading">
                {submission.final_score}
              </span>
              <span className="text-sm text-muted-foreground font-body">
                / {submission.assignment.max_score}
              </span>
            </div>
          )}

          {canResubmit && (
            <button
              onClick={() => router.push(`/submissions/${submission.id}/submit`)}
              className="btn-primary mt-4"
            >
              📝 {submission.revisions.length > 0 ? t.submissionDetail.resubmit : t.submissionDetail.submit}
            </button>
          )}
        </div>

        {/* Reviews */}
        {submission.reviews.length > 0 && (
          <div className="space-y-3 mb-6">
            {submission.reviews
              .slice()
              .reverse()
              .map((review) => (
                <div
                  key={review.id}
                  className={`card p-5 ${
                    review.status === 'approved'
                      ? 'border-success/30 bg-success/5'
                      : review.status === 'rejected'
                      ? 'border-destructive/30 bg-destructive/5'
                      : 'border-warning/30 bg-warning/5'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <StatusBadge status={review.status} />
                    <span className="text-sm font-semibold text-foreground font-mono">
                      {review.score} / {review.max_score}
                    </span>
                  </div>
                  <p className="text-sm text-foreground whitespace-pre-line font-body">
                    {review.feedback}
                  </p>
                  <p className="text-xs text-muted-foreground mt-3 font-mono">
                    {formatDateTime(review.reviewed_at)}
                  </p>
                </div>
              ))}
          </div>
        )}

        {/* Submission History */}
        <h2 className="text-sm font-semibold text-foreground mb-3 font-heading">
          {t.submissionDetail.submissionHistory}
        </h2>
        <div className="space-y-4">
          {submission.revisions.length === 0 && (
            <div className="card p-8 text-center">
              <div className="text-4xl mb-3">📭</div>
              <p className="text-sm text-muted-foreground font-body">
                {t.submissionDetail.noSubmissions}
              </p>
            </div>
          )}
          {submission.revisions
            .slice()
            .reverse()
            .map((rev) => (
              <div key={rev.id} className="card p-5">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-semibold text-foreground font-body">
                    {t.submissionDetail.version} 
                  </span>
                  <span className="text-xs text-muted-foreground font-mono">
                    {formatDateTime(rev.submitted_at)}
                  </span>
                </div>
                <RevisionPayload submissionType={rev.submission_type} payload={rev.payload} />
                {rev.notes && (
                  <p className="text-sm text-muted-foreground mt-3 font-body">{rev.notes}</p>
                )}
              </div>
            ))}
        </div>

        {!latestRevision && (
          <p className="text-xs text-muted-foreground mt-4 font-mono">
            {t.submissionDetail.submissionId}: {submission.id}
          </p>
        )}
      </div>
    </div>
  );
}