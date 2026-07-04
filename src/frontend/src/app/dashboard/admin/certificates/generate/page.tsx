'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { useTranslation } from '@/lib/i18n/useTranslation';

interface UserWithEnrollment {
  id: string;
  email: string;
  name: string;
  enrollment_id: string;
  course_id: string;
  course_title: string;
}

interface Template {
  id: string;
  name: string;
  description: string;
}

export default function GenerateCertificatePage() {
  const router = useRouter();
  const { t } = useTranslation();

  const [users, setUsers] = useState<UserWithEnrollment[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedEnrollmentId, setSelectedEnrollmentId] = useState('');
  const [selectedTemplateId, setSelectedTemplateId] = useState('');
  const [finalScore, setFinalScore] = useState('100');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await adminApi.getCertificateGenerationData();
      setUsers(data.users_with_enrollments || []);
      setTemplates(data.templates || []);

      // Устанавливаем первый шаблон по умолчанию
      if (data.templates && data.templates.length > 0) {
        setSelectedTemplateId(data.templates[0].id);
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  // Фильтруем enrollments по выбранному пользователю
  const userEnrollments = users.filter(u => u.id === selectedUserId);

  // Уникальные пользователи
  const uniqueUsers = Array.from(new Map(users.map(u => [u.id, u])).values());

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSubmitting(true);

    try {
      const result = await adminApi.generateCertificate({
        user_id: selectedUserId,
        enrollment_id: selectedEnrollmentId || undefined,
        template_id: selectedTemplateId || undefined,
        final_score: finalScore,
      });

      setSuccess(
        `${t.certificates.generateSuccess}\n\n` +
        `${t.certificates.certificateNumber}: ${result.certificate_number}\n` +
        `${t.certificates.verificationCode}: ${result.verification_code}\n` +
        `${t.certificates.student}: ${result.student_full_name_snapshot}\n` +
        `${t.certificates.course}: ${result.course_name_snapshot}`
      );

      // Очищаем форму через 2 секунды и редиректим
      setTimeout(() => {
        router.push('/dashboard/admin/certificates');
      }, 3000);

    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSubmitting(false);
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

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Breadcrumbs */}
      <nav className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground font-body">
          <li>
            <Link href="/dashboard/admin/certificates" className="hover:text-foreground transition-colors">
              {t.certificates.title}
            </Link>
          </li>
          <li>/</li>
          <li className="text-foreground font-medium">{t.certificates.generateTitle}</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-foreground font-heading">
          {t.certificates.generateTitle}
        </h1>
        <p className="text-sm text-muted-foreground mt-1 font-body">
          Talaba uchun yangi sertifikat yarating
        </p>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm mb-4 whitespace-pre-line font-body">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="max-w-2xl">
        <div className="card p-6 space-y-6">
          {/* Student Selection */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2 font-body">
              {t.certificates.selectStudent} *
            </label>
            <select
              value={selectedUserId}
              onChange={(e) => {
                setSelectedUserId(e.target.value);
                setSelectedEnrollmentId(''); // Reset enrollment when user changes
              }}
              className="input"
              required
            >
              <option value="">{t.certificates.selectStudentPlaceholder}</option>
              {uniqueUsers.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name} ({user.email})
                </option>
              ))}
            </select>
            {uniqueUsers.length === 0 && (
              <p className="text-xs text-warning mt-1 font-body">
                {t.certificates.noStudents}
              </p>
            )}
          </div>

          {/* Enrollment Selection (if user has multiple enrollments) */}
          {userEnrollments.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-foreground mb-2 font-body">
                {t.certificates.selectCourse} *
              </label>
              <select
                value={selectedEnrollmentId}
                onChange={(e) => setSelectedEnrollmentId(e.target.value)}
                className="input"
                required
              >
                <option value="">{t.certificates.selectCoursePlaceholder}</option>
                {userEnrollments.map(enr => (
                  <option key={enr.enrollment_id} value={enr.enrollment_id}>
                    {enr.course_title}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Template Selection */}
          {templates.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-foreground mb-2 font-body">
                {t.certificates.selectTemplate}
              </label>
              <select
                value={selectedTemplateId}
                onChange={(e) => setSelectedTemplateId(e.target.value)}
                className="input"
              >
                <option value="">{t.certificates.defaultTemplate}</option>
                {templates.map(tmpl => (
                  <option key={tmpl.id} value={tmpl.id}>
                    {tmpl.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Final Score */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2 font-body">
              {t.certificates.finalScore}
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={finalScore}
              onChange={(e) => setFinalScore(e.target.value)}
              className="input"
            />
            <p className="text-xs text-muted-foreground mt-1 font-body">
              {t.certificates.finalScoreHint}
            </p>
          </div>

          {/* Preview Info */}
          {selectedUserId && selectedEnrollmentId && (
            <div className="bg-info/5 border border-info/20 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-foreground mb-3 font-heading">
                {t.certificates.certificatePreview}
              </h3>
              <div className="text-sm text-foreground space-y-1.5 font-body">
                <p>
                  <span className="text-muted-foreground">{t.certificates.student}:</span>{' '}
                  <span className="font-semibold">
                    {users.find(u => u.id === selectedUserId)?.name}
                  </span>
                </p>
                <p>
                  <span className="text-muted-foreground">{t.certificates.course}:</span>{' '}
                  <span className="font-semibold">
                    {userEnrollments.find(e => e.enrollment_id === selectedEnrollmentId)?.course_title}
                  </span>
                </p>
                <p>
                  <span className="text-muted-foreground">{t.certificates.score}:</span>{' '}
                  <span className="font-semibold">{finalScore}%</span>
                </p>
                <p>
                  <span className="text-muted-foreground">{t.certificates.template}:</span>{' '}
                  <span className="font-semibold">
                    {templates.find(tm => tm.id === selectedTemplateId)?.name || t.certificates.defaultTemplate}
                  </span>
                </p>
              </div>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={submitting || !selectedUserId || !selectedEnrollmentId}
              className="btn-primary flex-1"
            >
              {submitting ? t.certificates.generating : `✨ ${t.certificates.generate}`}
            </button>
            <Link
              href="/dashboard/admin/certificates"
              className="btn-ghost px-6"
            >
              {t.certificates.cancel}
            </Link>
          </div>
        </div>
      </form>
    </AdminLayout>
  );
}