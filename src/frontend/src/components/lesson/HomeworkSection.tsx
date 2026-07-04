'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, handleApiError } from '@/lib/api';
import { Assignment, Submission } from '@/types/api';
import { StatusBadge } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface HomeworkSectionProps {
  lessonId: string;
  enrollmentId: string | null;
}

export default function HomeworkSection({ lessonId, enrollmentId }: HomeworkSectionProps) {
  const router = useRouter();
  const { t } = useTranslation();
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const a = await api.submissions.getAssignmentByLesson(lessonId);
        if (!active) return;
        setAssignment(a);

        if (a && enrollmentId) {
          const mine = await api.submissions.getMySubmissions(enrollmentId).catch(() => []);
          const existing = mine.find((s) => s.assignment_id === a.id) || null;
          if (active) setSubmission(existing);
        }
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => { active = false; };
  }, [lessonId, enrollmentId]);

  const handleStart = async () => {
    if (!assignment || !enrollmentId) return;
    setCreating(true);
    setError(null);
    try {
      const created = await api.submissions.createSubmission({
        assignment_id: assignment.id,
        enrollment_id: enrollmentId,
      });
      router.push(`/submissions/${created.id}/submit`);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
      </div>
    );
  }

  if (!assignment) {
    return (
      <div className="card p-8 text-center">
        <div className="text-3xl mb-2">📝</div>
        <p className="text-sm text-muted-foreground font-body">
          {t.lesson.homework.noAssignment}
        </p>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
            style={{ backgroundColor: 'var(--color-warning)' + '15' }}
          >
            📝
          </div>
          <h3 className="text-lg font-bold text-foreground font-heading">
            {assignment.title}
          </h3>
        </div>
        {submission && <StatusBadge status={submission.status} />}
      </div>

      <p className="text-foreground text-sm mb-4 whitespace-pre-line font-body leading-relaxed">
        {assignment.description}
      </p>

      <div className="flex items-center gap-2 mb-5">
        <span className="text-xs text-muted-foreground font-mono uppercase">
          {t.lesson.homework.maxScore}:
        </span>
        <span className="text-sm font-bold text-foreground font-mono">
          {assignment.max_score}
        </span>
      </div>

      {error && (
        <div className="mb-4 bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
          {error}
        </div>
      )}

      {submission ? (
        <button
          onClick={() => router.push(`/submissions/${submission.id}`)}
          className="btn-primary text-sm inline-flex items-center gap-2"
        >
          {t.lesson.homework.viewSubmission}
        </button>
      ) : (
        <button
          onClick={handleStart}
          disabled={creating || !enrollmentId}
          className="btn-primary text-sm"
        >
          {creating ? t.lesson.homework.loading : t.lesson.homework.startAssignment}
        </button>
      )}
    </div>
  );
}