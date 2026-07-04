'use client';

import { useState, useEffect } from 'react';  // ✅ Добавили useEffect
import Link from 'next/link';
import { ModuleWithLessons, LessonSummary } from '@/types/learning';
import { adminApi, isNotImplemented, handleApiError } from '@/lib/admin-api';
import SortableList from '../SortableList';
import PublishToggle from '../PublishToggle';
import NotImplementedBanner from '../NotImplementedBanner';
import { ConfirmModal } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface CurriculumTabProps {
  courseId: string;
  courseSlug: string;
  modules: ModuleWithLessons[];
  onRefresh: () => void;
}

export default function CurriculumTab({ courseId, courseSlug, modules, onRefresh }: CurriculumTabProps) {
  const { t } = useTranslation();
  const [localModules, setLocalModules] = useState(modules);
  const [addingModule, setAddingModule] = useState(false);

  // ✅ НОВОЕ: Синхронизация localModules с modules props
  useEffect(() => {
    setLocalModules(modules);
  }, [modules]);

  // ✅ НОВОЕ: Состояние для уведомлений
  const [success, setSuccess] = useState('');

  const [moduleForm, setModuleForm] = useState({
    title: '',
    description: '',
    estimated_hours: '',
  });

  const [savingModule, setSavingModule] = useState(false);
  const [addingLessonForModule, setAddingLessonForModule] = useState<string | null>(null);
  const [lessonForm, setLessonForm] = useState({ title: '', description: '', estimated_minutes: '', is_free_preview: false });

  const [editingModule, setEditingModule] = useState<{
    id: string;
    title: string;
    description: string;
    estimated_hours: string;
  } | null>(null);

  const [error, setError] = useState('');
  const [notImplemented, setNotImplemented] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ type: 'module' | 'lesson'; id: string; label: string } | null>(null);
  const [deleting, setDeleting] = useState(false);

  // ✅ Вспомогательная функция для показа уведомлений
  const showSuccess = (message: string) => {
    setSuccess(message);
    setTimeout(() => setSuccess(''), 3000);
  };

  const handleAddModule = async () => {
    if (!moduleForm.title.trim()) {
      setError(t.curriculum.titleRequired);
      return;
    }

    setSavingModule(true);
    setError('');
    setNotImplemented(false);

    try {
      await adminApi.createModule({
        course_id: courseId,
        title: moduleForm.title.trim(),
        description: moduleForm.description.trim() || undefined,
        estimated_hours: moduleForm.estimated_hours ? Number(moduleForm.estimated_hours) : undefined,
      });

      setModuleForm({ title: '', description: '', estimated_hours: '' });
      setAddingModule(false);

      // ✅ Показываем уведомление
      showSuccess('✅ Modul muvaffaqiyatli qo\'shildi');

      // ✅ Обновляем данные
      onRefresh();
    } catch (err) {
      if (isNotImplemented(err)) {
        setNotImplemented(true);
      } else {
        setError(handleApiError(err));
      }
    } finally {
      setSavingModule(false);
    }
  };

  const handleUpdateModule = async () => {
    if (!editingModule) return;

    if (!editingModule.title.trim()) {
      setError(t.curriculum.titleRequired);
      return;
    }

    setSavingModule(true);
    setError('');

    try {
      await adminApi.updateModule(editingModule.id, {
        title: editingModule.title.trim(),
        description: editingModule.description.trim() || undefined,
        estimated_hours: editingModule.estimated_hours ? Number(editingModule.estimated_hours) : undefined,
      });

      setEditingModule(null);

      // ✅ Показываем уведомление
      showSuccess('✅ Modul muvaffaqiyatli yangilandi');

      // ✅ Обновляем данные
      onRefresh();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSavingModule(false);
    }
  };

  const handleAddLesson = async (moduleId: string) => {
    if (!lessonForm.title.trim()) {
      setError(t.curriculum.titleRequired);
      return;
    }

    setSavingModule(true);
    setError('');
    setNotImplemented(false);

    try {
      await adminApi.createLesson({
        module_id: moduleId,
        title: lessonForm.title.trim(),
        description: lessonForm.description.trim() || undefined,
        estimated_minutes: lessonForm.estimated_minutes ? Number(lessonForm.estimated_minutes) : undefined,
        is_free_preview: lessonForm.is_free_preview,
      });

      setLessonForm({ title: '', description: '', estimated_minutes: '', is_free_preview: false });
      setAddingLessonForModule(null);

      // ✅ Показываем уведомление
      showSuccess('✅ Dars muvaffaqiyatli qo\'shildi');

      // ✅ Обновляем данные
      onRefresh();
    } catch (err) {
      if (isNotImplemented(err)) {
        setNotImplemented(true);
      } else {
        setError(handleApiError(err));
      }
    } finally {
      setSavingModule(false);
    }
  };

  const handleReorderModules = async (reordered: ModuleWithLessons[]) => {
    setLocalModules(reordered);
    try {
      await adminApi.reorderModules(courseId, reordered.map((m) => m.id));
      showSuccess('✅ Modul tartibi yangilandi');
    } catch {
      setLocalModules(modules);
      setError('Tartibni o\'zgartirishda xatolik');
    }
  };

  const handleReorderLessons = async (moduleId: string, reordered: LessonSummary[]) => {
    setLocalModules((prev) => prev.map((m) => m.id === moduleId ? { ...m, lessons: reordered } : m));
    try {
      await adminApi.reorderLessons(moduleId, reordered.map((l) => l.id));
      showSuccess('✅ Dars tartibi yangilandi');
    } catch {
      setLocalModules(modules);
      setError('Tartibni o\'zgartirishda xatolik');
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      if (deleteTarget.type === 'module') {
        await adminApi.deleteModule(deleteTarget.id);
        showSuccess('✅ Modul o\'chirildi');
      } else {
        await adminApi.deleteLesson(deleteTarget.id);
        showSuccess('✅ Dars o\'chirildi');
      }
      setDeleteTarget(null);
      onRefresh();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-4">
      {notImplemented && <NotImplementedBanner />}

      {/* ✅ Success message */}
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

      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground font-body">
          {localModules.length} {t.curriculum.modules}
        </p>
        <div className="flex items-center gap-4">
          <Link
            href={`/courses/${courseSlug}`}
            target="_blank"
            className="text-sm text-muted-foreground hover:text-foreground font-body"
          >
            {t.curriculum.previewOnSite}
          </Link>
          <button
            onClick={() => setAddingModule(true)}
            className="text-sm font-semibold text-primary hover:text-primary/80 font-body"
          >
            {t.curriculum.addModule}
          </button>
        </div>
      </div>

      {/* Add module form */}
      {addingModule && (
        <div className="bg-muted border border-border rounded-xl p-4 space-y-3">
          <div>
            <label className="block text-xs font-medium text-foreground mb-1 font-body">
              {t.curriculum.moduleTitle} *
            </label>
            <input
              value={moduleForm.title}
              onChange={(e) => setModuleForm((f) => ({ ...f, title: e.target.value }))}
              placeholder={t.curriculum.moduleTitle}
              className="input"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-foreground mb-1 font-body">
              {t.curriculum.moduleDescription}
            </label>
            <textarea
              value={moduleForm.description}
              onChange={(e) => setModuleForm((f) => ({ ...f, description: e.target.value }))}
              placeholder={t.curriculum.moduleDescription}
              rows={2}
              className="input resize-none"
            />
          </div>
          <div className="flex items-center gap-3">
            <div className="w-32">
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {t.curriculum.estimatedHours}
              </label>
              <input
                type="number"
                min="1"
                value={moduleForm.estimated_hours}
                onChange={(e) => setModuleForm((f) => ({ ...f, estimated_hours: e.target.value }))}
                placeholder={t.curriculum.hours}
                className="input"
              />
            </div>
            <div className="flex items-end gap-2 pt-5">
              <button
                onClick={handleAddModule}
                disabled={savingModule}
                className="btn-primary text-sm"
              >
                {savingModule ? t.curriculum.creating : t.curriculum.create}
              </button>
              <button
                onClick={() => {
                  setAddingModule(false);
                  setModuleForm({ title: '', description: '', estimated_hours: '' });
                  setError('');
                }}
                className="text-sm text-muted-foreground hover:text-foreground py-2 font-body"
              >
                {t.curriculum.cancel}
              </button>
            </div>
          </div>
        </div>
      )}

      <SortableList
        items={localModules}
        onReorder={handleReorderModules}
        renderItem={(module, dragProps) => (
          <div className="p-4">
            {/* Edit module form */}
            {editingModule?.id === module.id ? (
              <div className="bg-primary/5 border border-primary/20 rounded-xl p-4 space-y-3 mb-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.curriculum.moduleTitle} *
                  </label>
                  <input
                    value={editingModule.title}
                    onChange={(e) => setEditingModule((m) => m ? { ...m, title: e.target.value } : m)}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.curriculum.moduleDescription}
                  </label>
                  <textarea
                    value={editingModule.description}
                    onChange={(e) => setEditingModule((m) => m ? { ...m, description: e.target.value } : m)}
                    rows={2}
                    className="input resize-none"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32">
                    <label className="block text-xs font-medium text-foreground mb-1 font-body">
                      {t.curriculum.estimatedHours}
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={editingModule.estimated_hours}
                      onChange={(e) => setEditingModule((m) => m ? { ...m, estimated_hours: e.target.value } : m)}
                      className="input"
                    />
                  </div>
                  <div className="flex items-end gap-2 pt-5">
                    <button
                      onClick={handleUpdateModule}
                      disabled={savingModule}
                      className="btn-primary text-sm"
                    >
                      {savingModule ? t.curriculum.saving : t.curriculum.save}
                    </button>
                    <button
                      onClick={() => {
                        setEditingModule(null);
                        setError('');
                      }}
                      className="text-sm text-muted-foreground hover:text-foreground py-2 font-body"
                    >
                      {t.curriculum.cancel}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 mb-2">
                <span {...dragProps} className="text-muted-foreground cursor-grab">⠿</span>
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <p className="font-semibold text-foreground truncate font-body">{module.title}</p>
                  <PublishToggle type="module" id={module.id} isPublished={module.is_published} onChanged={() => {
                    onRefresh();
                    showSuccess('✅ Modul holati yangilandi');
                  }} onError={(msg) => setError(msg)} />
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={() => setEditingModule({
                      id: module.id,
                      title: module.title,
                      description: module.description || '',
                      estimated_hours: module.estimated_hours ? String(module.estimated_hours) : '',
                    })}
                    className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                  >
                    {t.curriculum.edit}
                  </button>
                  <button
                    onClick={() => setDeleteTarget({ type: 'module', id: module.id, label: module.title })}
                    className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono"
                  >
                    {t.curriculum.delete}
                  </button>
                </div>
              </div>
            )}

            {/* Module info */}
            {editingModule?.id !== module.id && (
              <>
                {module.description && (
                  <p className="text-xs text-muted-foreground ml-7 mb-1 line-clamp-2 font-body">{module.description}</p>
                )}
                <p className="text-xs text-muted-foreground ml-7 mb-3 font-mono">
                  {module.lesson_count} {t.curriculum.lessons}{module.estimated_hours ? ` · ~${module.estimated_hours}${t.curriculum.hours}` : ''}
                </p>
              </>
            )}

            <div className="ml-7 space-y-2">
              <SortableList
                items={module.lessons}
                onReorder={(reordered) => handleReorderLessons(module.id, reordered)}
                renderItem={(lesson, lessonDragProps) => (
                  <div className="flex items-center gap-2 px-3 py-2">
                    <span {...lessonDragProps} className="text-muted-foreground cursor-grab text-sm">⠿</span>
                    <span className="text-muted-foreground text-xs w-5 font-mono">{lesson.order}.</span>
                    <p className="flex-1 text-sm text-foreground truncate font-body">{lesson.title}</p>
                    {lesson.is_free_preview && (
                      <span className="text-xs text-info font-semibold font-mono">{t.curriculum.free}</span>
                    )}
                    <PublishToggle type="lesson" id={lesson.id} isPublished={lesson.is_published} onChanged={() => {
                      onRefresh();
                      showSuccess('✅ Dars holati yangilandi');
                    }} onError={(msg) => setError(msg)} />
                    <Link
                      href={`/admin/courses/${courseId}/modules/${module.id}/lessons/${lesson.id}`}
                      className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                    >
                      {t.curriculum.edit}
                    </Link>
                    <button
                      onClick={() => setDeleteTarget({ type: 'lesson', id: lesson.id, label: lesson.title })}
                      className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono"
                    >
                      ×
                    </button>
                  </div>
                )}
              />

              {addingLessonForModule === module.id ? (
                <div className="bg-muted border border-border rounded-xl p-3 space-y-2 mt-1">
                  <div>
                    <label className="block text-xs font-medium text-foreground mb-1 font-body">
                      {t.curriculum.lessonTitle} *
                    </label>
                    <input
                      value={lessonForm.title}
                      onChange={(e) => setLessonForm((f) => ({ ...f, title: e.target.value }))}
                      placeholder={t.curriculum.lessonTitle}
                      className="input text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-foreground mb-1 font-body">
                      {t.curriculum.lessonDescription}
                    </label>
                    <textarea
                      value={lessonForm.description}
                      onChange={(e) => setLessonForm((f) => ({ ...f, description: e.target.value }))}
                      placeholder={t.curriculum.lessonDescription}
                      rows={2}
                      className="input text-sm resize-none"
                    />
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-24">
                      <label className="block text-xs font-medium text-foreground mb-1 font-body">
                        {t.curriculum.estimatedMinutes}
                      </label>
                      <input
                        type="number"
                        min="1"
                        value={lessonForm.estimated_minutes}
                        onChange={(e) => setLessonForm((f) => ({ ...f, estimated_minutes: e.target.value }))}
                        placeholder={t.curriculum.min}
                        className="input text-sm"
                      />
                    </div>
                    <div className="pt-5">
                      <label className="flex items-center gap-1.5 text-xs text-foreground font-body cursor-pointer">
                        <input
                          type="checkbox"
                          checked={lessonForm.is_free_preview}
                          onChange={(e) => setLessonForm((f) => ({ ...f, is_free_preview: e.target.checked }))}
                          className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30"
                        />
                        {t.curriculum.freePreview}
                      </label>
                    </div>
                    <div className="flex items-end gap-2 pt-5 ml-auto">
                      <button
                        onClick={() => handleAddLesson(module.id)}
                        disabled={savingModule}
                        className="btn-primary text-xs"
                      >
                        {savingModule ? '...' : t.curriculum.create}
                      </button>
                      <button
                        onClick={() => {
                          setAddingLessonForModule(null);
                          setLessonForm({ title: '', description: '', estimated_minutes: '', is_free_preview: false });
                          setError('');
                        }}
                        className="text-xs text-muted-foreground hover:text-foreground py-1.5 font-body"
                      >
                        {t.curriculum.cancel}
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setAddingLessonForModule(module.id)}
                  className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                >
                  {t.curriculum.addLesson}
                </button>
              )}
            </div>
          </div>
        )}
      />

      <ConfirmModal
        open={!!deleteTarget}
        title={`${t.curriculum.delete} ${deleteTarget?.type}?`}
        description={`"${deleteTarget?.label}" ${t.curriculum.deleteWarning}`}
        confirmLabel={t.curriculum.delete}
        danger
        loading={deleting}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}