'use client';

import { useState } from 'react';
import { handleApiError } from '@/lib/admin-api';
import apiClient from '@/lib/api-client';
import SortableList from '../SortableList';
import { useTranslation } from '@/lib/i18n/useTranslation';

const PRACTICE_TYPES = [
  { key: 'coding', labelKey: 'coding' as const },
  { key: 'multiple_choice', labelKey: 'multiple_choice' as const },
  { key: 'fill_blank', labelKey: 'fill_blank' as const },
  { key: 'matching', labelKey: 'matching' as const },
  { key: 'project', labelKey: 'project' as const },
];

const LANGUAGES = [
  'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'go', 'rust', 'sql', 'other'
];

interface PracticeItem {
  id: string;
  title: string;
  description: string;
  instructions: string;
  practice_type: string;
  starter_code: string;
  solution_code: string;
  language: string;
  hints: string[];
  max_score: number;
  time_limit_minutes: number | null;
  order: number;
  lesson_id: string;
}

interface PracticeForm {
  title: string;
  description: string;
  instructions: string;
  practice_type: string;
  starter_code: string;
  solution_code: string;
  language: string;
  hints_text: string;
  max_score: number;
  time_limit_minutes: string;
}

const emptyForm: PracticeForm = {
  title: '',
  description: '',
  instructions: '',
  practice_type: 'coding',
  starter_code: '',
  solution_code: '',
  language: 'python',
  hints_text: '',
  max_score: 10,
  time_limit_minutes: '',
};

export interface PracticeTabProps {
  lessonId: string;
  items: PracticeItem[];
  onRefresh: () => void;
}

export function PracticeTab({ lessonId, items, onRefresh }: PracticeTabProps) {
  const { t } = useTranslation();
  const [localItems, setLocalItems] = useState<PracticeItem[]>(items);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<PracticeForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const resetForm = () => {
    setForm(emptyForm);
    setShowForm(false);
    setEditingId(null);
    setError('');
  };

  const handleEditClick = (item: PracticeItem) => {
    setEditingId(item.id);
    setForm({
      title: item.title || '',
      description: item.description || '',
      instructions: item.instructions || '',
      practice_type: item.practice_type || 'coding',
      starter_code: item.starter_code || '',
      solution_code: item.solution_code || '',
      language: item.language || 'python',
      hints_text: Array.isArray(item.hints) ? item.hints.join('\n') : '',
      max_score: item.max_score || 10,
      time_limit_minutes: item.time_limit_minutes ? String(item.time_limit_minutes) : '',
    });
    setShowForm(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) {
      setError(t.practice.titleRequired);
      return;
    }

    setSaving(true);
    setError('');

    try {
      const hints = form.hints_text
        .split('\n')
        .map((h) => h.trim())
        .filter(Boolean);

      const payload = {
        title: form.title.trim(),
        description: form.description.trim() || undefined,
        instructions: form.instructions.trim() || undefined,
        practice_type: form.practice_type,
        starter_code: form.starter_code || undefined,
        solution_code: form.solution_code || undefined,
        language: form.language || undefined,
        hints: hints.length > 0 ? hints : undefined,
        max_score: form.max_score,
        time_limit_minutes: form.time_limit_minutes ? Number(form.time_limit_minutes) : undefined,
      };

      if (editingId) {
        await apiClient.patch(`/learning/lessons/${lessonId}/practice/${editingId}/`, payload);
      } else {
        await apiClient.post(`/learning/lessons/${lessonId}/practice/`, payload);
      }

      resetForm();
      onRefresh();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t.practice.deleteConfirm)) return;
    setDeletingId(id);
    try {
      await apiClient.delete(`/learning/lessons/${lessonId}/practice/${id}/`);
      setLocalItems((prev) => prev.filter((p) => p.id !== id));
      onRefresh();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setDeletingId(null);
    }
  };

  const handleReorder = async (reordered: PracticeItem[]) => {
    setLocalItems(reordered);
    try {
      await apiClient.post(`/learning/lessons/${lessonId}/practice/reorder/`, {
        practice_ids: reordered.map((p) => p.id),
      });
    } catch {
      setLocalItems(items);
    }
  };

  const TYPE_ICON: Record<string, string> = {
    coding: '💻',
    multiple_choice: '☑️',
    fill_blank: '📝',
    matching: '🔗',
    project: '🚀',
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}

      <div className="flex justify-between items-center">
        <h3 className="text-sm font-semibold text-foreground font-heading">
          {t.practice.items} ({localItems.length})
        </h3>
        <button
          onClick={() => { setShowForm(true); setEditingId(null); setForm(emptyForm); }}
          className="text-sm font-semibold text-primary hover:text-primary/80 font-body"
        >
          {t.practice.addItem}
        </button>
      </div>

      {showForm && (
        <div className="bg-muted border border-border rounded-xl p-4 space-y-3">
          <h4 className="text-sm font-semibold text-foreground font-heading">
            {editingId ? t.practice.editItem : t.practice.newItem}
          </h4>

          {/* Title + Type */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {t.practice.titleLabel} *
              </label>
              <input
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                className="input text-sm"
                placeholder={t.practice.placeholders.title}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {t.practice.type} *
              </label>
              <select
                value={form.practice_type}
                onChange={(e) => setForm((f) => ({ ...f, practice_type: e.target.value }))}
                className="input text-sm"
              >
                {PRACTICE_TYPES.map((type) => (
                  <option key={type.key} value={type.key}>
                    {t.practice.types[type.labelKey]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-medium text-foreground mb-1 font-body">
              {t.practice.description}
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={2}
              className="input text-sm resize-none"
              placeholder={t.practice.placeholders.description}
            />
          </div>

          {/* Instructions */}
          <div>
            <label className="block text-xs font-medium text-foreground mb-1 font-body">
              {t.practice.instructions}
            </label>
            <textarea
              value={form.instructions}
              onChange={(e) => setForm((f) => ({ ...f, instructions: e.target.value }))}
              rows={3}
              className="input text-sm resize-none"
              placeholder={t.practice.placeholders.instructions}
            />
          </div>

          {/* Coding-specific fields */}
          {form.practice_type === 'coding' && (
            <>
              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.practice.language}
                </label>
                <select
                  value={form.language}
                  onChange={(e) => setForm((f) => ({ ...f, language: e.target.value }))}
                  className="input text-sm"
                >
                  {LANGUAGES.map((l) => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.practice.starterCode}
                </label>
                <textarea
                  value={form.starter_code}
                  onChange={(e) => setForm((f) => ({ ...f, starter_code: e.target.value }))}
                  rows={4}
                  className="input text-sm font-mono bg-background text-success resize-none"
                  placeholder={t.practice.placeholders.starterCode}
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.practice.solutionCode}
                </label>
                <textarea
                  value={form.solution_code}
                  onChange={(e) => setForm((f) => ({ ...f, solution_code: e.target.value }))}
                  rows={4}
                  className="input text-sm font-mono bg-background text-success resize-none"
                  placeholder={t.practice.placeholders.solutionCode}
                />
              </div>
            </>
          )}

          {/* Hints */}
          <div>
            <label className="block text-xs font-medium text-foreground mb-1 font-body">
              {t.practice.hints}
            </label>
            <textarea
              value={form.hints_text}
              onChange={(e) => setForm((f) => ({ ...f, hints_text: e.target.value }))}
              rows={3}
              className="input text-sm resize-none"
              placeholder={t.practice.placeholders.hints}
            />
          </div>

          {/* Score + Time */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {t.practice.maxScore}
              </label>
              <input
                type="number"
                min="0"
                value={form.max_score}
                onChange={(e) => setForm((f) => ({ ...f, max_score: Number(e.target.value) }))}
                className="input text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {t.practice.timeLimit}
              </label>
              <input
                type="number"
                min="0"
                value={form.time_limit_minutes}
                onChange={(e) => setForm((f) => ({ ...f, time_limit_minutes: e.target.value }))}
                className="input text-sm"
                placeholder={t.practice.noLimit}
              />
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              onClick={handleSave}
              disabled={saving}
              className="btn-primary text-sm"
            >
              {saving ? t.practice.saving : editingId ? t.practice.update : t.practice.create}
            </button>
            <button
              onClick={resetForm}
              className="btn-ghost text-sm"
            >
              {t.practice.cancel}
            </button>
          </div>
        </div>
      )}

      {localItems.length === 0 && !showForm ? (
        <div className="text-center py-8">
          <div className="text-3xl mb-3">💪</div>
          <p className="text-sm text-muted-foreground font-body">{t.practice.noItems}</p>
        </div>
      ) : (
        <SortableList
          items={localItems}
          onReorder={handleReorder}
          renderItem={(item, dragProps) => (
            <div className="flex items-center gap-3 px-4 py-3">
              <span {...dragProps} className="text-muted-foreground cursor-grab">⠿</span>
              <span className="text-lg">{TYPE_ICON[item.practice_type] || '📋'}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground font-body">{item.title}</p>
                <p className="text-xs text-muted-foreground truncate font-mono">
                  {item.practice_type}
                  {item.language && ` · ${item.language}`}
                  {item.max_score ? ` · ${item.max_score} ${t.practice.pts}` : ''}
                  {item.time_limit_minutes ? ` · ${item.time_limit_minutes} ${t.practice.min}` : ''}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleEditClick(item)}
                  className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                >
                  {t.practice.edit}
                </button>
                <button
                  onClick={() => handleDelete(item.id)}
                  disabled={deletingId === item.id}
                  className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono disabled:opacity-40"
                >
                  {deletingId === item.id ? '...' : '×'}
                </button>
              </div>
            </div>
          )}
        />
      )}
    </div>
  );
}