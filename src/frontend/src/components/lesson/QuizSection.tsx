'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { QuizInfo } from '@/types/learning';
import { api, handleApiError } from '@/lib/api';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface QuizSectionProps {
  quiz: QuizInfo;
  enrollmentId: string | null;
}

export default function QuizSection({ quiz, enrollmentId }: QuizSectionProps) {
  const router = useRouter();
  const { t } = useTranslation();
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStart = async () => {
    if (!enrollmentId) return;
    setStarting(true);
    setError(null);
    try {
      const attempt = await api.assessment.startAttempt({
        enrollment_id: enrollmentId,
        assessment_id: quiz.id,
      });
      router.push(`/assessments/${attempt.attempt_id}`);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="card p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
          style={{ backgroundColor: 'var(--color-info)' + '15' }}
        >
          📋
        </div>
        <h3 className="text-lg font-bold text-foreground font-heading">
          {quiz.title}
        </h3>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="bg-muted rounded-xl p-3">
          <p className="text-xs text-muted-foreground font-mono uppercase mb-1">
            {t.lesson.quiz.questions}
          </p>
          <p className="text-xl font-bold text-foreground font-heading">
            {quiz.questions.length}
          </p>
        </div>
        <div className="bg-muted rounded-xl p-3">
          <p className="text-xs text-muted-foreground font-mono uppercase mb-1">
            {t.lesson.quiz.passScore}
          </p>
          <p className="text-xl font-bold font-heading" style={{ color: 'var(--color-success)' }}>
            {quiz.pass_score}%
          </p>
        </div>
        {quiz.max_attempts != null && (
          <div className="bg-muted rounded-xl p-3">
            <p className="text-xs text-muted-foreground font-mono uppercase mb-1">
              {t.lesson.quiz.attempts}
            </p>
            <p className="text-xl font-bold text-foreground font-heading">
              {quiz.max_attempts}
            </p>
          </div>
        )}
        {quiz.time_limit_minutes != null && (
          <div className="bg-muted rounded-xl p-3">
            <p className="text-xs text-muted-foreground font-mono uppercase mb-1">
              {t.lesson.quiz.timeLimit}
            </p>
            <p className="text-xl font-bold text-foreground font-heading">
              {quiz.time_limit_minutes} <span className="text-sm font-normal">{t.lesson.quiz.minutes}</span>
            </p>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
          {error}
        </div>
      )}

      {/* Start button */}
      <button
        onClick={handleStart}
        disabled={starting || !enrollmentId}
        className="btn-primary text-sm w-full sm:w-auto"
      >
        {starting ? t.lesson.quiz.starting : `🚀 ${t.lesson.quiz.startQuiz}`}
      </button>
    </div>
  );
}