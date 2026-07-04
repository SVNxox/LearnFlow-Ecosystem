'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, handleApiError } from '@/lib/api';
import { CourseDetail, LessonDetail } from '@/types/learning';
import { CourseEnrollment } from '@/types/api';
import { Navbar, LoadingSpinner } from '@/components/ui';
import CourseSidebar from '@/components/course/CourseSidebar';
import { useTranslation } from '@/lib/i18n/useTranslation';
import { formatDate } from '@/utils/helpers';

export default function LessonPage() {
  const params = useParams<{ slug: string; lessonId: string }>();
  const { user } = useAuth();
  const { t } = useTranslation();

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [enrollment, setEnrollment] = useState<CourseEnrollment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [courseData, lessonData] = await Promise.all([
          api.learning.getCourse(params.slug),
          api.learning.getLesson(params.lessonId),
        ]);

        if (!active) return;

        console.log('[LessonPage] Course:', courseData);
        console.log('[LessonPage] Lesson:', lessonData);
        console.log('[LessonPage] Content items:', lessonData.content_items);
        console.log('[LessonPage] Homework:', lessonData.homework);
        console.log('[LessonPage] Practice:', lessonData.practice_items);
        console.log('[LessonPage] Quiz:', lessonData.quiz);

        setCourse(courseData);
        setLesson(lessonData);

        if (user) {
          const enrollments = await api.enrollment.getMyEnrollments().catch(() => []);
          const mine = enrollments.find((e: any) => e.course_id === courseData.id && e.status !== 'dropped');
          if (active) setEnrollment(mine || null);
        }
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => { active = false; };
  }, [params.slug, params.lessonId, user]);

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (error || !course || !lesson) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-16 text-center">
          <div className="text-5xl mb-4">📖</div>
          <p className="text-destructive mb-4 font-body">{error || 'Dars topilmadi'}</p>
          <Link href="/courses" className="text-primary hover:text-primary/80 font-body">
            ← Kurslarga qaytish
          </Link>
        </div>
      </div>
    );
  }

  // Проверяем доступ к уроку
  const hasAccess = lesson.is_free_preview || !!enrollment;

  // Находим предыдущий и следующий уроки
  const allLessons = course.modules.flatMap(m => m.lessons);
  const currentIndex = allLessons.findIndex(l => l.id === lesson.id);
  const prevLesson = currentIndex > 0 ? allLessons[currentIndex - 1] : null;
  const nextLesson = currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : null;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="flex pt-14">
        {/* ✅ Sidebar слева */}
        <div className="w-80 flex-shrink-0 h-[calc(100vh-3.5rem)] sticky top-14">
          <CourseSidebar
            course={course}
            enrollment={enrollment}
            currentLessonId={lesson.id}
          />
        </div>

        {/* Main content */}
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-3xl mx-auto">
            {/* Breadcrumbs */}
            <nav className="mb-4 text-sm text-muted-foreground font-body">
              <Link href={`/courses/${course.slug}`} className="hover:text-foreground">
                {course.title}
              </Link>
              <span className="mx-2">/</span>
              <Link href={`/courses/${course.slug}/modules`} className="hover:text-foreground">
                {t.courseDetail.tabs.curriculum}
              </Link>
              <span className="mx-2">/</span>
              <span className="text-foreground">{lesson.title}</span>
            </nav>

            {!hasAccess ? (
              /* Нет доступа */
              <div className="card p-8 text-center">
                <div className="text-5xl mb-4">🔒</div>
                <h2 className="text-xl font-bold text-foreground mb-2 font-heading">
                  Bu dars yopiq
                </h2>
                <p className="text-muted-foreground mb-6 font-body">
                  Darsni ko'rish uchun kursga yozilishingiz kerak.
                </p>
                <Link
                  href={`/courses/${course.slug}`}
                  className="btn-primary inline-block"
                >
                  Kurs sahifasiga qaytish
                </Link>
              </div>
            ) : (
              <>
                {/* Lesson header */}
                <div className="mb-6">
                  <h1 className="text-2xl md:text-3xl font-bold text-foreground font-heading mb-2">
                    {lesson.title}
                  </h1>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground font-body flex-wrap">
                    <span>📖 {lesson.module_title}</span>
                    {lesson.estimated_minutes && (
                      <>
                        <span>·</span>
                        <span>⏱ {lesson.estimated_minutes} daqiqa</span>
                      </>
                    )}
                    {lesson.is_free_preview && (
                      <>
                        <span>·</span>
                        <span className="text-info font-semibold">🆓 Bepul ko'rib chiqish</span>
                      </>
                    )}
                  </div>
                  {lesson.description && (
                    <p className="text-muted-foreground mt-3 font-body">
                      {lesson.description}
                    </p>
                  )}
                </div>

                {/* Content items */}
                {lesson.content_items && lesson.content_items.length > 0 ? (
                  <div className="space-y-6 mb-8">
                    {lesson.content_items.map((item, index) => (
                      <div key={item.id} className="card overflow-hidden">
                        {/* Header */}
                        <div className="px-5 py-3 border-b border-border bg-muted/30">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-xl">
                                {item.type === 'video' && '🎥'}
                                {item.type === 'recording' && '🎙️'}
                                {item.type === 'text' && '📝'}
                                {item.type === 'code' && '💻'}
                                {item.type === 'pdf' && '📄'}
                                {item.type === 'slides' && '📊'}
                                {item.type === 'link' && '🔗'}
                              </span>
                              <h3 className="font-semibold text-foreground font-heading">
                                {index + 1}. {item.title}
                              </h3>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
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
                            </div>
                          </div>
                          {item.description && (
                            <p className="text-sm text-muted-foreground mt-2 font-body">
                              {item.description}
                            </p>
                          )}
                        </div>

                        {/* Content body */}
                        <div className="p-5">
                          {/* Video */}
                          {item.type === 'video' && item.url && (
                            <div className="bg-background rounded-xl overflow-hidden">
                              <video
                                src={item.url}
                                controls
                                className="w-full"
                                preload="metadata"
                              >
                                Brauzeringiz video qo'llab-quvvatlamaydi.
                              </video>
                            </div>
                          )}

                          {/* Audio */}
                          {item.type === 'recording' && item.url && (
                            <div className="bg-background rounded-xl p-4">
                              <audio
                                src={item.url}
                                controls
                                className="w-full"
                                preload="metadata"
                              >
                                Brauzeringiz audio qo'llab-quvvatlamaydi.
                              </audio>
                            </div>
                          )}

                          {/* PDF */}
                          {item.type === 'pdf' && item.url && (
                            <div className="space-y-3">
                              <iframe
                                src={item.url}
                                className="w-full h-[500px] border border-border rounded-xl"
                                title={item.title}
                              />
                              <div className="flex gap-2">
                                <a
                                  href={item.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="btn-ghost text-sm inline-flex items-center gap-2"
                                >
                                  🔗 Yangi oynada ochish
                                </a>
                                {item.is_downloadable && (
                                  <a
                                    href={item.url}
                                    download
                                    className="btn-primary text-sm inline-flex items-center gap-2"
                                  >
                                    ⬇️ Yuklab olish
                                  </a>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Slides */}
                          {item.type === 'slides' && item.url && (
                            <div className="space-y-3">
                              <iframe
                                src={item.url}
                                className="w-full h-[500px] border border-border rounded-xl"
                                title={item.title}
                              />
                              <a
                                href={item.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn-ghost text-sm inline-flex items-center gap-2"
                              >
                                🔗 Yangi oynada ochish
                              </a>
                            </div>
                          )}

                          {/* Text */}
                          {item.type === 'text' && item.body && (
                            <div className="prose prose-sm max-w-none text-foreground font-body whitespace-pre-line leading-relaxed">
                              {item.body}
                            </div>
                          )}

                          {/* Code */}
                          {item.type === 'code' && item.body && (
                            <div className="space-y-2">
                              <div className="flex items-center justify-between px-3 py-2 bg-muted rounded-t-xl border border-border border-b-0">
                                <span className="text-xs text-muted-foreground font-mono">
                                  {item.metadata?.language || 'code'}
                                </span>
                                <button
                                  onClick={() => navigator.clipboard.writeText(item.body || '')}
                                  className="text-xs text-primary hover:text-primary/80 font-mono"
                                >
                                  📋 Nusxa olish
                                </button>
                              </div>
                              <pre className="bg-background border border-border rounded-b-xl p-4 overflow-x-auto">
                                <code className="text-sm font-mono text-success">{item.body}</code>
                              </pre>
                            </div>
                          )}

                          {/* Link */}
                          {item.type === 'link' && item.url && (
                            <div className="space-y-3">
                              <a
                                href={item.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn-primary inline-flex items-center gap-2"
                              >
                                🔗 Havolaga o'tish
                              </a>
                              <p className="text-xs text-muted-foreground font-mono break-all">
                                {item.url}
                              </p>
                            </div>
                          )}

                          {/* Fallback если нет контента */}
                          {!item.url && !item.body && (
                            <div className="text-center py-8 text-muted-foreground">
                              <div className="text-4xl mb-2">📭</div>
                              <p className="text-sm font-body">Bu kontentda ma'lumot yo'q</p>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="card p-8 text-center mb-8">
                    <div className="text-4xl mb-3">📝</div>
                    <p className="text-muted-foreground font-body">
                      Bu darsda hali kontent yo'q
                    </p>
                  </div>
                )}

                {/* Homework */}
                {lesson.homework && (
                  <div className="card p-6 mb-8 border-l-4 border-l-warning">
                    <div className="flex items-start gap-3 mb-4">
                      <span className="text-3xl">📝</span>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-foreground font-heading mb-1">
                          Uy vazifasi
                        </h3>
                        <p className="font-semibold text-foreground font-body">
                          {lesson.homework.title}
                        </p>
                      </div>
                    </div>

                    <div className="space-y-3">
                      {lesson.homework.description && (
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">
                            Tavsif
                          </p>
                          <p className="text-sm text-foreground font-body whitespace-pre-line">
                            {lesson.homework.description}
                          </p>
                        </div>
                      )}

                      {lesson.homework.instructions && (
                        <div>
                          <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-1">
                            Ko'rsatmalar
                          </p>
                          <p className="text-sm text-foreground font-body whitespace-pre-line">
                            {lesson.homework.instructions}
                          </p>
                        </div>
                      )}

                      <div className="flex gap-4 pt-3 border-t border-border">
                        <div className="text-xs text-muted-foreground font-mono">
                          🎯 Maksimal ball: <span className="text-foreground font-semibold">{lesson.homework.max_score}</span>
                        </div>
                        {lesson.homework.deadline_offset_days && (
                          <div className="text-xs text-muted-foreground font-mono">
                            ⏰ Muddat: <span className="text-foreground font-semibold">{lesson.homework.deadline_offset_days} kun</span>
                          </div>
                        )}
                        <div className="text-xs text-muted-foreground font-mono">
                          📋 Turi: <span className="text-foreground font-semibold">{lesson.homework.type}</span>
                        </div>
                      </div>

                      <Link
                        href={`/submissions/new?homework_id=${lesson.homework.id}`}
                        className="btn-primary inline-flex items-center gap-2 mt-4"
                      >
                        📤 Uy vazifasini topshirish
                      </Link>
                    </div>
                  </div>
                )}

                {/* Practice */}
                {lesson.practice_items && lesson.practice_items.length > 0 && (
                  <div className="space-y-4 mb-8">
                    <div className="flex items-center gap-2 mb-4">
                      <span className="text-2xl">💻</span>
                      <h3 className="text-xl font-bold text-foreground font-heading">
                        Amaliyot mashqlari
                      </h3>
                    </div>

                    {lesson.practice_items.map((practice, index) => (
                      <div key={practice.id} className="card p-6 border-l-4 border-l-info">
                        <div className="flex items-start gap-3 mb-4">
                          <span className="text-2xl">💻</span>
                          <div className="flex-1">
                            <h4 className="font-semibold text-foreground font-body mb-1">
                              {index + 1}. {practice.title}
                            </h4>
                            {practice.description && (
                              <p className="text-sm text-muted-foreground font-body">
                                {practice.description}
                              </p>
                            )}
                          </div>
                        </div>

                        {practice.instructions && (
                          <div className="mb-4">
                            <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mb-2">
                              Ko'rsatmalar
                            </p>
                            <p className="text-sm text-foreground font-body whitespace-pre-line">
                              {practice.instructions}
                            </p>
                          </div>
                        )}

                        {practice.starter_code && (
                          <div className="space-y-2">
                            <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono">
                              Boshlang'ich kod
                            </p>
                            <pre className="bg-background border border-border rounded-xl p-4 overflow-x-auto">
                              <code className="text-sm font-mono text-success">{practice.starter_code}</code>
                            </pre>
                          </div>
                        )}

                        {practice.hints && practice.hints.length > 0 && (
                          <div className="mt-4 space-y-2">
                            <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono">
                              Maslahatlar
                            </p>
                            <ul className="space-y-1">
                              {practice.hints.map((hint, i) => (
                                <li key={i} className="text-sm text-muted-foreground font-body flex items-start gap-2">
                                  <span className="text-info">💡</span>
                                  <span>{hint}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        <div className="flex gap-4 mt-4 pt-4 border-t border-border">
                          {practice.max_score && (
                            <div className="text-xs text-muted-foreground font-mono">
                              🎯 Maksimal ball: <span className="text-foreground font-semibold">{practice.max_score}</span>
                            </div>
                          )}
                          {practice.time_limit_minutes && (
                            <div className="text-xs text-muted-foreground font-mono">
                              ⏰ Vaqt: <span className="text-foreground font-semibold">{practice.time_limit_minutes} min</span>
                            </div>
                          )}
                        </div>

                        <Link
                          href={`/practice/${practice.id}`}
                          className="btn-primary inline-flex items-center gap-2 mt-4"
                        >
                          ▶ Boshlash
                        </Link>
                      </div>
                    ))}
                  </div>
                )}

                {/* Quiz */}
                {lesson.quiz && (
                  <div className="card p-6 mb-8 border-l-4 border-l-primary">
                    <div className="flex items-start gap-3 mb-4">
                      <span className="text-3xl">❓</span>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-foreground font-heading mb-1">
                          Test: {lesson.quiz.title}
                        </h3>
                        <p className="text-sm text-muted-foreground font-body">
                          Bilimingizni sinab ko'ring
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="bg-muted rounded-lg p-3 text-center">
                        <p className="text-lg font-bold text-primary font-heading">{lesson.quiz.pass_score}%</p>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mt-1">
                          O'tish balli
                        </p>
                      </div>
                      <div className="bg-muted rounded-lg p-3 text-center">
                        <p className="text-lg font-bold text-primary font-heading">
                          {lesson.quiz.max_attempts || '∞'}
                        </p>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mt-1">
                          Urinishlar
                        </p>
                      </div>
                      {lesson.quiz.time_limit_minutes && (
                        <div className="bg-muted rounded-lg p-3 text-center">
                          <p className="text-lg font-bold text-primary font-heading">{lesson.quiz.time_limit_minutes}</p>
                          <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono mt-1">
                            Daqiqa
                          </p>
                        </div>
                      )}
                    </div>

                    <Link
                      href={`/assessments/${lesson.quiz.id}`}
                      className="btn-primary inline-flex items-center gap-2"
                    >
                      ▶ Testni boshlash
                    </Link>
                  </div>
                )}

                {/* Navigation */}
                <div className="flex items-center justify-between pt-6 border-t border-border">
                  {prevLesson ? (
                    <Link
                      href={`/courses/${course.slug}/lessons/${prevLesson.id}`}
                      className="btn-ghost inline-flex items-center gap-2"
                    >
                      ← {prevLesson.title}
                    </Link>
                  ) : (
                    <div />
                  )}
                  {nextLesson ? (
                    <Link
                      href={`/courses/${course.slug}/lessons/${nextLesson.id}`}
                      className="btn-primary inline-flex items-center gap-2"
                    >
                      {nextLesson.title} →
                    </Link>
                  ) : (
                    <Link
                      href={`/courses/${course.slug}/modules`}
                      className="btn-primary inline-flex items-center gap-2"
                    >
                      ✅ Kursni tugatish
                    </Link>
                  )}
                </div>
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}