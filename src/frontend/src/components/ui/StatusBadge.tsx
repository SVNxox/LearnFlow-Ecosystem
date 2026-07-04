interface StatusBadgeProps {
  status: string;
  className?: string;
}

const STATUS_MAP: Record<string, { label: string; color: string; bg: string }> = {
  // Enrollment statuses
  active:            { label: 'Активен',     color: '
  pending:           { label: 'Ожидает',     color: '
  completed:         { label: 'Завершён',    color: '
  dropped:           { label: 'Отчислен',    color: '
  suspended:         { label: 'Приостановл.', color: '
  // Submission statuses
  under_review:      { label: 'На проверке', color: '
  approved:          { label: 'Одобрено',    color: '
  changes_requested: { label: 'Исправить',   color: '
  rejected:          { label: 'Отклонено',   color: '
  // Assessment statuses
  passed:            { label: 'Сдан',        color: '
  failed:            { label: 'Не сдан',     color: '
  // Payment statuses
  paid:              { label: 'Оплачен',     color: '
  refunded:          { label: 'Возврат',     color: '
  // Progress statuses
  in_progress:       { label: 'В процессе', color: '
  not_started:       { label: 'Не начат',   color: '
  locked:            { label: 'Закрыт',     color: '
  // Certificate
  issued:            { label: 'Выдан',      color: '
  revoked:           { label: 'Отозван',    color: '
  // Course
  published:         { label: 'Опубликован', color: '
  draft:             { label: 'Черновик',   color: '
  archived:          { label: 'Архив',      color: '
};

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const s = STATUS_MAP[status] ?? {
    label: status,
    color: '
    bg: 'rgba(107,107,138,0.12)',
  };
  return (
    <span
      className={`status-badge ${className}`}
      style={{ backgroundColor: s.bg, color: s.color }}
    >
      {s.label}
    </span>
  );
}