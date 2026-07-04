import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/utils/helpers';

export interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'white';
}

const Spinner = forwardRef<HTMLDivElement, SpinnerProps>(
  ({ className, size = 'md', variant = 'primary', ...props }, ref) => {
    const sizes = {
      sm: 'h-4 w-4',
      md: 'h-8 w-8',
      lg: 'h-12 w-12',
      xl: 'h-16 w-16',
    };

    const variants = {
      primary: 'border-blue-600',
      white: 'border-white',
    };

    return (
      <div ref={ref} className={cn('flex justify-center items-center', className)} {...props}>
        <div
          className={cn(
            'animate-spin rounded-full border-b-2',
            sizes[size],
            variants[variant]
          )}
        />
      </div>
    );
  }
);

Spinner.displayName = 'Spinner';

export default Spinner;

// Fullscreen loading component
export const LoadingScreen = ({ message }: { message?: string }) => (
  <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
    <Spinner size="lg" />
    {message && <p className="mt-4 text-gray-600">{message}</p>}
  </div>
);
