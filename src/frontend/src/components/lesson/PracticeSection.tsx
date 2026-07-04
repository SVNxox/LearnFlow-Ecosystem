'use client';

import { useState } from 'react';
import { PracticeItemInfo } from '@/types/learning';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface PracticeSectionProps {
  items: PracticeItemInfo[];
}

export default function PracticeSection({ items }: PracticeSectionProps) {
  const { t } = useTranslation();
  const [openId, setOpenId] = useState<string | null>(items[0]?.id ?? null);

  if (!items.length) {
    return (
      <div className="card p-8 text-center">
        <div className="text-3xl mb-2">💪</div>
        <p className="text-sm text-muted-foreground font-body">
          {t.lesson.practice.noPractice}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((item, idx) => {
        const open = openId === item.id;
        return (
          <div
            key={item.id}
            className={`card overflow-hidden transition-all duration-200 ${
              open ? 'border-primary/30' : ''
            }`}
          >
            <button
              onClick={() => setOpenId(open ? null : item.id)}
              className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-muted/30 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0 font-mono"
                  style={{
                    backgroundColor: open ? 'var(--color-primary)' : 'var(--color-muted)',
                    color: open ? 'var(--color-primary-foreground)' : 'var(--color-muted-foreground)',
                  }}
                >
                  {idx + 1}
                </div>
                <span className="text-foreground font-semibold font-body">
                  {item.title}
                </span>
              </div>
              <span
                className={`text-lg transition-transform duration-200 ${
                  open ? 'rotate-180' : ''
                }`}
                style={{ color: 'var(--color-muted-foreground)' }}
              >
                ▾
              </span>
            </button>
            {open && (
              <div className="px-5 pb-5 pt-2 text-sm text-muted-foreground whitespace-pre-line font-body leading-relaxed border-t border-border">
                {item.instructions}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}