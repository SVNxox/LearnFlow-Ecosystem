export interface ConfirmModalProps {
  open: boolean;
  title: string;
  description: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
  confirmLabel?: string;
  danger?: boolean;
}

export function ConfirmModal({
  open, title, description, onConfirm, onCancel, loading, confirmLabel = 'Подтвердить', danger,
}: ConfirmModalProps) {
  if (!open) return null;
  return (
    <>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" onClick={onCancel} />
      <div className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md">
        <div className="bg-card border border-border rounded-2xl p-6 shadow-2xl mx-4">
          <h3 className="text-lg font-bold text-foreground mb-2 font-heading">{title}</h3>
          <p className="text-sm text-muted-foreground mb-6 font-body leading-relaxed">{description}</p>
          <div className="flex gap-3">
            <button onClick={onCancel} className="btn-ghost flex-1 text-sm">
              Отмена
            </button>
            <button
              onClick={onConfirm}
              disabled={loading}
              className={`flex-1 text-sm ${danger ? 'btn-danger' : 'btn-primary'}`}
            >
              {loading ? 'Загрузка...' : confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}