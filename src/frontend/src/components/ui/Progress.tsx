import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/utils/helpers';

export interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value: number; // 0-100
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

const Progress = forwardRef<HTMLDivElement, ProgressProps>(
  (
    {
      className,
      value,
      showLabel = false,
      size = 'md',
      variant = 'default',
      ...props
    },
    ref
  ) => {
    const clampedValue = Math.min(100, Math.max(0, value));

    const sizes = {
      sm: 'h-1.5',
      md: 'h-2.5',
      lg: 'h-4',
    };

    const variants = {
      default: 'bg-blue-600',
      success: 'bg-green-600',
      warning: 'bg-yellow-600',
      danger: 'bg-red-600',
    };

    return (
      <div ref={ref} className={cn('w-full', className)} {...props}>
        {showLabel && (
          <div className="flex justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm font-medium text-gray-700">
              {Math.round(clampedValue)}%
            </span>
          </div>
        )}
        <div className={cn('w-full bg-gray-200 rounded-full overflow-hidden', sizes[size])}>
          <div
            className={cn('h-full transition-all duration-300 rounded-full', variants[variant])}
            style={{ width: `${clampedValue}%` }}
          />
        </div>
      </div>
    );
  }
);

Progress.displayName = 'Progress';

export default Progress;
