'use client';

import { useState, useEffect } from 'react';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface HomeworkTabProps {
  lessonId: string;
  onRefresh: () => void;
}

const SUBMISSION_TYPES = [
  { value: 'text', label: 'Matnli javob', icon: '📝' },
  { value: 'file', label: 'Fayl yuklash', icon: '📎' },
  { value: 'code', label: 'Kod', icon: '💻' },
  { value: 'link', label: 'Havola', icon: '🔗' },
];

export function HomeworkTab({ lessonId, onRefresh }: HomeworkTabProps) {
  const { t } = useTranslation();

  const [homework, setHomework] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [form, setForm] = useState({
    title: '',
    description: '',
    instructions: '',
    max_score: 100,
    submission_type: 'text',
    allowed_file_types: [] as string[],
    max_file_size_mb: 50,
    deadline_offset_days: null as number | null,
  });

  useEffect(() => {
    loadHomework();
  }, [lessonId]);

  const loadHomework = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getLessonHomework(lessonId);
      setHomework(data);
      if (data) {
        setForm({
          title: data.title || '',
          description: data.description || '',
          instructions: data.instructions || '',
          max_score: data.max_score || 100,
          submission_type: data.submission_type || 'text',
          allowed_file_types: data.allowed_file_types || [],
          max_file_size_mb: data.max_file_size_mb || 50,
          deadline_offset_days: data.deadline_offset_days,
        });
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const showSuccess = (msg: string) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(''), 3000);
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
        title: form.title.trim(),
        description: form.description.trim(),
        instructions: form.instructions.trim(),
        max_score: form.max_score,
        submission_type: form.submission_type,
        allowed_file_types: form.allowed_file_types,
        max_file_size_mb: form.max_file_size_mb,
        deadline_offset_days: form.deadline_offset_days,
      };

      if (homework) {
        await adminApi.updateLessonHomework(lessonId, payload);
        showSuccess('✅ Uy vazifasi yangilandi');
      } else {
        await adminApi.createLessonHomework(lessonId, payload);
        showSuccess('✅ Uy vazifasi yaratildi');
      }

      setEditing(false);
      loadHomework();
      onRefresh();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!homework) return;

    if (!confirm('Uy vazifasini o\'chirishni xohlaysizmi?')) return;

    setSaving(true);
    try {
      await adminApi.deleteLessonHomework(lessonId);
      setHomework(null);
      setEditing(false);
      showSuccess('✅ Uy vazifasi o\'chirildi');
      onRefresh();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const startEdit = () => {
    if (homework) {
      setForm({
        title: homework.title || '',
        description: homework.description || '',
        instructions: homework.instructions || '',
        max_score: homework.max_score || 100,
        submission_type: homework.submission_type || 'text',
        allowed_file_types: homework.allowed_file_types || [],
        max_file_size_mb: homework.max_file_size_mb || 50,
        deadline_offset_days: homework.deadline_offset_days,
      });
    }
    setEditing(true);
  };

  if (loading) {
    return (
      <div className="card p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
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

      {/* View mode */}
      {homework && !editing && (
        <div className="card p-6 border-l-4 border-l-warning">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start gap-3">
              <span className="text-3xl">📝</span>
              <div>
                <h3 className="text-lg font-bold text-foreground font-heading">
                  {homework.title}
                </h3>
                <p className="text-xs text-muted-foreground font-mono mt-1">
                  {SUBMISSION_TYPES.find(t => t.value === homework.submission_type)?.icon}{' '}
                  {SUBMISSION_TYPES.find(t => t.value === homework.submission_type)?.label}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={startEdit}
                className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
              >
                ✏️ Tahrirlash
              </button>
              <button
                onClick={handleDelete}
                disabled={saving}
                className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono"
              >
                🗑 O'chirish
              </button>
            </div>
          </div>

          {homework.description && (
            <div className="mb-3">
              <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">
                Tavsif
              </p>
              <p className="text-sm text-foreground font-body whitespace-pre-line">
                {homework.description}
              </p>
            </div>
          )}

          {homework.instructions && (
            <div className="mb-3">
              <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">
                Ko'rsatmalar
              </p>
              <p className="text-sm text-foreground font-body whitespace-pre-line">
                {homework.instructions}
              </p>
            </div>
          )}

          <div className="flex gap-4 pt-3 border-t border-border flex-wrap text-xs text-muted-foreground font-mono">
            <span>🎯 Maksimal ball: {homework.max_score}</span>
            {homework.deadline_offset_days && (
              <span>⏰ Muddat: {homework.deadline_offset_days} kun</span>
            )}
            <span>📦 Maksimal fayl: {homework.max_file_size_mb} MB</span>
          </div>
        </div>
      )}

      {/* Edit/Create mode */}
      {editing && (
        <div className="card p-6 border-l-4 border-l-primary">
          <h3 className="text-lg font-bold text-foreground font-heading mb-4">
            {homework ? '✏️ Uy vazifasini tahrirlash' : '➕ Yangi uy vazifasi'}
          </h3>

          <div className="space-y-4">
            {/* Title */}
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Sarlavha *
              </label>
              <input
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                className="input"
                placeholder="Uy vazifasi sarlavhasi"
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
                rows={3}
                className="input resize-none"
                placeholder="Uy vazifasi haqida qisqa tavsif"
              />
            </div>

            {/* Instructions */}
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Ko'rsatmalar
              </label>
              <textarea
                value={form.instructions}
                onChange={(e) => setForm((f) => ({ ...f, instructions: e.target.value }))}
                rows={5}
                className="input resize-none"
                placeholder="Batafsil ko'rsatmalar..."
              />
            </div>

            {/* Submission type */}
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Topshirish turi
              </label>
              <div className="grid grid-cols-2 gap-2">
                {SUBMISSION_TYPES.map((type) => (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setForm((f) => ({ ...f, submission_type: type.value }))}
                    className={`px-3 py-2 rounded-lg text-sm font-semibold transition-all ${
                      form.submission_type === type.value
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-card border border-border text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    {type.icon} {type.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Max score + Deadline */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  Maksimal ball
                </label>
                <input
                  type="number"
                  min="1"
                  value={form.max_score}
                  onChange={(e) => setForm((f) => ({ ...f, max_score: Number(e.target.value) }))}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  Muddat (kun)
                </label>
                <input
                  type="number"
                  min="1"
                  value={form.deadline_offset_days || ''}
                  onChange={(e) => setForm((f) => ({ ...f, deadline_offset_days: e.target.value ? Number(e.target.value) : null }))}
                  className="input"
                  placeholder="Muddatsiz"
                />
              </div>
            </div>

            {/* Max file size */}
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Maksimal fayl hajmi (MB)
              </label>
              <input
                type="number"
                min="1"
                value={form.max_file_size_mb}
                onChange={(e) => setForm((f) => ({ ...f, max_file_size_mb: Number(e.target.value) }))}
                className="input max-w-xs"
              />
            </div>

            {/* Buttons */}
            <div className="flex gap-2 pt-2">
              <button
                onClick={handleSave}
                disabled={saving}
                className="btn-primary"
              >
                {saving ? 'Saqlanmoqda...' : homework ? '💾 Yangilash' : '➕ Yaratish'}
              </button>
              <button
                onClick={() => {
                  setEditing(false);
                  setError('');
                  if (homework) {
                    setForm({
                      title: homework.title || '',
                      description: homework.description || '',
                      instructions: homework.instructions || '',
                      max_score: homework.max_score || 100,
                      submission_type: homework.submission_type || 'text',
                      allowed_file_types: homework.allowed_file_types || [],
                      max_file_size_mb: homework.max_file_size_mb || 50,
                      deadline_offset_days: homework.deadline_offset_days,
                    });
                  }
                }}
                className="btn-ghost"
              >
                Bekor qilish
              </button>
            </div>
          </div>
        </div>
      )}

      {/* No homework - show create button */}
      {!homework && !editing && (
        <div className="card p-8 text-center">
          <div className="text-4xl mb-3">📝</div>
          <p className="text-muted-foreground mb-4 font-body">
            Bu darsda uy vazifasi yo'q
          </p>
          <button
            onClick={() => setEditing(true)}
            className="btn-primary"
          >
            ➕ Uy vazifasi qo'shish
          </button>
        </div>
      )}
    </div>
  );
}