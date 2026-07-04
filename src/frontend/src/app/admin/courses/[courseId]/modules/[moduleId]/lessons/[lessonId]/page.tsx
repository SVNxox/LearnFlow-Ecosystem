'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { LessonDetail } from '@/types/learning';
import ContentTab from '@/components/admin/LessonEditor/ContentTab';
import QuizTab from '@/components/admin/LessonEditor/QuizTab';
import { HomeworkTab } from '@/components/admin/LessonEditor/HomeworkTab';
import { PracticeTab } from '@/components/admin/LessonEditor/PracticeTab';
import PublishToggle from '@/components/admin/PublishToggle';
import { useTranslation } from '@/lib/i18n/useTranslation';
import { formatDate } from '@/utils/helpers';

type Tab = 'content' | 'homework' | 'practice' | 'quiz';

export default function LessonEditorPage() {
  const { courseId, moduleId, lessonId } = useParams<{
    courseId: string;
    moduleId: string;
    lessonId: string;
  }>();
  const { t } = useTranslation();

  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState<Tab>('content');

  const [editingMeta, setEditingMeta] = useState(false);
  const [metaForm, setMetaForm] = useState({
    title: '',
    description: '',
    estimated_minutes: '',
    is_free_preview: false,
  });
  const [savingMeta, setSavingMeta] = useState(false);

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await adminApi.getLesson(lessonId);
      setLesson(data);
      setMetaForm({
        title: data.title,
        description: data.description || '',
        estimated_minutes: data.estimated_minutes ? String(data.estimated_minutes) : '',
        is_free_preview: data.is_free_preview,
      });
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [lessonId]);

  const handleSaveMeta = async () => {
    if (!metaForm.title.trim()) {
      setError(t.lessons.titleRequired);
      return;
    }

    setSavingMeta(true);
    setError('');
    try {
      await adminApi.updateLesson(lessonId, {
        title: metaForm.title.trim(),
        description: metaForm.description.trim() || undefined,
        estimated_minutes: metaForm.estimated_minutes ? Number(metaForm.estimated_minutes) : undefined,
        is_free_preview: metaForm.is_free_preview,
      });
      setEditingMeta(false);
      load();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSavingMeta(false);
    }
  };

  if (loading) {
    return (
      <AdminLayout roles={['admin', 'staff']}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
        </div>
      </AdminLayout>
    );
  }

  if (!lesson) {
    return (
      <AdminLayout roles={['admin', 'staff']}>
        <div className="text-center py-12">
          <div className="text-5xl mb-4">📖</div>
          <p className="text-destructive mb-4 font-body">{error || t.lessons.notFound}</p>
          <Link href="/admin/courses" className="text-primary hover:underline font-body">
            ← {t.courses.backToCourses}
          </Link>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Breadcrumbs */}
      <nav className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground font-body">
          <li>
            <Link href="/admin/courses" className="hover:text-foreground transition-colors">
              {t.lessons.breadcrumbs.courses}
            </Link>
          </li>
          <li>/</li>
          <li>
            <Link href={`/admin/courses/${courseId}`} className="hover:text-foreground transition-colors">
              {lesson.course_title}
            </Link>
          </li>
          <li>/</li>
          <li>
            <Link
              href={`/admin/courses/${courseId}/modules/${moduleId}`}
              className="hover:text-foreground transition-colors"
            >
              {lesson.module_title}
            </Link>
          </li>
          <li>/</li>
          <li className="text-foreground font-medium truncate max-w-xs">{lesson.title}</li>
        </ol>
      </nav>

      {/* Header with status */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          {editingMeta ? (
            <div className="space-y-3 max-w-2xl">
              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.lessons.titleLabel} *
                </label>
                <input
                  value={metaForm.title}
                  onChange={(e) => setMetaForm((f) => ({ ...f, title: e.target.value }))}
                  className="input text-lg font-bold"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.lessons.descriptionLabel}
                </label>
                <textarea
                  value={metaForm.description}
                  onChange={(e) => setMetaForm((f) => ({ ...f, description: e.target.value }))}
                  rows={3}
                  className="input resize-none"
                />
              </div>
              <div className="flex items-center gap-4">
                <div className="w-32">
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.lessons.minutes}
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={metaForm.estimated_minutes}
                    onChange={(e) => setMetaForm((f) => ({ ...f, estimated_minutes: e.target.value }))}
                    className="input"
                  />
                </div>
                <div className="pt-5">
                  <label className="flex items-center gap-2 text-sm text-foreground font-body cursor-pointer">
                    <input
                      type="checkbox"
                      checked={metaForm.is_free_preview}
                      onChange={(e) => setMetaForm((f) => ({ ...f, is_free_preview: e.target.checked }))}
                      className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30"
                    />
                    {t.lessons.freePreview}
                  </label>
                </div>
                <div className="flex items-end gap-2 pt-5 ml-auto">
                  <button
                    onClick={handleSaveMeta}
                    disabled={savingMeta}
                    className="btn-primary text-sm"
                  >
                    {savingMeta ? t.lessons.saving : t.lessons.save}
                  </button>
                  <button
                    onClick={() => {
                      setEditingMeta(false);
                      setError('');
                    }}
                    className="text-sm text-muted-foreground hover:text-foreground py-2 font-body"
                  >
                    {t.lessons.cancel}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-xl font-bold text-foreground font-heading">{lesson.title}</h1>
                <PublishToggle
                  type="lesson"
                  id={lessonId}
                  isPublished={lesson.is_published}
                  onChanged={load}
                  onError={(msg) => setError(msg)}
                />
              </div>
              {lesson.description && (
                <p className="text-sm text-muted-foreground mb-2 font-body">{lesson.description}</p>
              )}
              <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono flex-wrap">
                <span>{t.lessons.order}: {lesson.order}</span>
                <span>·</span>
                <span>{lesson.estimated_minutes ? `${lesson.estimated_minutes} ${t.lessons.min}` : t.lessons.noDuration}</span>
                <span>·</span>
                <span>{t.lessons.created}: {lesson.created_at ? formatDate(lesson.created_at) : '—'}</span>
                <span>·</span>
                <span>{t.lessons.updated}: {lesson.updated_at ? formatDate(lesson.updated_at) : '—'}</span>
              </div>
              <button
                onClick={() => setEditingMeta(true)}
                className="mt-2 text-xs text-primary hover:text-primary/80 font-semibold font-mono"
              >
                {t.lessons.editMetadata}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border mb-5">
        {([
          ['content', `${t.lessons.tabs.content} (${lesson.content_items.length})`],
          ['homework', t.lessons.tabs.homework],
          ['practice', `${t.lessons.tabs.practice} (${lesson.practice_items.length})`],
          ['quiz', t.lessons.tabs.quiz],
        ] as [Tab, string][]).map(([tTab, label]) => (
          <button
            key={tTab}
            onClick={() => setTab(tTab)}
            className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-colors font-body ${
              tab === tTab
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
          {error}
        </div>
      )}

      {/* Tab content */}
      {tab === 'content' && <ContentTab lessonId={lessonId} items={lesson.content_items} onRefresh={load} />}
      {tab === 'homework' && <HomeworkTab lessonId={lessonId} onRefresh={load} />}
      {tab === 'practice' && <PracticeTab lessonId={lessonId} items={lesson.practice_items} onRefresh={load} />}
      {tab === 'quiz' && <QuizTab lessonId={lessonId} />}
    </AdminLayout>
  );
}