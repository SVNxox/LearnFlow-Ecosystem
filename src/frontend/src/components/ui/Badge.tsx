type BadgeVariant = 'primary' | 'success' | 'warning' | 'error' | 'muted' | 'purple';

export interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const badgeStyles: Record<BadgeVariant, { bg: string; text: string }> = {
  primary: { bg: 'rgba(129,140,248,0.12)', text: '
  success: { bg: 'rgba(52,211,153,0.12)',  text: '
  warning: { bg: 'rgba(251,191,36,0.12)',  text: '
  error:   { bg: 'rgba(248,113,113,0.12)', text: '
  purple:  { bg: 'rgba(167,139,250,0.12)', text: '
  muted:   { bg: 'rgba(107,107,138,0.15)', text: '
};

export function Badge({ variant = 'primary', children, className = '' }: BadgeProps) {
  const s = badgeStyles[variant];
  return (
    <span
      className={`status-badge ${className}`}
      style={{ backgroundColor: s.bg, color: s.text }}
    >
      {children}
    </span>
  );
}