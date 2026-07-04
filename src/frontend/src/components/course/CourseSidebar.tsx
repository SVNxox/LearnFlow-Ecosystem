'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { CourseDetail } from '@/types/learning';
import { CourseEnrollment } from '@/types/api';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface CourseSidebarProps {
  course: CourseDetail;
  enrollment: CourseEnrollment | null;
  currentLessonId?: string;
}

export default function CourseSidebar({ course, enrollment, currentLessonId }: CourseSidebarProps) {
  const { t } = useTranslation();

  // Находим модуль с текущим уроком
  const currentModuleId = currentLessonId
    ? course.modules.find(m => m.lessons.some(l => l.id === currentLessonId))?.id
    : null;

  const [expandedModules, setExpandedModules] = useState<Set<string>>(() => {
    const initial = new Set<string>();
    if (currentModuleId) initial.add(currentModuleId);
    if (course.modules.length > 0) initial.add(course.modules[0].id);
    return initial;
  });

  // Автоматически раскрываем модуль с текущим уроком
  useEffect(() => {
    if (currentModuleId) {
      setExpandedModules(prev => new Set([...prev, currentModuleId]));
    }
  }, [currentModuleId]);

  const toggleModule = (moduleId: string) => {
    setExpandedModules(prev => {
      const next = new Set(prev);
      if (next.has(moduleId)) next.delete(moduleId);
      else next.add(moduleId);
      return next;
    });
  };

  const hasAccess = (lesson: any) => lesson.is_free_preview || !!enrollment;

  const totalLessons = course.modules.reduce((sum, m) => sum + m.lesson_count, 0);
  const totalHours = course.modules.reduce((sum, m) => sum + (m.estimated_hours || 0), 0);

  return (
    <aside className="h-full overflow-y-auto bg-card border-r border-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border flex-shrink-0">
        <Link
          href={`/courses/${course.slug}`}
          className="text-xs text-muted-foreground hover:text-foreground font-body block mb-2"
        >
          ← {t.courseDetail.backToList}
        </Link>
        <h2 className="text-sm font-bold text-foreground font-heading truncate">
          {course.title}
        </h2>
        <p className="text-xs text-muted-foreground mt-1 font-mono">
          {course.modules.length} modul · {totalLessons} dars
          {totalHours > 0 && ` · ${totalHours} soat`}
        </p>
      </div>

      {/* Modules list */}
      <div className="flex-1 overflow-y-auto p-2">
        {course.modules.map((module, moduleIdx) => {
          const isExpanded = expandedModules.has(module.id);
          const isCurrentModule = module.id === currentModuleId;

          return (
            <div key={module.id} className="mb-1">
              {/* Module header */}
              <button
                onClick={() => toggleModule(module.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-left transition-colors ${
                  isCurrentModule ? 'bg-primary/10' : 'hover:bg-muted'
                }`}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-foreground truncate font-body">
                    {moduleIdx + 1}. {module.title}
                  </p>
                  <p className="text-xs text-muted-foreground font-mono mt-0.5">
                    {module.lesson_count} dars
                    {module.estimated_hours ? ` · ${module.estimated_hours} soat` : ''}
                  </p>
                </div>
                <span
                  className={`text-muted-foreground transition-transform ml-2 ${
                    isExpanded ? 'rotate-180' : ''
                  }`}
                >
                  ▾
                </span>
              </button>

              {/* Lessons */}
              {isExpanded && (
                <div className="mt-0.5 ml-2 space-y-0.5">
                  {module.lessons.map((lesson) => {
                    const isCurrent = lesson.id === currentLessonId;
                    const accessible = hasAccess(lesson);

                    return (
                      <Link
                        key={lesson.id}
                        href={accessible ? `/courses/${course.slug}/lessons/${lesson.id}` : '
                        className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                          isCurrent
                            ? 'bg-primary text-primary-foreground font-semibold'
                            : accessible
                            ? 'text-foreground hover:bg-muted'
                            : 'text-muted-foreground cursor-not-allowed hover:bg-muted/50'
                        }`}
                        onClick={(e) => !accessible && e.preventDefault()}
                      >
                        <span className="text-xs font-mono w-5 flex-shrink-0">
                          {lesson.order}.
                        </span>
                        <span className="flex-1 truncate font-body">{lesson.title}</span>
                        {!accessible && <span className="text-xs">🔒</span>}
                        {lesson.is_free_preview && !isCurrent && (
                          <span className="text-xs">🆓</span>
                        )}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      {enrollment && (
        <div className="p-3 border-t border-border flex-shrink-0">
          <div className="bg-success/10 border border-success/30 rounded-lg px-3 py-2 text-center">
            <p className="text-xs text-success font-semibold font-body">
              ✅ {t.courseDetail.alreadyEnrolled}
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}