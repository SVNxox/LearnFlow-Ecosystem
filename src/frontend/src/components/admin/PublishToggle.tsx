'use client';

import { useState } from 'react';
import { adminApi, handleApiError, isNotImplemented } from '@/lib/admin-api';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface PublishToggleProps {
  type: 'course' | 'module' | 'lesson';
  id: string;
  isPublished: boolean;
  onChanged: () => void;
  onError?: (message: string) => void;
}

export default function PublishToggle({
  type,
  id,
  isPublished,
  onChanged,
  onError,
}: PublishToggleProps) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const toggle = async () => {
    setLoading(true);
    setFailed(false);
    setErrorMessage('');

    try {
      if (type === 'course') {
        isPublished ? await adminApi.unpublishCourse(id) : await adminApi.publishCourse(id);
      } else if (type === 'module') {
        isPublished ? await adminApi.unpublishModule(id) : await adminApi.publishModule(id);
      } else {
        isPublished ? await adminApi.unpublishLesson(id) : await adminApi.publishLesson(id);
      }
      onChanged();
    } catch (err) {
      console.error(`[PublishToggle] ${type} ${id}:`, err);
      console.error('[PublishToggle] Response data:', (err as any)?.response?.data);

      if (isNotImplemented(err)) {
        setFailed(true);
        setErrorMessage('Backend endpoint not implemented');
      } else {
        const message = handleApiError(err);
        setErrorMessage(message);

        if (onError) {
          onError(message);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative inline-block">
      <button
        onClick={toggle}
        disabled={loading}
        title={failed ? errorMessage : undefined}
        className={`text-xs font-semibold px-2.5 py-1 rounded-full transition-all disabled:opacity-50 font-mono ${
          failed
            ? 'bg-warning/10 text-warning border border-warning/30'
            : isPublished
            ? 'bg-success/10 text-success border border-success/30 hover:bg-success/20'
            : 'bg-muted text-muted-foreground border border-border hover:bg-muted/80'
        }`}
      >
        {loading ? '...' : failed ? `⚠️ ${t.common.error}` : isPublished ? `✓ ${t.common.published}` : t.common.draft}
      </button>

      {/* Error tooltip */}
      {errorMessage && !onError && (
        <div className="absolute top-full left-0 mt-1 z-10 min-w-[200px] max-w-[300px] bg-destructive/10 border border-destructive/30 rounded-xl p-2 shadow-lg">
          <p className="text-xs text-destructive break-words font-body">{errorMessage}</p>
          <button
            onClick={() => setErrorMessage('')}
            className="absolute top-1 right-1 text-destructive/70 hover:text-destructive"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}