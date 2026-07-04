'use client';

import { useRef, useState } from 'react';

export interface SortableListProps<T extends { id: string }> {
  items: T[];
  onReorder: (newItems: T[]) => void;
  renderItem: (item: T, dragHandleProps: React.HTMLAttributes<HTMLSpanElement>) => React.ReactNode;
}

export default function SortableList<T extends { id: string }>({
  items,
  onReorder,
  renderItem,
}: SortableListProps<T>) {
  const [dragOverId, setDragOverId] = useState<string | null>(null);
  const dragIdRef = useRef<string | null>(null);

  const handleDragStart = (id: string) => {
    dragIdRef.current = id;
  };

  const handleDrop = (targetId: string) => {
    const sourceId = dragIdRef.current;
    if (!sourceId || sourceId === targetId) return;
    const sourceIdx = items.findIndex((i) => i.id === sourceId);
    const targetIdx = items.findIndex((i) => i.id === targetId);
    const next = [...items];
    const [moved] = next.splice(sourceIdx, 1);
    next.splice(targetIdx, 0, moved);
    onReorder(next);
    setDragOverId(null);
    dragIdRef.current = null;
  };

  return (
    <div className="space-y-2">
      {items.map((item) => {
        const dragHandleProps: React.HTMLAttributes<HTMLSpanElement> = {
          draggable: true,
          onDragStart: () => handleDragStart(item.id),
          onDragEnd: () => {
            dragIdRef.current = null;
            setDragOverId(null);
          },
          className: 'cursor-grab active:cursor-grabbing text-muted-foreground hover:text-foreground px-1 select-none transition-colors',
        };

        return (
          <div
            key={item.id}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOverId(item.id);
            }}
            onDrop={() => handleDrop(item.id)}
            onDragLeave={() => setDragOverId(null)}
            className={`rounded-xl border transition-all duration-200 ${
              dragOverId === item.id 
                ? 'border-primary/50 bg-primary/5 shadow-sm' 
                : 'border-border bg-card hover:border-primary/20'
            }`}
          >
            {renderItem(item, dragHandleProps)}
          </div>
        );
      })}
    </div>
  );
}