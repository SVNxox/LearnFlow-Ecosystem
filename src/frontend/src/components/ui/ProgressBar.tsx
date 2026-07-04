export interface ProgressBarProps {
  value: number;          // 0-100
  color?: string;         // CSS color, default = var(--primary)
  size?: 'sm' | 'md';
  showLabel?: boolean;
  className?: string;
}

export function ProgressBar({
  value,
  color,
  size = 'sm',
  showLabel,
  className = '',
}: ProgressBarProps) {
  const h = size === 'sm' ? 'h-1.5' : 'h-2.5';
  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between mb-1">
          <span className="text-xs text-muted-foreground font-body">Прогресс</span>
          <span className="text-xs font-bold font-mono" style={{ color: color ?? 'var(--primary)' }}>
            {value}%
          </span>
        </div>
      )}
      <div className={`progress-track ${h}`}>
        <div
          className="progress-fill"
          style={{
            width: `${Math.min(100, Math.max(0, value))}%`,
            backgroundColor: color ?? 'var(--primary)',
          }}
        />
      </div>
    </div>
  );
}