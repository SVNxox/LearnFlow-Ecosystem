'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, handleApiError } from '@/lib/api';
import { Navbar, LoadingSpinner } from '@/components/ui';

interface HomeworkInfo {
  id: string;
  title: string;
  description: string;
  instructions: string;
  max_score: number;
  type: string;
  deadline_offset_days: number | null;
  max_file_size_mb: number;
  lesson_id: string;
  lesson_title: string;
  module_title: string;
  course_title: string;
  course_slug: string;
  assignment_id: string;  // ✅ ДОБАВЛЕНО
}

export default function NewSubmissionPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user } = useAuth();

  const homeworkId = searchParams.get('homework_id');

  const [homework, setHomework] = useState<HomeworkInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [textResponse, setTextResponse] = useState('');
  const [linkResponse, setLinkResponse] = useState('');
  const [codeResponse, setCodeResponse] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    if (!homeworkId) {
      setError('Homework ID not provided');
      setLoading(false);
      return;
    }

    loadHomework();
  }, [homeworkId, user, router]);

  const loadHomework = async () => {
    try {
      const data = await api.submissions.getHomeworkInfo(homeworkId!);
      setHomework(data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!homework) return;

    // Валидация
    if (homework.type === 'text' && !textResponse.trim()) {
      setError('Matnli javob kiritilishi shart');
      return;
    }
    if (homework.type === 'code' && !codeResponse.trim()) {
      setError('Kod kiritilishi shart');
      return;
    }
    if (homework.type === 'link' && !linkResponse.trim()) {
      setError('Havola kiritilishi shart');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      // Получаем enrollment студента
      const enrollments = await api.enrollment.getMyEnrollments();
      const enrollment = enrollments.find((e: any) => e.status === 'active');

      if (!enrollment) {
        throw new Error('Siz kursga yozilmagansiz yoki enrollment topilmadi');
      }

      console.log('[Submission] Enrollment:', enrollment);

      // Формируем payload
      let payload: any = {};
      let submissionType = 'text_answer';

      if (homework.type === 'text') {
        payload = { text: textResponse };
        submissionType = 'text_answer';
      } else if (homework.type === 'code') {
        payload = { code: codeResponse, language: 'python' };
        submissionType = 'text_answer';
      } else if (homework.type === 'link') {
        payload = { url: linkResponse };
        submissionType = 'external_link';
      }

      console.log('[Submission] Sending:', {
        assignment_id: homework.id,
        enrollment_id: enrollment.id,
        submission_type: submissionType,
        payload: payload,
      });

      // Создаём submission через API
      const submission = await api.submissions.createSubmission({
        assignment_id: homework.assignment_id,  // ← Теперь используем assignment_id
        enrollment_id: enrollment.id,
        submission_type: submissionType,
        payload: payload,
        notes: notes || '',
      });

      console.log('[Submission] Created:', submission);

      setSuccess('✅ Uy vazifasi muvaffaqiyatli topshirildi!');

      // Возвращаемся к уроку через 1.5 секунды
      setTimeout(() => {
        router.push(`/courses/${homework.course_slug}/lessons/${homework.lesson_id}`);
      }, 1500);
    } catch (err) {
      console.error('[Submission] Error:', err);
      setError(handleApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  const backToLessonUrl = homework
    ? `/courses/${homework.course_slug}/lessons/${homework.lesson_id}`
    : '/my-courses';

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (error && !homework) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-16 text-center">
          <div className="text-5xl mb-4">📝</div>
          <p className="text-destructive mb-4 font-body">{error}</p>
          <Link href="/courses" className="text-primary hover:text-primary/80 font-body">
            ← Kurslarga qaytish
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="mt-10 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Кнопка "Назад к уроку" */}
        <nav className="mb-4">
          <Link
            href={backToLessonUrl}
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground font-body transition-colors"
          >
            <span>←</span>
            <span>{homework?.lesson_title || 'Darsga qaytish'}</span>
          </Link>
        </nav>

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-foreground font-heading mb-2">
            📝 {homework?.title || 'Uy vazifasi'}
          </h1>
          {homework?.description && (
            <p className="text-muted-foreground font-body">{homework.description}</p>
          )}
        </div>

        {/* Messages */}
        {success && (
          <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm mb-4 font-body">
            {success}
          </div>
        )}
        {error && (
          <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
            {error}
          </div>
        )}

        {/* Homework info */}
        {homework && (
          <div className="card p-6 mb-6 border-l-4 border-l-warning">
            <h3 className="text-sm font-semibold text-foreground mb-3 font-body">
              Vazifa haqida
            </h3>
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
            <div className="flex gap-4 text-xs text-muted-foreground font-mono flex-wrap">
              <span>🎯 Maksimal ball: {homework.max_score}</span>
              <span>📋 Turi: {homework.type}</span>
              {homework.deadline_offset_days && (
                <span>⏰ Muddat: {homework.deadline_offset_days} kun</span>
              )}
              {homework.type === 'file' && (
                <span>📦 Maksimal hajm: {homework.max_file_size_mb} MB</span>
              )}
            </div>
          </div>
        )}

        {/* Submission form */}
        <div className="card p-6">
          <h3 className="text-lg font-bold text-foreground font-heading mb-4">
            Javobingizni kiriting
          </h3>

          {homework?.type === 'text' && (
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Matnli javob *
              </label>
              <textarea
                value={textResponse}
                onChange={(e) => setTextResponse(e.target.value)}
                rows={10}
                className="input resize-none"
                placeholder="Javobingizni shu yerga kiriting..."
              />
            </div>
          )}

          {homework?.type === 'link' && (
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Havola *
              </label>
              <input
                type="url"
                value={linkResponse}
                onChange={(e) => setLinkResponse(e.target.value)}
                className="input font-mono"
                placeholder="https://..."
              />
              <p className="text-xs text-muted-foreground mt-1 font-body">
                GitHub, GitLab yoki boshqa havolani kiriting
              </p>
            </div>
          )}

          {homework?.type === 'code' && (
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Kod *
              </label>
              <textarea
                value={codeResponse}
                onChange={(e) => setCodeResponse(e.target.value)}
                rows={15}
                className="input resize-none font-mono text-sm"
                placeholder="// Kodingizni shu yerga kiriting..."
                spellCheck={false}
              />
            </div>
          )}

          {homework?.type === 'file' && (
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                Fayl yuklash *
              </label>
              <input
                type="file"
                className="input"
              />
              <p className="text-xs text-muted-foreground mt-1 font-body">
                Maksimal hajm: {homework.max_file_size_mb} MB
              </p>
            </div>
          )}

          {/* Notes */}
          <div className="mt-4">
            <label className="block text-xs font-medium text-foreground mb-1 font-body">
              Qo'shimcha izoh (ixtiyoriy)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="input resize-none"
              placeholder="Mentor uchun qo'shimcha ma'lumot..."
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-3 mt-6">
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="btn-primary flex-1"
            >
              {submitting ? (
                <span className="inline-flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Yuborilmoqda...
                </span>
              ) : (
                '📤 Topshirish'
              )}
            </button>
            <Link
              href={backToLessonUrl}
              className="btn-ghost"
            >
              Bekor qilish
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}