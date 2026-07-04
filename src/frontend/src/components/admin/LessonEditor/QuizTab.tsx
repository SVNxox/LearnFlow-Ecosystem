'use client';

import { useEffect, useState } from 'react';
import { QuizSettings, QuizQuestion, CreateQuestionBody } from '@/types/api';
import { adminApi, isNotImplemented, handleApiError } from '@/lib/admin-api';
import NotImplementedBanner from '../NotImplementedBanner';
import { useTranslation } from '@/lib/i18n/useTranslation';

const DEFAULT_SETTINGS: QuizSettings = {
  pass_score: 70,
  max_attempts: 3,
  time_limit_minutes: null,
  shuffle_questions: false,
  shuffle_options: false,
  show_correct_after_attempt: true,
};

interface QuizData {
  settings: QuizSettings;
  questions: QuizQuestion[];
}

export interface QuizTabProps {
  lessonId: string;
}

type QuestionFormState = CreateQuestionBody & {
  options: { body: string; is_correct: boolean }[];
};

const defaultQuestion = (): QuestionFormState => ({
  type: 'single_choice', body: '', explanation: '', points: 1,
  options: [{ body: '', is_correct: true }, { body: '', is_correct: false }],
});

export default function QuizTab({ lessonId }: QuizTabProps) {
  const { t } = useTranslation();
  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState<QuizSettings>(DEFAULT_SETTINGS);
  const [showSettingsForm, setShowSettingsForm] = useState(false);
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<QuizQuestion | null>(null);
  const [questionForm, setQuestionForm] = useState<QuestionFormState>(defaultQuestion());
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notImplemented, setNotImplemented] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    adminApi.getQuiz(lessonId)
      .then((data) => {
        if (!active) return;
        const loaded = data as Partial<QuizData> & { questions?: QuizQuestion[] };
        if (loaded && (loaded.settings || loaded.questions)) {
          const loadedSettings = loaded.settings || DEFAULT_SETTINGS;
          setQuiz({ settings: loadedSettings, questions: loaded.questions || [] });
          setSettings(loadedSettings);
        } else {
          setShowSettingsForm(true);
        }
      })
      .catch((err) => {
        if (!active) return;
        if (isNotImplemented(err)) { setNotImplemented(true); setShowSettingsForm(true); }
        else setShowSettingsForm(true);
      })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [lessonId]);

  const handleCreateOrUpdateQuiz = async () => {
    setSaving(true); setError(''); setNotImplemented(false);
    try {
      if (quiz) {
        await adminApi.updateQuiz(lessonId, settings);
        setQuiz({ ...quiz, settings });
      } else {
        await adminApi.createQuiz(lessonId, settings);
        setQuiz({ settings, questions: [] });
      }
      setShowSettingsForm(false);
    } catch (err) {
      if (isNotImplemented(err)) setNotImplemented(true);
      else setError(handleApiError(err));
    } finally { setSaving(false); }
  };

  const handleDeleteQuiz = async () => {
    if (!confirm(t.quiz.deleteConfirm)) return;
    setSaving(true);
    try {
      await adminApi.deleteQuiz(lessonId);
      setQuiz(null);
      setShowSettingsForm(true);
    } catch (err) {
      if (isNotImplemented(err)) setNotImplemented(true);
      else setError(handleApiError(err));
    } finally { setSaving(false); }
  };

  const validateQuestion = (q: QuestionFormState): string => {
    if (!q.body.trim()) return t.quiz.questionTextRequired;
    if (q.type !== 'short_text') {
      const correctCount = q.options.filter((o) => o.is_correct).length;
      if (q.type === 'single_choice' && correctCount !== 1) return t.quiz.validation.singleChoice;
      if (q.type === 'multiple_choice' && correctCount < 1) return t.quiz.validation.multipleChoice;
    }
    return '';
  };

  const handleSaveQuestion = async () => {
    const err = validateQuestion(questionForm);
    if (err) { setError(err); return; }
    setSaving(true); setError(''); setNotImplemented(false);
    try {
      let question: QuizQuestion;
      if (editingQuestion) {
        question = await adminApi.updateQuestion(lessonId, editingQuestion.id, {
          type: questionForm.type, body: questionForm.body,
          explanation: questionForm.explanation, points: questionForm.points,
        });
        for (const opt of editingQuestion.options) {
          await adminApi.deleteOption(lessonId, editingQuestion.id, opt.id).catch(() => {});
        }
      } else {
        question = await adminApi.addQuestion(lessonId, {
          type: questionForm.type, body: questionForm.body,
          explanation: questionForm.explanation, points: questionForm.points,
        });
      }
      if (questionForm.type !== 'short_text') {
        const optionsToAdd = questionForm.type === 'true_false'
          ? [{ body: 'True', is_correct: questionForm.options[0]?.is_correct ?? true }, { body: 'False', is_correct: !(questionForm.options[0]?.is_correct ?? true) }]
          : questionForm.options.filter((o) => o.body.trim());
        for (const opt of optionsToAdd) {
          await adminApi.addOption(lessonId, question.id, opt).catch(() => {});
        }
      }
      const updatedQuestions = editingQuestion
        ? quiz!.questions.map((q) => q.id === editingQuestion.id ? question : q)
        : [...(quiz?.questions || []), question];
      setQuiz((prev) => prev ? { ...prev, questions: updatedQuestions } : prev);
      setShowQuestionForm(false);
      setEditingQuestion(null);
      setQuestionForm(defaultQuestion());
    } catch (err) {
      if (isNotImplemented(err)) setNotImplemented(true);
      else setError(handleApiError(err));
    } finally { setSaving(false); }
  };

  const handleDeleteQuestion = async (q: QuizQuestion) => {
    if (!confirm(`${t.quiz.deleteConfirm} "${q.body.slice(0, 40)}"?`)) return;
    try {
      await adminApi.deleteQuestion(lessonId, q.id);
      setQuiz((prev) => prev ? { ...prev, questions: prev.questions.filter((qq) => qq.id !== q.id) } : prev);
    } catch (err) {
      if (isNotImplemented(err)) setNotImplemented(true);
      else setError(handleApiError(err));
    }
  };

  const openEditQuestion = (q: QuizQuestion) => {
    setEditingQuestion(q);
    setQuestionForm({
      type: q.type, body: q.body, explanation: q.explanation || '', points: q.points,
      options: q.options.map((o) => ({ body: o.body, is_correct: o.is_correct })),
    });
    setShowQuestionForm(true);
  };

  return (
    <div className="space-y-5">
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        </div>
      )}
      {!loading && notImplemented && <NotImplementedBanner />}
      {!loading && error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}
      {!loading && (
      <>
      {/* Quiz settings */}
      {showSettingsForm ? (
        <div className="bg-muted border border-border rounded-xl p-4 space-y-3">
          <h3 className="text-sm font-semibold text-foreground font-heading">
            {quiz ? t.quiz.editSettings : t.quiz.createQuiz}
          </h3>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {t.quiz.passScore}
              </label>
              <input type="number" min={0} max={100} value={settings.pass_score}
                onChange={(e) => setSettings((s) => ({ ...s, pass_score: Number(e.target.value) }))}
                className="input text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {t.quiz.maxAttempts}
              </label>
              <input type="number" min={1} value={settings.max_attempts ?? ''}
                onChange={(e) => setSettings((s) => ({ ...s, max_attempts: e.target.value ? Number(e.target.value) : null }))}
                className="input text-sm" placeholder="∞" />
            </div>
            <div>
              <label className="block text-xs font-medium text-foreground mb-1 font-body">
                {t.quiz.timeLimit}
              </label>
              <input type="number" min={1} value={settings.time_limit_minutes ?? ''}
                onChange={(e) => setSettings((s) => ({ ...s, time_limit_minutes: e.target.value ? Number(e.target.value) : null }))}
                className="input text-sm" placeholder={t.quiz.noTimeLimit} />
            </div>
          </div>
          <div className="flex flex-wrap gap-4 text-sm">
            {([['shuffle_questions', t.quiz.shuffleQuestions], ['shuffle_options', t.quiz.shuffleOptions], ['show_correct_after_attempt', t.quiz.showCorrect]] as const).map(([key, label]) => (
              <label key={key} className="flex items-center gap-2 text-foreground font-body cursor-pointer">
                <input type="checkbox" checked={!!settings[key]}
                  onChange={(e) => setSettings((s) => ({ ...s, [key]: e.target.checked }))}
                  className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30" />
                {label}
              </label>
            ))}
          </div>
          <div className="flex gap-2">
            <button onClick={handleCreateOrUpdateQuiz} disabled={saving}
              className="btn-primary text-sm">
              {saving ? t.quiz.saving : quiz ? t.quiz.updateSettings : t.quiz.createQuiz}
            </button>
            {quiz && (
              <button onClick={() => setShowSettingsForm(false)} className="btn-ghost text-sm">
                {t.quiz.cancel}
              </button>
            )}
          </div>
        </div>
      ) : quiz ? (
        <div className="flex items-center justify-between card px-4 py-3">
          <p className="text-sm text-foreground font-body">
            {quiz.settings.pass_score}% {t.quiz.pass} · {quiz.settings.max_attempts ?? '∞'} {t.quiz.attempts} · {quiz.settings.time_limit_minutes ? `${quiz.settings.time_limit_minutes} ${t.quiz.min}` : t.quiz.noTimeLimit}
          </p>
          <div className="flex gap-2">
            <button onClick={() => setShowSettingsForm(true)} className="text-xs text-primary hover:text-primary/80 font-semibold font-mono">
              {t.quiz.editSettings}
            </button>
            <button onClick={handleDeleteQuiz} className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono">
              {t.quiz.deleteQuiz}
            </button>
          </div>
        </div>
      ) : null}

      {/* Questions */}
      {quiz && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-foreground font-heading">
              {t.quiz.questions} ({quiz.questions.length})
            </h3>
            <button
              onClick={() => { setShowQuestionForm(true); setEditingQuestion(null); setQuestionForm(defaultQuestion()); }}
              className="text-sm font-semibold text-primary hover:text-primary/80 font-body"
            >
              {t.quiz.addQuestion}
            </button>
          </div>

          {showQuestionForm && (
            <div className="bg-muted border border-border rounded-xl p-4 space-y-3">
              <h4 className="text-sm font-semibold text-foreground font-heading">
                {editingQuestion ? t.quiz.editQuestion : t.quiz.newQuestion}
              </h4>
              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.quiz.questionText} *
                  </label>
                  <textarea
                    value={questionForm.body}
                    onChange={(e) => setQuestionForm((f) => ({ ...f, body: e.target.value }))}
                    rows={2}
                    className="input text-sm resize-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.quiz.type}
                  </label>
                  <select
                    value={questionForm.type}
                    onChange={(e) => setQuestionForm((f) => ({ ...f, type: e.target.value as QuestionFormState['type'] }))}
                    className="input text-sm mb-2"
                  >
                    <option value="single_choice">{t.quiz.types.single_choice}</option>
                    <option value="multiple_choice">{t.quiz.types.multiple_choice}</option>
                    <option value="true_false">{t.quiz.types.true_false}</option>
                    <option value="short_text">{t.quiz.types.short_text}</option>
                  </select>
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.quiz.points}
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={questionForm.points}
                    onChange={(e) => setQuestionForm((f) => ({ ...f, points: Number(e.target.value) }))}
                    className="input text-sm"
                  />
                </div>
              </div>

              {(questionForm.type === 'single_choice' || questionForm.type === 'multiple_choice') && (
                <div className="space-y-2">
                  <label className="text-xs font-medium text-foreground font-body">
                    {t.quiz.options}
                  </label>
                  {questionForm.options.map((opt, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <input
                        type={questionForm.type === 'single_choice' ? 'radio' : 'checkbox'}
                        name={`q-correct-${idx}`}
                        checked={opt.is_correct}
                        onChange={() => {
                          setQuestionForm((f) => ({
                            ...f,
                            options: f.options.map((o, i) => ({
                              ...o,
                              is_correct: questionForm.type === 'single_choice' ? i === idx : (i === idx ? !o.is_correct : o.is_correct),
                            })),
                          }));
                        }}
                        className="w-4 h-4 border-border text-primary focus:ring-primary/30"
                      />
                      <input
                        value={opt.body}
                        onChange={(e) => setQuestionForm((f) => ({
                          ...f,
                          options: f.options.map((o, i) => i === idx ? { ...o, body: e.target.value } : o),
                        }))}
                        placeholder={`Variant ${idx + 1}`}
                        className="flex-1 input text-sm"
                      />
                      {questionForm.options.length > 2 && (
                        <button
                          onClick={() => setQuestionForm((f) => ({ ...f, options: f.options.filter((_, i) => i !== idx) }))}
                          className="text-destructive hover:text-destructive/80 text-lg leading-none"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => setQuestionForm((f) => ({ ...f, options: [...f.options, { body: '', is_correct: false }] }))}
                    className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                  >
                    {t.quiz.addOption}
                  </button>
                </div>
              )}

              {questionForm.type === 'true_false' && (
                <p className="text-xs text-muted-foreground font-body">
                  {t.quiz.trueFalseHint}
                </p>
              )}

              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.quiz.explanation}
                </label>
                <input
                  value={questionForm.explanation || ''}
                  onChange={(e) => setQuestionForm((f) => ({ ...f, explanation: e.target.value }))}
                  className="input text-sm"
                  placeholder={t.quiz.explanationHint}
                />
              </div>

              {error && <p className="text-xs text-destructive font-body">{error}</p>}
              <div className="flex gap-2">
                <button
                  onClick={handleSaveQuestion}
                  disabled={saving}
                  className="btn-primary text-sm"
                >
                  {saving ? t.quiz.saving : t.quiz.saveQuestion}
                </button>
                <button
                  onClick={() => { setShowQuestionForm(false); setEditingQuestion(null); setError(''); }}
                  className="btn-ghost text-sm"
                >
                  {t.quiz.cancel}
                </button>
              </div>
            </div>
          )}

          {quiz.questions.length === 0 && !showQuestionForm && (
            <div className="text-center py-8">
              <div className="text-3xl mb-3">❓</div>
              <p className="text-sm text-muted-foreground font-body">{t.quiz.noQuestions}</p>
            </div>
          )}

          {quiz.questions.map((q, idx) => (
            <div key={q.id} className="card p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-sm font-medium text-foreground font-body">
                    Q{idx + 1}. {q.body}
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5 font-mono">
                    {q.type.replace('_', ' ')} · {q.points} {t.quiz.pt}
                  </p>
                  {q.options.map((o) => (
                    <p key={o.id} className={`text-xs mt-1 font-body ${o.is_correct ? 'text-success font-semibold' : 'text-muted-foreground'}`}>
                      {o.is_correct ? '✓' : '○'} {o.body}
                    </p>
                  ))}
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={() => openEditQuestion(q)}
                    className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                  >
                    {t.quiz.edit}
                  </button>
                  <button
                    onClick={() => handleDeleteQuestion(q)}
                    className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono"
                  >
                    {t.quiz.delete}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      </>
      )}
    </div>
  );
}