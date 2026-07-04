'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api, handleApiError } from '@/lib/api';
import { Navbar, LoadingSpinner } from '@/components/ui';

interface AssessmentItem {
  id: string;
  type: string;
  title: string;
  description: string;
  max_points: string;
  order: number;
  options?: Array<{ id: string; text: string; order: number }>;
  starter_code?: string;
  coding_language?: string;
}

interface Assessment {
  id: string;
  title: string;
  instructions: string;
  time_limit_minutes: number;
  items: AssessmentItem[];
}

export default function TakeAssessmentPage() {
  const params = useParams<{ slug: string; id: string }>();
  const router = useRouter();
  const { user } = useAuth();

  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    loadAssessment();
  }, [params.id, user]);

  const loadAssessment = async () => {
    try {
      const data = await api.assessment.getStudentAssessmentDetail(params.id);
      setAssessment(data);

      // Автоматически начинаем попытку
      const attempt = await api.assessment.startAssessmentAttempt(params.id);
      setAttemptId(attempt.attempt_id);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (itemId: string, value: any) => {
    setAnswers(prev => ({ ...prev, [itemId]: value }));
  };

  const handleNext = async () => {
    const currentItem = assessment!.items[currentItemIndex];
    const answer = answers[currentItem.id];

    if (!answer) {
      setError('Iltimos, javobni to\'ldiring');
      return;
    }

    try {
      // Отправляем ответ
      const payload: any = { item_id: currentItem.id };

      if (currentItem.type === 'multiple_choice') {
        payload.selected_option_ids = Array.isArray(answer) ? answer : [answer];
      } else if (currentItem.type === 'coding') {
        payload.submitted_code = answer;
        payload.coding_language = currentItem.coding_language || 'python';
      } else {
        payload.text_response = answer;
      }

      await api.assessment.submitAssessmentResponse(attemptId!, payload);
      setError('');

      if (currentItemIndex < assessment!.items.length - 1) {
        setCurrentItemIndex(prev => prev + 1);
      }
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const handleSubmit = async () => {
    if (!attemptId) return;

    setSubmitting(true);
    setError('');

    try {
      const result = await api.assessment.submitAssessmentAttempt(attemptId);

      setSuccess(`✅ Test yakunlandi! Ball: ${result.final_score}/${result.max_score} (${result.percentage}%)`);

      setTimeout(() => {
        router.push(`/courses/${params.slug}`);
      }, 3000);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (!assessment) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-16 text-center">
          <p className="text-destructive mb-4 font-body">{error || 'Test topilmadi'}</p>
          <Link href={`/courses/${params.slug}`} className="text-primary hover:text-primary/80">
            ← Kursga qaytish
          </Link>
        </div>
      </div>
    );
  }

  const currentItem = assessment.items[currentItemIndex];
  const isLastItem = currentItemIndex === assessment.items.length - 1;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-foreground font-heading mb-2">
            {assessment.title}
          </h1>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>📝 Savol {currentItemIndex + 1} / {assessment.items.length}</span>
            <span>⏰ {assessment.time_limit_minutes} daqiqa</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all"
              style={{ width: `${((currentItemIndex + 1) / assessment.items.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Messages */}
        {success && (
          <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm mb-4">
            {success}
          </div>
        )}
        {error && (
          <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
            {error}
          </div>
        )}

        {/* Question */}
        <div className="card p-6 mb-6">
          <h2 className="text-lg font-bold text-foreground font-heading mb-3">
            {currentItem.title}
          </h2>
          <p className="text-muted-foreground font-body mb-4 whitespace-pre-line">
            {currentItem.description}
          </p>

          {/* Multiple Choice */}
          {currentItem.type === 'multiple_choice' && currentItem.options && (
            <div className="space-y-2">
              {currentItem.options.map((option) => (
                <label key={option.id} className="flex items-start gap-3 p-3 rounded-lg border border-border hover:bg-muted/50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={(answers[currentItem.id] || []).includes(option.id)}
                    onChange={(e) => {
                      const current = answers[currentItem.id] || [];
                      const newValue = e.target.checked
                        ? [...current, option.id]
                        : current.filter((id: string) => id !== option.id);
                      handleAnswerChange(currentItem.id, newValue);
                    }}
                    className="mt-1"
                  />
                  <span className="text-foreground font-body">{option.text}</span>
                </label>
              ))}
            </div>
          )}

          {/* Text Response */}
          {currentItem.type === 'text_response' && (
            <textarea
              value={answers[currentItem.id] || ''}
              onChange={(e) => handleAnswerChange(currentItem.id, e.target.value)}
              rows={8}
              className="input resize-none"
              placeholder="Javobingizni shu yerga kiriting..."
            />
          )}

          {/* Coding */}
          {currentItem.type === 'coding' && (
            <textarea
              value={answers[currentItem.id] || currentItem.starter_code || ''}
              onChange={(e) => handleAnswerChange(currentItem.id, e.target.value)}
              rows={15}
              className="input resize-none font-mono text-sm"
              placeholder="// Kodingizni shu yerga kiriting..."
              spellCheck={false}
            />
          )}
        </div>

        {/* Navigation */}
        <div className="flex gap-3">
          {currentItemIndex > 0 && (
            <button
              onClick={() => setCurrentItemIndex(prev => prev - 1)}
              className="btn-ghost"
            >
              ← Oldingi
            </button>
          )}

          {isLastItem ? (
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="btn-primary flex-1"
            >
              {submitting ? 'Yuborilmoqda...' : '✅ Testni yakunlash'}
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="btn-primary flex-1"
            >
              Keyingi →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}