export interface EmptyStateProps {
  icon?: React.ReactNode | string;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="text-center py-16 px-4">
      {icon && (
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-muted mb-5">
          {typeof icon === 'string' ? (
            <span className="text-3xl">{icon}</span>
          ) : (
            <span className="text-muted-foreground">{icon}</span>
          )}
        </div>
      )}
      <h3 className="text-base font-semibold text-foreground mb-2 font-heading">{title}</h3>
      {description && (
        <p className="text-sm text-muted-foreground mb-6 max-w-sm mx-auto font-body">{description}</p>
      )}
      {action && (
        <button onClick={action.onClick} className="btn-primary text-sm">
          {action.label}
        </button>
      )}
    </div>
  );
}