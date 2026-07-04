'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface EnrollModalProps {
  open: boolean;
  courseTitle: string;
  supportsOnline: boolean;
  supportsOffline: boolean;
  loading?: boolean;
  error?: string | null;
  onConfirm: (format: 'online' | 'offline') => void;
  onCancel: () => void;
}

export default function EnrollModal({
  open,
  courseTitle,
  supportsOnline,
  supportsOffline,
  loading,
  error,
  onConfirm,
  onCancel,
}: EnrollModalProps) {
  const { t } = useTranslation();
  const [format, setFormat] = useState<'online' | 'offline'>(supportsOnline ? 'online' : 'offline');

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onCancel} />
      <div className="relative bg-card border border-border rounded-2xl shadow-2xl max-w-md w-full p-6">
        <h3 className="text-lg font-bold text-foreground mb-1 font-heading">
          {t.enrollModal.title}
        </h3>
        <p className="text-sm text-muted-foreground mb-5 font-body">{courseTitle}</p>

        <div className="space-y-3 mb-6">
          {supportsOnline && (
            <button
              type="button"
              onClick={() => setFormat('online')}
              className={`w-full text-left p-4 border-2 rounded-xl transition-all ${
                format === 'online'
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50 hover:bg-muted'
              }`}
            >
              <div className="font-semibold text-foreground font-body">
                {t.enrollModal.onlineLabel}
              </div>
              <div className="text-sm text-muted-foreground mt-1 font-body">
                {t.enrollModal.onlineDesc}
              </div>
            </button>
          )}
          {supportsOffline && (
            <button
              type="button"
              onClick={() => setFormat('offline')}
              className={`w-full text-left p-4 border-2 rounded-xl transition-all ${
                format === 'offline'
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50 hover:bg-muted'
              }`}
            >
              <div className="font-semibold text-foreground font-body">
                {t.enrollModal.offlineLabel}
              </div>
              <div className="text-sm text-muted-foreground mt-1 font-body">
                {t.enrollModal.offlineDesc}
              </div>
            </button>
          )}
        </div>

        {error && (
          <div className="mb-4 bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3">
          <Button variant="ghost" onClick={onCancel} disabled={loading}>
            {t.enrollModal.cancel}
          </Button>
          <Button onClick={() => onConfirm(format)} loading={loading}>
            {t.enrollModal.confirm}
          </Button>
        </div>
      </div>
    </div>
  );
}