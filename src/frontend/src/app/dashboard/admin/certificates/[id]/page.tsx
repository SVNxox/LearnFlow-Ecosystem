'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { StatusBadge } from '@/components/ui';
import { formatDate } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

interface AuditLog {
  id: string;
  action: string;
  actor_id: string | null;
  details: Record<string, unknown>;
  ip_address: string | null;
  created_at: string;
}

interface CertificateDetail {
  id: string;
  certificate_number: string;
  verification_code: string;
  student_full_name_snapshot: string;
  course_name_snapshot: string;
  course_description_snapshot: string | null;
  user_id: string | null;
  user_email: string | null;
  enrollment_id: string | null;
  course_id: string | null;
  template_id: string | null;
  status: string;
  final_score: string | null;
  completion_date: string | null;
  issued_at: string;
  pdf_url: string | null;
  pdf_generated_at: string | null;
  revoked_at: string | null;
  revoked_reason: string | null;
  revoked_by_id: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  audit_logs: AuditLog[];
}

export default function AdminCertificateDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { t } = useTranslation();
  const certId = params.id as string;

  const [cert, setCert] = useState<CertificateDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Edit mode
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    student_full_name_snapshot: '',
    course_name_snapshot: '',
    final_score: '',
    course_description_snapshot: '',
  });
  const [saving, setSaving] = useState(false);

  // Revoke modal
  const [showRevoke, setShowRevoke] = useState(false);
  const [revokeReason, setRevokeReason] = useState('');
  const [revoking, setRevoking] = useState(false);

  useEffect(() => {
    loadCertificate();
  }, [certId]);

  const loadCertificate = async () => {
    try {
      setLoading(true);
      const data = await adminApi.getCertificate(certId);
      setCert(data);
      setEditForm({
        student_full_name_snapshot: data.student_full_name_snapshot,
        course_name_snapshot: data.course_name_snapshot,
        final_score: data.final_score || '',
        course_description_snapshot: data.course_description_snapshot || '',
      });
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const updated = await adminApi.updateCertificate(certId, {
        student_full_name_snapshot: editForm.student_full_name_snapshot,
        course_name_snapshot: editForm.course_name_snapshot,
        final_score: editForm.final_score || undefined,
        course_description_snapshot: editForm.course_description_snapshot || undefined,
      });
      setCert(updated);
      setEditing(false);
      setSuccess(t.certificates.updateSuccess);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const handleRevoke = async () => {
    if (!revokeReason.trim()) return;
    setRevoking(true);
    setError('');
    try {
      await adminApi.revokeCertificate(certId, { reason: revokeReason });
      await loadCertificate();
      setShowRevoke(false);
      setRevokeReason('');
      setSuccess(t.certificates.revokeSuccess);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setRevoking(false);
    }
  };

  const copyVerificationCode = () => {
    if (cert) {
      navigator.clipboard.writeText(cert.verification_code);
      setSuccess(t.certificates.codeCopied);
      setTimeout(() => setSuccess(''), 2000);
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

  if (!cert) {
    return (
      <AdminLayout roles={['admin', 'staff']}>
        <div className="text-center py-12">
          <div className="text-5xl mb-4">📜</div>
          <p className="text-muted-foreground mb-4 font-body">{t.certificates.invalidCertificate}</p>
          <Link href="/dashboard/admin/certificates" className="text-primary hover:underline font-body">
            ← {t.certificates.backToList}
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
            <Link href="/dashboard/admin/certificates" className="hover:text-foreground transition-colors">
              {t.certificates.title}
            </Link>
          </li>
          <li>/</li>
          <li className="text-foreground font-medium truncate max-w-xs font-mono">
            {cert.certificate_number}
          </li>
        </ol>
      </nav>

      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-foreground font-heading">{t.certificates.details}</h1>
          <p className="text-sm text-muted-foreground font-mono mt-1">{cert.certificate_number}</p>
        </div>
        <div className="flex gap-2">
          {cert.status === 'issued' && !editing && (
            <>
              <button
                onClick={() => setEditing(true)}
                className="btn-primary text-sm"
              >
                ✏️ {t.certificates.edit}
              </button>
              <button
                onClick={() => setShowRevoke(true)}
                className="btn-danger text-sm"
              >
                🚫 {t.certificates.revoke}
              </button>
            </>
          )}
          {editing && (
            <>
              <button
                onClick={handleSave}
                disabled={saving}
                className="btn-primary text-sm"
              >
                {saving ? t.certificates.saving : `💾 ${t.certificates.save}`}
              </button>
              <button
                onClick={() => {
                  setEditing(false);
                  setEditForm({
                    student_full_name_snapshot: cert.student_full_name_snapshot,
                    course_name_snapshot: cert.course_name_snapshot,
                    final_score: cert.final_score || '',
                    course_description_snapshot: cert.course_description_snapshot || '',
                  });
                }}
                className="btn-ghost text-sm"
              >
                {t.certificates.cancel}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm mb-4">
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Status Card */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-foreground font-heading">{t.certificates.status}</h2>
              <StatusBadge status={cert.status} />
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground font-body">{t.certificates.issuedAt}</p>
                <p className="font-medium text-foreground font-body">{formatDate(cert.issued_at)}</p>
              </div>
              <div>
                <p className="text-muted-foreground font-body">{t.certificates.completionDate}</p>
                <p className="font-medium text-foreground font-body">
                  {cert.completion_date ? formatDate(cert.completion_date) : '—'}
                </p>
              </div>
              {cert.revoked_at && (
                <>
                  <div>
                    <p className="text-muted-foreground font-body">{t.certificates.revokedAt}</p>
                    <p className="font-medium text-destructive font-body">{formatDate(cert.revoked_at)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground font-body">{t.certificates.revocationReason}</p>
                    <p className="font-medium text-destructive font-body">{cert.revoked_reason || '—'}</p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Student & Course */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4 font-heading">
              {t.certificates.student} & {t.certificates.course}
            </h2>
            {editing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1 font-body">
                    {t.certificates.studentName}
                  </label>
                  <input
                    type="text"
                    value={editForm.student_full_name_snapshot}
                    onChange={(e) => setEditForm(f => ({ ...f, student_full_name_snapshot: e.target.value }))}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1 font-body">
                    {t.certificates.courseName}
                  </label>
                  <input
                    type="text"
                    value={editForm.course_name_snapshot}
                    onChange={(e) => setEditForm(f => ({ ...f, course_name_snapshot: e.target.value }))}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1 font-body">
                    {t.certificates.finalScore} (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    value={editForm.final_score}
                    onChange={(e) => setEditForm(f => ({ ...f, final_score: e.target.value }))}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1 font-body">
                    {t.certificates.courseDescription}
                  </label>
                  <textarea
                    value={editForm.course_description_snapshot}
                    onChange={(e) => setEditForm(f => ({ ...f, course_description_snapshot: e.target.value }))}
                    rows={3}
                    className="input resize-none"
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-muted-foreground uppercase font-mono">{t.certificates.student}</p>
                  <p className="text-lg font-semibold text-foreground font-heading">{cert.student_full_name_snapshot}</p>
                  {cert.user_email && <p className="text-sm text-muted-foreground font-body">{cert.user_email}</p>}
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase font-mono">{t.certificates.course}</p>
                  <p className="text-lg font-semibold text-foreground font-heading">{cert.course_name_snapshot}</p>
                </div>
                {cert.course_description_snapshot && (
                  <div>
                    <p className="text-xs text-muted-foreground uppercase font-mono">{t.certificates.courseDescription}</p>
                    <p className="text-sm text-foreground font-body">{cert.course_description_snapshot}</p>
                  </div>
                )}
                <div>
                  <p className="text-xs text-muted-foreground uppercase font-mono">{t.certificates.finalScore}</p>
                  <p className="text-2xl font-bold font-heading" style={{ color: 'var(--color-info)' }}>
                    {cert.final_score ? `${cert.final_score}%` : '—'}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Audit Logs */}
          {cert.audit_logs && cert.audit_logs.length > 0 && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4 font-heading">{t.certificates.auditLogs}</h2>
              <div className="space-y-3">
                {cert.audit_logs.map(log => (
                  <div key={log.id} className="flex items-start gap-3 pb-3 border-b border-border last:border-0">
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                      log.action === 'created' ? 'bg-info' :
                      log.action === 'issued' ? 'bg-success' :
                      log.action === 'revoked' ? 'bg-destructive' :
                      log.action === 'updated' ? 'bg-warning' :
                      'bg-muted-foreground'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground capitalize font-body">{log.action}</p>
                      <p className="text-xs text-muted-foreground font-mono">
                        {formatDate(log.created_at)}
                        {log.ip_address && ` • IP: ${log.ip_address}`}
                      </p>
                      {log.details && Object.keys(log.details).length > 0 && (
                        <pre className="text-xs text-muted-foreground mt-1 bg-muted p-2 rounded-lg overflow-x-auto font-mono">
                          {JSON.stringify(log.details, null, 2)}
                        </pre>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Verification */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4 font-heading">{t.certificates.verification}</h2>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-muted-foreground uppercase font-mono">{t.certificates.certificateNumber}</p>
                <p className="font-mono text-sm text-foreground break-all">{cert.certificate_number}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase font-mono">{t.certificates.verificationCode}</p>
                <p className="font-mono text-sm text-foreground break-all">{cert.verification_code}</p>
              </div>
              <button
                onClick={copyVerificationCode}
                className="btn-ghost w-full text-sm"
              >
                📋 {t.certificates.copyVerificationCode}
              </button>
            </div>
          </div>

          {/* PDF */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4 font-heading">{t.certificates.pdfDocument}</h2>
            {cert.pdf_url ? (
              <div>
                <a
                  href={cert.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary w-full inline-flex items-center justify-center gap-2"
                >
                  📄 {t.certificates.downloadPdf}
                </a>
                {cert.pdf_generated_at && (
                  <p className="text-xs text-muted-foreground mt-2 font-mono">
                    {formatDate(cert.pdf_generated_at)}
                  </p>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground font-body">{t.certificates.pdfNotGenerated}</p>
            )}
          </div>

          {/* IDs */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4 font-heading">{t.certificates.references}</h2>
            <div className="space-y-2 text-xs">
              <div>
                <p className="text-muted-foreground font-mono">{t.certificates.userId}</p>
                <p className="font-mono text-foreground break-all">{cert.user_id || '—'}</p>
              </div>
              <div>
                <p className="text-muted-foreground font-mono">{t.certificates.enrollmentId}</p>
                <p className="font-mono text-foreground break-all">{cert.enrollment_id || '—'}</p>
              </div>
              <div>
                <p className="text-muted-foreground font-mono">{t.certificates.courseId}</p>
                <p className="font-mono text-foreground break-all">{cert.course_id || '—'}</p>
              </div>
              <div>
                <p className="text-muted-foreground font-mono">{t.certificates.templateId}</p>
                <p className="font-mono text-foreground break-all">{cert.template_id || '—'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Revoke Modal */}
      {showRevoke && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowRevoke(false)} />
          <div className="relative bg-card border border-border rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-bold text-foreground mb-2 font-heading">{t.certificates.revoke}</h3>
            <p className="text-sm text-muted-foreground mb-4 font-body leading-relaxed">
              {t.certificates.revokeWarning}
            </p>
            <textarea
              value={revokeReason}
              onChange={(e) => setRevokeReason(e.target.value)}
              rows={3}
              placeholder={t.certificates.revokeReason}
              className="input resize-none mb-4"
              autoFocus
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShowRevoke(false)}
                className="btn-ghost flex-1 text-sm"
              >
                {t.certificates.cancel}
              </button>
              <button
                onClick={handleRevoke}
                disabled={revoking || !revokeReason.trim()}
                className="btn-danger flex-1 text-sm"
              >
                {revoking ? 'Yuklanmoqda...' : t.certificates.revoke}
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}