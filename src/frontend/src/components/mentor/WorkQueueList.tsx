import Link from 'next/link';
import { PendingAssessmentReview, PendingSubmissionReview } from '@/types/api';
import { formatRelativeTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

function PriorityBadge({ submittedAt }: { submittedAt: string | null }) {
  const { t } = useTranslation();
  if (!submittedAt) return null;
  const hours = (Date.now() - new Date(submittedAt).getTime()) / (1000 * 60 * 60);
  if (hours > 48) {
    return (
      <span className="text-xs font-semibold text-destructive bg-destructive/10 border border-destructive/30 px-2 py-0.5 rounded-full font-mono">
        ⚠️ {t.workQueue.urgent}
      </span>
    );
  }
  if (hours > 24) {
    return (
      <span className="text-xs font-semibold text-warning bg-warning/10 border border-warning/30 px-2 py-0.5 rounded-full font-mono">
        🔥 {t.workQueue.high}
      </span>
    );
  }
  return null;
}

export function AssessmentQueueList({ items }: { items: PendingAssessmentReview[] }) {
  const { t } = useTranslation();

  if (items.length === 0) {
    return (
      <div className="card p-8 text-center">
        <div className="text-4xl mb-3">🎉</div>
        <p className="text-sm text-muted-foreground font-body">
          {t.workQueue.noAssessments}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <Link
          key={item.response_id}
          href={`/dashboard/mentor/assessments/${item.attempt_id}`}
          className="flex items-center justify-between gap-4 card p-4 hover:border-primary/30 hover:-translate-y-0.5 transition-all duration-200 group"
        >
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="text-xs font-mono text-muted-foreground">
                {item.user_id.slice(0, 8)}
              </span>
              <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full capitalize font-mono">
                {item.item_type.replace('_', ' ')}
              </span>
              <PriorityBadge submittedAt={item.submitted_at} />
            </div>
            <p className="font-semibold text-foreground truncate font-body group-hover:text-primary transition-colors">
              {item.assessment_title}
            </p>
            <p className="text-sm text-muted-foreground truncate font-body">
              {item.item_title}
            </p>
          </div>
          <span className="text-xs text-muted-foreground flex-shrink-0 font-mono">
            {item.submitted_at ? formatRelativeTime(item.submitted_at) : ''}
          </span>
        </Link>
      ))}
    </div>
  );
}

export function SubmissionQueueList({ items }: { items: PendingSubmissionReview[] }) {
  const { t } = useTranslation();

  if (items.length === 0) {
    return (
      <div className="card p-8 text-center">
        <div className="text-4xl mb-3">🎉</div>
        <p className="text-sm text-muted-foreground font-body">
          {t.workQueue.noSubmissions}
        </p>
      </div>
    );
  }

  const typeIcon: Record<string, string> = {
    github_repository: '🐙',
    file_upload: '📁',
    file: '📁',
    text_answer: '📝',
    external_link: '🔗',
  };

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <Link
          key={item.submission_id}
          href={`/dashboard/mentor/submissions/${item.submission_id}`}
          className="flex items-center justify-between gap-4 card p-4 hover:border-primary/30 hover:-translate-y-0.5 transition-all duration-200 group"
        >
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
              style={{ backgroundColor: 'var(--color-info)' + '15' }}
            >
              {typeIcon[item.submission_type] || '📄'}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span className="text-xs font-medium text-foreground font-body">
                  {item.student_name}
                </span>
                <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full font-mono">
                  {t.workQueue.revision}{item.revision_number}
                </span>
                <PriorityBadge submittedAt={item.submitted_at} />
              </div>
              <p className="font-semibold text-foreground truncate font-body group-hover:text-primary transition-colors">
                {item.assignment_title}
              </p>
            </div>
          </div>
          <span className="text-xs text-muted-foreground flex-shrink-0 font-mono">
            {formatRelativeTime(item.submitted_at)}
          </span>
        </Link>
      ))}
    </div>
  );
}