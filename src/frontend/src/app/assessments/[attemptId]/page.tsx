'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api, handleApiError } from '@/lib/api';
import { AttemptDetail, AssessmentItemDetail } from '@/types/api';
import { Navbar, LoadingSpinner, ConfirmModal } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';

function useCountdown(expiresAt: string | null) {
  const [remaining, setRemaining] = useState<number | null>(null);

  useEffect(() => {
    if (!expiresAt) return;
    const tick = () => {
      const diff = new Date(expiresAt).getTime() - Date.now();
      setRemaining(Math.max(0, Math.floor(diff / 1000)));
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [expiresAt]);

  return remaining;
}

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function AssessmentAttemptPage() {
  const params = useParams<{ attemptId: string }>();
  const { t } = useTranslation();

  const [attempt, setAttempt] = useState<AttemptDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [confirmSubmit, setConfirmSubmit] = useState(false);
  const [submitting, setSubmitting] = useState(false);

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

  const remaining = useCountdown(attempt && !attempt.submitted_at ? attempt.expires_at : null);
  const isSubmitted = !!attempt?.submitted_at;

  const handleSave = async (item: AssessmentItemDetail, answer: Partial<AssessmentItemDetail>) => {
    if (!attempt) return;
    setSavingId(item.item_id);
    try {
      await api.assessment.submitResponse(attempt.attempt_id, {
        item_id: item.item_id,
        selected_option_ids: answer.selected_option_ids,
        text_response: answer.text_response,
        submitted_code: answer.submitted_code,
      });
      setSavedIds((prev) => new Set(prev).add(item.item_id));
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSavingId(null);
    }
  };

  const handleFinalize = async () => {
    if (!attempt) return;
    setSubmitting(true);
    try {
      const result = await api.assessment.finalizeAttempt(attempt.attempt_id);
      setAttempt(result);
      setConfirmSubmit(false);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner fullScreen message={t.assessment.loading} />;

  if (error && !attempt) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 py-16 text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <p className="text-destructive font-body">{error}</p>
        </div>
      </div>
    );
  }

  if (!attempt) return null;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Card */}
        <div className="card p-6 mb-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-foreground font-heading">
                {attempt.assessment_title}
              </h1>
              <p className="text-sm text-muted-foreground mt-1 font-body">
                {t.assessment.attempt} 
              </p>
            </div>
            {remaining !== null && !isSubmitted && (
              <div
                className={`text-sm font-semibold px-3 py-1.5 rounded-xl font-mono ${
                  remaining < 60
                    ? 'bg-destructive/10 text-destructive border border-destructive/30'
                    : 'bg-info/10 text-info border border-info/30'
                }`}
              >
                ⏱ {formatTime(remaining)}
              </div>
            )}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-6 font-body">
            {error}
          </div>
        )}

        {/* Content */}
        {isSubmitted ? (
          <ResultsView attempt={attempt} />
        ) : (
          <>
            <div className="space-y-5">
              {attempt.items
                .sort((a, b) => a.order - b.order)
                .map((item) => (
                  <ItemEditor
                    key={item.item_id}
                    item={item}
                    saving={savingId === item.item_id}
                    saved={savedIds.has(item.item_id)}
                    onSave={(answer) => handleSave(item, answer)}
                  />
                ))}
            </div>

            <div className="flex justify-end mt-8">
              <button
                onClick={() => setConfirmSubmit(true)}
                className="btn-primary"
              >
                🎯 {t.assessment.finalize}
              </button>
            </div>
          </>
        )}
      </div>

      <ConfirmModal
        open={confirmSubmit}
        title={t.assessment.finalizeConfirm}
        description={t.assessment.finalizeDesc}
        confirmLabel={t.assessment.finalizeButton}
        loading={submitting}
        onConfirm={handleFinalize}
        onCancel={() => setConfirmSubmit(false)}
      />
    </div>
  );
}

function ItemEditor({
  item,
  saving,
  saved,
  onSave,
}: {
  item: AssessmentItemDetail;
  saving: boolean;
  saved: boolean;
  onSave: (answer: Partial<AssessmentItemDetail>) => void;
}) {
  const { t } = useTranslation();
  const [selected, setSelected] = useState<string[]>(item.selected_option_ids || []);
  const [text, setText] = useState(item.text_response || '');
  const [code, setCode] = useState(item.submitted_code || item.starter_code || '');

  const toggleOption = (optionId: string) => {
    let next: string[];
    if (item.item_type === 'single_choice') {
      next = [optionId];
    } else {
      next = selected.includes(optionId) ? selected.filter((id) => id !== optionId) : [...selected, optionId];
    }
    setSelected(next);
    onSave({ selected_option_ids: next });
  };

  return (
    <div className="card p-6">
      {/* Status indicators */}
      <div className="flex items-center gap-2 mb-3 text-xs font-mono">
        <span className="bg-primary/10 text-primary px-2 py-0.5 rounded-full font-semibold">
          {item.max_points} {t.assessment.points}
        </span>
        {saving && (
          <span className="text-info flex items-center gap-1">
            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-info" />
            {t.assessment.saving}
          </span>
        )}
        {!saving && saved && (
          <span className="text-success">
            {t.assessment.saved}
          </span>
        )}
      </div>

      {/* Question */}
      <h3 className="font-semibold text-foreground mb-4 font-heading">
        {item.item_title}
      </h3>

      {/* Single/Multiple Choice */}
      {(item.item_type === 'single_choice' || item.item_type === 'multiple_choice') && (
        <div className="space-y-2.5">
          {item.options?.map((opt) => {
            const isSelected = selected.includes(opt.id);
            return (
              <button
                key={opt.id}
                onClick={() => toggleOption(opt.id)}
                className={`w-full text-left p-4 rounded-xl border-2 transition-all font-body ${
                  isSelected
                    ? 'border-primary bg-primary/10 text-foreground font-semibold'
                    : 'border-border hover:border-primary/50 hover:bg-muted/30 text-muted-foreground'
                }`}
              >
                {opt.text}
              </button>
            );
          })}
        </div>
      )}

      {/* Text Answer */}
      {(item.item_type === 'text_answer' || item.item_type === 'project' || item.item_type === 'interview') && (
        <div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onBlur={() => onSave({ text_response: text })}
            rows={6}
            placeholder={t.assessment.answerPlaceholder}
            className="input resize-none"
          />
          {item.min_word_count && (
            <p className="text-xs text-muted-foreground mt-1 font-body">
              {t.assessment.minWords.replace('{count}', String(item.min_word_count))}
            </p>
          )}
        </div>
      )}

      {/* Coding */}
      {item.item_type === 'coding' && (
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          onBlur={() => onSave({ submitted_code: code })}
          rows={12}
          spellCheck={false}
          className="input resize-none font-mono text-sm bg-background text-success"
        />
      )}
    </div>
  );
}

function ResultsView({ attempt }: { attempt: AttemptDetail }) {
  const { t } = useTranslation();
  const passed = attempt.passed;
  const mentorReview = attempt.grading_status === 'mentor_review';

  return (
    <div className="space-y-6">
      {/* Result Card */}
      <div
        className={`card p-6 text-center ${
          mentorReview
            ? 'border-info/30 bg-info/5'
            : passed
            ? 'border-success/30 bg-success/5'
            : 'border-warning/30 bg-warning/5'
        }`}
      >
        <div className="text-5xl mb-4">
          {mentorReview ? '🔍' : passed ? '🎉' : '😔'}
        </div>
        {mentorReview ? (
          <p className="text-info font-semibold font-body">
            {t.assessment.results.mentorReview}
          </p>
        ) : passed ? (
          <div>
            <p className="text-success font-bold text-xl font-heading">
              {t.assessment.results.passed}
            </p>
            <p className="text-3xl font-bold text-success mt-2 font-heading">
              {attempt.percentage}%
            </p>
          </div>
        ) : (
          <div>
            <p className="text-warning font-bold text-xl font-heading">
              {t.assessment.results.failed}
            </p>
            <p className="text-3xl font-bold text-warning mt-2 font-heading">
              {attempt.percentage}%
            </p>
            <p className="text-sm text-muted-foreground mt-2 font-body">
              {t.assessment.results.passingScore}: {attempt.passing_percentage}%
            </p>
          </div>
        )}
      </div>

      {/* Detailed Results */}
      {attempt.grading_status === 'finalized' && (
        <div className="space-y-4">
          {attempt.items
            .sort((a, b) => a.order - b.order)
            .map((item) => (
              <div key={item.item_id} className="card p-5">
                <div className="flex items-start justify-between gap-4 mb-2">
                  <h3 className="font-medium text-foreground font-body">
                    {item.item_title}
                  </h3>
                  <span className="text-sm font-semibold text-foreground font-mono flex-shrink-0">
                    {item.final_points ?? '—'} / {item.max_points}
                  </span>
                </div>
                {item.review_comment && (
                  <p className="text-sm text-muted-foreground font-body">
                    {item.review_comment}
                  </p>
                )}
              </div>
            ))}
        </div>
      )}

      {/* Back link */}
      <Link
        href="/my-courses"
        className="inline-block text-sm text-primary hover:text-primary/80 font-semibold font-body"
      >
        {t.assessment.results.backToCourses}
      </Link>
    </div>
  );
}