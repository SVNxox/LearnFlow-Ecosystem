'use client';

import { useState } from 'react';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { ContentItem, ContentItemType } from '@/types/learning';
import SortableList from '../SortableList';
import { ConfirmModal } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';
import ContentUploader from './ContentUploader';
import DurationInput from '../DurationInput';

export interface ContentTabProps {
  lessonId: string;
  items: ContentItem[];
  onRefresh: () => void;
}

const TYPE_LABELS: Record<ContentItemType, { label: string; icon: string }> = {
  video: { label: 'Video', icon: '🎥' },
  recording: { label: 'Ovoz yozuvi', icon: '🎙️' },
  text: { label: 'Matn', icon: '📝' },
  code: { label: 'Kod', icon: '💻' },
  pdf: { label: 'PDF', icon: '📄' },
  slides: { label: 'Slaydlar', icon: '📊' },
  link: { label: 'Havola', icon: '🔗' },
};

// ✅ Типы, для которых нужна длительность
const TYPES_WITH_DURATION: ContentItemType[] = ['video', 'recording'];

// ✅ Типы, для которых нужна загрузка файла
const TYPES_WITH_UPLOAD: ContentItemType[] = ['video', 'recording', 'pdf', 'slides'];

// ✅ Accept для разных типов
const ACCEPT_MAP: Record<string, { accept: string; label: string }> = {
  video: { accept: 'video/*', label: 'Video' },
  recording: { accept: 'audio/*', label: 'Audio' },
  pdf: { accept: '.pdf,application/pdf', label: 'PDF' },
  slides: { accept: '.ppt,.pptx,.odp,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation', label: 'Slaydlar' },
};

export default function ContentTab({ lessonId, items, onRefresh }: ContentTabProps) {
  const { t } = useTranslation();
  const [adding, setAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const emptyForm = {
    type: 'text' as ContentItemType,
    title: '',
    description: '',
    url: '',
    body: '',
    duration_seconds: null as number | null,
    file_size_bytes: null as number | null,
    metadata: {} as Record<string, any>,
    is_required: false,
    is_downloadable: false,
    order: items.length + 1,
  };

  const [form, setForm] = useState(emptyForm);

  const showSuccess = (msg: string) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(''), 3000);
  };

  const resetForm = () => {
    setForm(emptyForm);
    setAdding(false);
    setEditingId(null);
    setError('');
  };

  const handleSave = async () => {
    if (!form.title.trim()) {
      setError('Sarlavha kiritilishi shart');
      return;
    }

    setSaving(true);
    setError('');

    try {
      const payload = {
        type: form.type,
        title: form.title.trim(),
        description: form.description.trim(),
        url: form.url.trim(),
        body: form.body,
        duration_seconds: TYPES_WITH_DURATION.includes(form.type) ? form.duration_seconds : null,
        file_size_bytes: form.file_size_bytes,
        metadata: form.metadata,
        is_required: form.is_required,
        is_downloadable: form.is_downloadable,
        order: form.order,
      };

      if (editingId) {
        await adminApi.updateLessonContent(lessonId, editingId, payload);
        showSuccess('✅ Kontent yangilandi');
      } else {
        await adminApi.createLessonContent(lessonId, payload);
        showSuccess('✅ Kontent qo\'shildi');
      }

      resetForm();
      onRefresh();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deletingId) return;
    setSaving(true);
    try {
      await adminApi.deleteLessonContent(lessonId, deletingId);
      setDeletingId(null);
      showSuccess('✅ Kontent o\'chirildi');
      onRefresh();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (item: ContentItem) => {
    setEditingId(item.id);
    setForm({
      type: item.type,
      title: item.title || '',
      description: item.description || '',  // ✅ Теперь правильно
      url: item.url || '',
      body: item.body || '',
      duration_seconds: item.duration_seconds,
      file_size_bytes: item.file_size_bytes,
      metadata: item.metadata || {},
      is_required: item.is_required || false,
      is_downloadable: item.is_downloadable || false,
      order: item.order,
    });
    setAdding(false);
  };

  const needsDuration = TYPES_WITH_DURATION.includes(form.type);
  const needsUpload = TYPES_WITH_UPLOAD.includes(form.type);
  const needsBody = form.type === 'text' || form.type === 'code';
  const needsUrl = !needsUpload && !needsBody;

  return (
    <div className="space-y-4">
      {/* Messages */}
      {success && (
        <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm font-body">
          {success}
        </div>
      )}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground font-body">
          {items.length} {t.curriculum?.lessons || 'ta dars'}
        </p>
        <button
          onClick={() => {
            resetForm();
            setAdding(true);
          }}
          className="text-sm font-semibold text-primary hover:text-primary/80 font-body"
        >
          {t.curriculum?.addLesson || '+ Kontent qo\'shish'}
        </button>
      </div>

      {/* Add/Edit Form */}
      {(adding || editingId) && (
        <div className="bg-muted border border-border rounded-xl p-4 space-y-4">
          <h3 className="text-sm font-semibold text-foreground font-heading">
            {editingId ? '✏️ Kontentni tahrirlash' : '➕ Yangi kontent'}
          </h3>

          {/* Type Selector */}
          <div>
            <label className="block text-xs font-medium text-foreground mb-1 font-body">
              Turi *
            </label>
            <div className="grid grid-cols-4 sm:grid-cols-7 gap-2">
              {(Object.keys(TYPE_LABELS) as ContentItemType[]).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setForm((f) => ({ ...f, type }))}
                  className={`px-2 py-2 rounded-lg text-xs font-semibold transition-all ${
                    form.type === type
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card border border-border text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <div className="text-lg mb-0.5">{TYPE_LABELS[type].icon}</div>
                  {TYPE_LABELS[type].label}
                </button>
              ))}
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="block text-xs font-medium text-foreground mb-1 font-body">
              Sarlavha *
            </label>
            <input
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              className="input"
              placeholder="Kontent sarlavhasi"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-medium text-foreground mb-1 font-body">
              Tavsif
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={2}
              className="input resize-none"
              placeholder="Qisqa tavsif"
            />
          </div>

          {/* URL / Upload / Body — в зависимости от типа */}
          {needsUpload && (
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {TYPE_LABELS[form.type].label}
              </label>
              <ContentUploader
                lessonId={lessonId}
                value={form.url}
                onChange={(url) => setForm((f) => ({ ...f, url }))}
                accept={ACCEPT_MAP[form.type]?.accept}
                acceptLabel={ACCEPT_MAP[form.type]?.label || 'Fayl'}
              />
            </div>
          )}

          {needsUrl && (
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                URL *
              </label>
              <input
                type="url"
                value={form.url}
                onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))}
                className="input font-mono"
                placeholder="https://..."
              />
            </div>
          )}

          {needsBody && (
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {form.type === 'code' ? 'Kod' : 'Matn'} *
              </label>
              <textarea
                value={form.body}
                onChange={(e) => setForm((f) => ({ ...f, body: e.target.value }))}
                rows={form.type === 'code' ? 10 : 6}
                className={`input resize-none ${form.type === 'code' ? 'font-mono text-sm' : ''}`}
                placeholder={form.type === 'code' ? 'console.log("Hello");' : 'Matn kontenti...'}
              />
            </div>
          )}

          {/* Duration — только для video и recording */}
          {needsDuration && (
            <DurationInput
              value={form.duration_seconds}
              onChange={(seconds) => setForm((f) => ({ ...f, duration_seconds: seconds }))}
              label="Davomiyligi"
            />
          )}

          {/* Checkboxes */}
          <div className="flex gap-6">
            <label className="flex items-center gap-2 text-sm text-foreground font-body cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_required}
                onChange={(e) => setForm((f) => ({ ...f, is_required: e.target.checked }))}
                className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30"
              />
              Majburiy kontent
            </label>
            <label className="flex items-center gap-2 text-sm text-foreground font-body cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_downloadable}
                onChange={(e) => setForm((f) => ({ ...f, is_downloadable: e.target.checked }))}
                className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30"
              />
              Yuklab olish mumkin
            </label>
          </div>

          {/* Buttons */}
          <div className="flex gap-2 pt-2">
            <button
              onClick={handleSave}
              disabled={saving}
              className="btn-primary text-sm"
            >
              {saving ? 'Saqlanmoqda...' : editingId ? '💾 Yangilash' : '➕ Qo\'shish'}
            </button>
            <button
              onClick={resetForm}
              className="btn-ghost text-sm"
            >
              Bekor qilish
            </button>
          </div>
        </div>
      )}

      {/* Items List */}
      <SortableList
        items={items}
        onReorder={async (reordered) => {
          try {
            await adminApi.reorderLessonContent(lessonId, reordered.map((i) => i.id));
            showSuccess('✅ Tartib yangilandi');
            onRefresh();
          } catch (err) {
            setError(handleApiError(err));
          }
        }}
        renderItem={(item, dragProps) => (
          <div className="p-4">
            <div className="flex items-start gap-3">
              <span {...dragProps} className="text-muted-foreground cursor-grab text-lg">⠿</span>
              <div className="text-2xl flex-shrink-0">{TYPE_LABELS[item.type]?.icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-semibold text-foreground truncate font-body">{item.title}</p>
                  <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full font-mono">
                    {TYPE_LABELS[item.type]?.label}
                  </span>
                  {item.is_required && (
                    <span className="text-xs bg-warning/10 text-warning px-2 py-0.5 rounded-full font-mono">
                      Majburiy
                    </span>
                  )}
                </div>
                {item.description && (
                  <p className="text-xs text-muted-foreground mb-1 line-clamp-2 font-body">
                    {item.description}
                  </p>
                )}
                <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono flex-wrap">
                  <span>
                  {item.duration_seconds && (
                    <span>
                      ⏱ {item.duration_seconds >= 3600
                        ? `${Math.round(item.duration_seconds / 3600 * 10) / 10} soat`
                        : item.duration_seconds >= 60
                        ? `${Math.round(item.duration_seconds / 60)} min`
                        : `${item.duration_seconds} sek`}
                    </span>
                  )}
                  {item.file_size_bytes && (
                    <span>
                      💾 {item.file_size_bytes >= 1024 * 1024
                        ? `${(item.file_size_bytes / (1024 * 1024)).toFixed(1)} MB`
                        : `${(item.file_size_bytes / 1024).toFixed(1)} KB`}
                    </span>
                  )}
                  {item.is_downloadable && (
                    <span>⬇️</span>
                  )}
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:text-primary/80 truncate max-w-[200px]"
                    >
                      🔗 Ochish
                    </a>
                  )}
                </div>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <button
                  onClick={() => startEdit(item)}
                  className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                >
                  ✏️
                </button>
                <button
                  onClick={() => setDeletingId(item.id)}
                  className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono"
                >
                  🗑
                </button>
              </div>
            </div>
          </div>
        )}
      />

      <ConfirmModal
        open={!!deletingId}
        title="Kontentni o'chirish"
        description="Bu kontent elementini o'chirishni tasdiqlaysizmi?"
        confirmLabel="O'chirish"
        danger
        loading={saving}
        onConfirm={handleDelete}
        onCancel={() => setDeletingId(null)}
      />
    </div>
  );
}