'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { api, handleApiError } from '@/lib/api';
import { AttemptDetail, AssessmentItemDetail } from '@/types/api';
import { LoadingSpinner } from '@/components/ui';
import { formatDateTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

function ManualReviewItem({ item, onSubmitted }: { item: AssessmentItemDetail; onSubmitted: () => void }) {
  const { t } = useTranslation();
  const [points, setPoints] = useState(item.mentor_points ?? item.auto_points ?? 0);
  const [comment, setComment] = useState(item.review_comment || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const alreadyGraded = item.is_graded;

  const handleSubmit = async () => {
    setSaving(true);
    setError('');
    try {
      await api.assessment.submitMentorReview(item.item_id, { points, comment });
      onSubmitted();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full capitalize font-mono">
          {item.item_type.replace('_', ' ')}
        </span>
        <span className="text-sm text-muted-foreground font-mono">
          {t.mentor.reviewAssessment.maxPoints}: {item.max_points} {t.mentor.reviewAssessment.points}
        </span>
      </div>

      {/* Question */}
      <h3 className="font-semibold text-foreground mb-4 font-heading">
        {item.item_title}
      </h3>

      {/* Response */}
      {item.text_response && (
        <div className="bg-muted border border-border rounded-xl p-4 text-sm text-foreground whitespace-pre-line mb-4 font-body">
          {item.text_response}
        </div>
      )}
      {item.submitted_code && (
        <pre className="bg-background border border-border rounded-xl p-4 text-sm overflow-x-auto mb-4 font-mono text-success">
          <code>{item.submitted_code}</code>
        </pre>
      )}

      {/* Graded or Form */}
      {alreadyGraded ? (
        <div className="flex items-center gap-2 text-sm text-success bg-success/10 border border-success/30 px-3 py-2 rounded-xl font-body">
          {t.mentor.reviewAssessment.gradedBadge}: {item.final_points} / {item.max_points}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <label className="text-sm text-muted-foreground font-body">
              {t.mentor.reviewAssessment.score}:
            </label>
            <input
              type="number"
              min={0}
              max={item.max_points}
              value={points}
              onChange={(e) => setPoints(Number(e.target.value))}
              className="input w-24"
            />
            <span className="text-sm text-muted-foreground font-mono">/ {item.max_points}</span>
          </div>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            placeholder={t.mentor.reviewAssessment.comment}
            className="input resize-none"
          />
          {error && <p className="text-sm text-destructive font-body">{error}</p>}
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="btn-primary"
          >
            {saving ? t.mentor.reviewAssessment.submitting : `✅ ${t.mentor.reviewAssessment.submitReview}`}
          </button>
        </div>
      )}
    </div>
  );
}

export default function MentorReviewAssessmentPage() {
  const params = useParams<{ attemptId: string }>();
  const { t } = useTranslation();

  const [attempt, setAttempt] = useState<AttemptDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.assessment.getAttempt(params.attemptId);
      setAttempt(data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.attemptId]);

  return (
    <DashboardLayout allowedRoles={['mentor']}>
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : error || !attempt ? (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
          {error || t.mentor.reviewAssessment.notFound}
        </div>
      ) : (
        <div className="max-w-3xl">
          {/* Back link */}
          <Link
            href="/dashboard/mentor/assessments"
            className="text-sm text-muted-foreground hover:text-foreground mb-4 inline-block font-body"
          >
            {t.mentor.reviewAssessment.backToQueue}
          </Link>

          {/* Header Card */}
          <div className="card p-6 mb-6">
            <h1 className="text-xl font-bold text-foreground font-heading">
              {attempt.assessment_title}
            </h1>
            <div className="flex flex-wrap gap-4 mt-2 text-sm text-muted-foreground font-body">
              <span>
                {t.mentor.reviewAssessment.attempt} 
              </span>
              <span>·</span>
              <span>
                {t.mentor.reviewAssessment.startedAt}: {formatDateTime(attempt.started_at)}
              </span>
              <span>·</span>
              <span>
                {t.mentor.reviewAssessment.graded}: {attempt.graded_items} / {attempt.total_items}
              </span>
            </div>
          </div>

          {/* Items */}
          <div className="space-y-5">
            {attempt.items
              .sort((a, b) => a.order - b.order)
              .map((item) => (
                <ManualReviewItem key={item.item_id} item={item} onSubmitted={load} />
              ))}
          </div>

          {/* All graded */}
          {attempt.graded_items >= attempt.total_items && (
            <div className="mt-6 bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm font-body">
              {t.mentor.reviewAssessment.allGraded}
            </div>
          )}
        </div>
      )}
    </DashboardLayout>
  );
}