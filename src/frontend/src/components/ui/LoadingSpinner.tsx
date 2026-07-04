interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const spinnerSize = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' };

export function LoadingSpinner({ size = 'md', className = '' }: SpinnerProps) {
  return (
    <div className={`animate-spin rounded-full border-2 border-muted border-t-primary ${spinnerSize[size]} ${className}`} />
  );
}

export function LoadingPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mx-auto mb-4" />
        <p className="text-sm text-muted-foreground font-body">Загрузка...</p>
      </div>
    </div>
  );
}