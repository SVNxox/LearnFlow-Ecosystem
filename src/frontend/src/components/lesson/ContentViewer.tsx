'use client';

import { useEffect, useState } from 'react';
import { ContentItem } from '@/types/learning';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface ContentViewerProps {
  content: ContentItem;
  onViewed: () => void;
}

const TYPE_ICON: Record<string, string> = {
  video: '🎥',
  recording: '🎙️',
  text: '📝',
  code: '💻',
  pdf: '📄',
  slides: '📊',
  link: '🔗',
};

export default function ContentViewer({ content, onViewed }: ContentViewerProps) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      onViewed();
    }, 3000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content.id]);

  const handleCopy = async () => {
    if (!content.body) return;
    try {
      await navigator.clipboard.writeText(content.body);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // ignore
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
          style={{ backgroundColor: 'var(--color-primary)' + '15' }}
        >
          {TYPE_ICON[content.type] || '📄'}
        </div>
        <h2 className="text-lg font-bold text-foreground font-heading">{content.title}</h2>
      </div>

      {/* Video / Recording */}
      {(content.type === 'video' || content.type === 'recording') && (
        content.url ? (
          <video
            src={content.url}
            controls
            className="w-full rounded-2xl bg-background border border-border aspect-video"
          />
        ) : (
          <div className="card p-6 text-center">
            <div className="text-3xl mb-2">🎥</div>
            <p className="text-sm text-muted-foreground font-body">
              {t.lesson.content.videoNotFound}
            </p>
          </div>
        )
      )}

      {/* Text */}
      {content.type === 'text' && (
        <div className="card p-6">
          <p className="text-foreground whitespace-pre-line leading-relaxed font-body">
            {content.body}
          </p>
        </div>
      )}

      {/* Code */}
      {content.type === 'code' && (
        <div className="relative">
          <pre className="bg-background border border-border rounded-2xl p-5 overflow-x-auto text-sm text-success font-mono">
            <code>{content.body}</code>
          </pre>
          <button
            onClick={handleCopy}
            className="absolute top-3 right-3 btn-ghost text-xs"
          >
            {copied ? t.lesson.content.copied : t.lesson.content.copy}
          </button>
        </div>
      )}

      {/* PDF / Slides */}
      {(content.type === 'pdf' || content.type === 'slides') && (
        <div className="card p-8 text-center">
          <div className="text-5xl mb-4">
            {content.type === 'pdf' ? '📄' : '📊'}
          </div>
          <p className="text-muted-foreground mb-5 font-body">
            {t.lesson.content.pdfHint}
          </p>
          {content.url && (
            <a
              href={content.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={onViewed}
              className="btn-primary inline-flex items-center gap-2"
            >
              {t.lesson.content.open}
            </a>
          )}
        </div>
      )}

      {/* Link */}
      {content.type === 'link' && content.url && (
        <a
          href={content.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={onViewed}
          className="block card p-6 hover:border-primary/30 transition-all duration-200 group"
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">🔗</span>
            <div className="flex-1 min-w-0">
              <p className="text-primary font-mono break-all font-semibold group-hover:text-primary/80 transition-colors">
                {content.url}
              </p>
              <p className="text-sm text-muted-foreground mt-1 font-body">
                {t.lesson.content.openLink}
              </p>
            </div>
          </div>
        </a>
      )}
    </div>
  );
}