'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, handleApiError } from '@/lib/api';
import { Navbar, LoadingSpinner } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';

interface PracticeDetail {
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
  lesson_id: string;
  lesson_title: string;
  module_title: string;
  course_title: string;
}

export default function PracticePage() {
  const params = useParams<{ practiceId: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const { t } = useTranslation();

  const [practice, setPractice] = useState<PracticeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [code, setCode] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<{
    success: boolean;
    message: string;
    score?: number;
    feedback?: string;
  } | null>(null);
  const [showHints, setShowHints] = useState(false);
  const [showSolution, setShowSolution] = useState(false);

  useEffect(() => {
    if (!user) {
      router.push(`/login?next=/practice/${params.practiceId}`);
      return;
    }

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.learning.getPractice(params.practiceId);
        setPractice(data);
        setCode(data.starter_code || '');
      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [params.practiceId, user, router]);

  const handleSubmit = async () => {
    if (!code.trim()) {
      setError('Kod kiritilishi shart');
      return;
    }

    setSubmitting(true);
    setError(null);
    setSubmitResult(null);

    try {
      const result = await api.learning.submitPractice(params.practiceId, code);

      setSubmitResult(result);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    if (practice) {
      setCode(practice.starter_code || '');
      setSubmitResult(null);
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (error || !practice) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-16 text-center">
          <div className="text-5xl mb-4">💻</div>
          <p className="text-destructive mb-4 font-body">{error || 'Amaliyot topilmadi'}</p>
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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumbs */}
        <nav className="mb-4 text-sm text-muted-foreground font-body">
          <Link href="/courses" className="hover:text-foreground">Kurslar</Link>
          <span className="mx-2">/</span>
          <span>{practice.course_title}</span>
          <span className="mx-2">/</span>
          <span>{practice.module_title}</span>
          <span className="mx-2">/</span>
          <span className="text-foreground">{practice.title}</span>
        </nav>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Left: Description */}
          <div className="space-y-4">
            <div className="card p-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-3xl">💻</span>
                <h1 className="text-2xl font-bold text-foreground font-heading">
                  {practice.title}
                </h1>
              </div>

              {practice.description && (
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-foreground mb-2 font-body">
                    Tavsif
                  </h3>
                  <p className="text-muted-foreground font-body whitespace-pre-line">
                    {practice.description}
                  </p>
                </div>
              )}

              {practice.instructions && (
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-foreground mb-2 font-body">
                    Ko'rsatmalar
                  </h3>
                  <div className="bg-muted rounded-xl p-4">
                    <p className="text-foreground font-body whitespace-pre-line text-sm">
                      {practice.instructions}
                    </p>
                  </div>
                </div>
              )}

              <div className="flex gap-4 text-xs text-muted-foreground font-mono">
                <span>🎯 Maksimal ball: {practice.max_score}</span>
                {practice.time_limit_minutes && (
                  <span>⏰ Vaqt: {practice.time_limit_minutes} min</span>
                )}
                <span>🔤 Til: {practice.language}</span>
              </div>
            </div>

            {/* Hints */}
            {practice.hints && practice.hints.length > 0 && (
              <div className="card p-6">
                <button
                  onClick={() => setShowHints(!showHints)}
                  className="flex items-center justify-between w-full text-left"
                >
                  <h3 className="text-sm font-semibold text-foreground font-body flex items-center gap-2">
                    💡 Maslahatlar ({practice.hints.length})
                  </h3>
                  <span className={`transition-transform ${showHints ? 'rotate-180' : ''}`}>
                    ▾
                  </span>
                </button>
                {showHints && (
                  <ul className="mt-4 space-y-2">
                    {practice.hints.map((hint, i) => (
                      <li key={i} className="text-sm text-muted-foreground font-body flex items-start gap-2">
                        <span className="text-info">💡</span>
                        <span>{hint}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* Solution */}
            <div className="card p-6">
              <button
                onClick={() => setShowSolution(!showSolution)}
                className="flex items-center justify-between w-full text-left"
              >
                <h3 className="text-sm font-semibold text-foreground font-body flex items-center gap-2">
                  ✅ Yechim (namuna)
                </h3>
                <span className={`transition-transform ${showSolution ? 'rotate-180' : ''}`}>
                  ▾
                </span>
              </button>
              {showSolution && (
                <div className="mt-4">
                  <pre className="bg-background border border-border rounded-xl p-4 overflow-x-auto">
                    <code className="text-sm font-mono text-success whitespace-pre">
                      {practice.solution_code || 'Yechim mavjud emas'}
                    </code>
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Right: Code Editor */}
          <div className="space-y-4">
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-foreground font-body">
                  Kod muharriri
                </h3>
                <button
                  onClick={handleReset}
                  className="text-xs text-muted-foreground hover:text-foreground font-mono"
                >
                  🔄 Qayta tiklash
                </button>
              </div>

              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full h-96 bg-background border border-border rounded-xl p-4 font-mono text-sm text-foreground resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
                placeholder="Kodingizni shu yerga kiriting..."
                spellCheck={false}
              />

              <div className="flex gap-3 mt-4">
                <button
                  onClick={handleSubmit}
                  disabled={submitting || !code.trim()}
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
                    '📤 Yechimni yuborish'
                  )}
                </button>
              </div>
            </div>

            {/* Result */}
            {submitResult && (
              <div className={`card p-6 ${submitResult.success ? 'border-l-4 border-l-success' : 'border-l-4 border-l-destructive'}`}>
                <h3 className="text-lg font-bold text-foreground mb-2 font-heading">
                  {submitResult.success ? '✅ Natija' : '❌ Xatolik'}
                </h3>
                <p className="text-foreground font-body mb-2">
                  {submitResult.message}
                </p>
                {submitResult.score !== null && submitResult.score !== undefined && (
                  <p className="text-sm text-muted-foreground font-mono">
                    Ball: {submitResult.score} / {practice.max_score}
                  </p>
                )}
                {submitResult.feedback && (
                  <p className="text-sm text-muted-foreground font-body mt-2">
                    {submitResult.feedback}
                  </p>
                )}
              </div>
            )}

            {error && (
              <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}