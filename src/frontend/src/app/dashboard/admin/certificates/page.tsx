'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { Certificate } from '@/types/api';
import { StatusBadge } from '@/components/ui';
import { formatDate } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

const STATUS_TABS = [
  { value: '', label: 'Barchasi' },
  { value: 'pending', label: 'Kutilmoqda' },
  { value: 'issued', label: 'Berilgan' },
  { value: 'revoked', label: 'Bekor qilingan' },
];

function CertificatesContent() {
  const { t } = useTranslation();
  const router = useRouter();
  const sp = useSearchParams();
  const status = sp.get('status') || '';
  const page = parseInt(sp.get('page') || '1', 10);
  const searchFromUrl = sp.get('search') || '';

  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [count, setCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchInput, setSearchInput] = useState(searchFromUrl);

  const updateParam = useCallback((key: string, value: string | null) => {
    const params = new URLSearchParams(sp.toString());
    if (value) params.set(key, value); else params.delete(key);
    if (key !== 'page') params.delete('page');
    router.push(`/dashboard/admin/certificates?${params.toString()}`);
  }, [router, sp]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== searchFromUrl) {
        updateParam('search', searchInput || null);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchInput, searchFromUrl, updateParam]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    adminApi.getAllCertificates({
      status: status || undefined,
      search: searchFromUrl || undefined,
      page,
    })
      .then((data) => {
        if (!active) return;
        const results = (data as { results?: Certificate[] }).results || (data as Certificate[]);
        setCertificates(results);
        setCount((data as { count?: number }).count || results.length);
        setTotalPages((data as { total_pages?: number }).total_pages || 1);
      })
      .catch((err) => {
        if (!active) return;
        setError(handleApiError(err));
      })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [status, page, searchFromUrl]);

  const handleRevoke = async (certId: string, reason: string) => {
    try {
      await adminApi.revokeCertificate(certId, { reason });
      setCertificates(prev => prev.map(c =>
        c.id === certId ? { ...c, status: 'revoked' } : c
      ));
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  // Statistika
  const issuedCount = certificates.filter(c => c.status === 'issued').length;
  const pendingCount = certificates.filter(c => c.status === 'pending').length;
  const revokedCount = certificates.filter(c => c.status === 'revoked').length;
  const avgScore = certificates.length > 0
    ? certificates.reduce((sum, c) => sum + (parseFloat(c.final_score || '0')), 0) / certificates.length
    : 0;

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-foreground font-heading">
            {t.certificates.title} ({count})
          </h1>
          <p className="text-sm text-muted-foreground mt-1 font-body">
            Barcha sertifikatlar ro'yxati va boshqaruvi
          </p>
        </div>
        <Link
          href="/dashboard/admin/certificates/generate"
          className="btn-primary text-sm inline-flex items-center gap-2"
        >
          <span>+</span>
          {t.certificates.generate}
        </Link>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.certificates.total}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-foreground)' }}>{count}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.certificates.issued}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-success)' }}>{issuedCount}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.certificates.pending}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-warning)' }}>{pendingCount}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.certificates.score}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-info)' }}>{avgScore.toFixed(0)}%</p>
        </div>
      </div>

      {/* Status tabs */}
      <div className="filter-pills mb-4">
        {STATUS_TABS.map((s) => (
          <button
            key={s.value}
            onClick={() => updateParam('status', s.value || null)}
            className={`filter-pill ${status === s.value ? 'filter-pill-active' : 'filter-pill-inactive'}`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder={t.certificates.search}
            className="input pl-10"
          />
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            🔍
          </span>
          {searchInput && (
            <button
              type="button"
              onClick={() => setSearchInput('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-card border border-border rounded-2xl overflow-hidden">
        <table className="min-w-full divide-y divide-border">
          <thead>
            <tr className="bg-muted/50">
              {[
                t.certificates.student,
                t.certificates.course,
                t.certificates.certificateNumber,
                t.certificates.score,
                t.certificates.status,
                t.certificates.issuedAt,
                t.common.actions,
              ].map((h) => (
                <th
                  key={h}
                  className="px-5 py-3 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider font-mono"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <tr key={i}>
                  <td colSpan={7} className="px-5 py-4">
                    <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                  </td>
                </tr>
              ))
            ) : certificates.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-5 py-12 text-center">
                  <div className="text-3xl mb-3">📜</div>
                  <p className="text-sm text-muted-foreground font-body">
                    {t.certificates.noCertificates}
                  </p>
                </td>
              </tr>
            ) : (
              certificates.map((cert) => (
                <tr key={cert.id} className="hover:bg-muted/30 transition-colors">
                  {/* Student */}
                  <td className="px-5 py-3.5">
                    <div>
                      <p className="text-sm font-medium text-foreground font-body">
                        {cert.student_full_name_snapshot || '—'}
                      </p>
                      {cert.user_email && (
                        <p className="text-xs text-muted-foreground font-mono mt-0.5">
                          {cert.user_email}
                        </p>
                      )}
                    </div>
                  </td>

                  {/* Course */}
                  <td className="px-5 py-3.5 text-sm text-foreground font-body">
                    {cert.course_name_snapshot || '—'}
                  </td>

                  {/* Certificate number */}
                  <td className="px-5 py-3.5">
                    <p className="text-xs font-mono text-foreground">
                      {cert.certificate_number}
                    </p>
                    {cert.verification_code && (
                      <p className="text-xs text-muted-foreground font-mono mt-0.5">
                        {cert.verification_code}
                      </p>
                    )}
                  </td>

                  {/* Score */}
                  <td className="px-5 py-3.5 text-sm font-semibold text-foreground font-mono">
                    {cert.final_score ? `${cert.final_score}%` : '—'}
                  </td>

                  {/* Status */}
                  <td className="px-5 py-3.5">
                    <StatusBadge status={cert.status} />
                  </td>

                  {/* Issued at */}
                  <td className="px-5 py-3.5 text-xs text-muted-foreground font-mono">
                    {cert.issued_at ? formatDate(cert.issued_at) : '—'}
                  </td>

                  {/* Actions */}
                  <td className="px-5 py-3.5">
                    <div className="flex gap-2">
                      <Link
                        href={`/dashboard/admin/certificates/${cert.id}`}
                        className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                      >
                        {t.common.view}
                      </Link>
                      {cert.status === 'issued' && (
                        <RevokeButton
                          certId={cert.id}
                          onRevoke={(reason) => handleRevoke(cert.id, reason)}
                          labels={t.certificates}
                        />
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-6">
          {page > 1 && (
            <button
              onClick={() => updateParam('page', String(page - 1))}
              className="btn-ghost text-sm px-4 py-2"
            >
              ← {t.common.previous}
            </button>
          )}
          <span className="text-sm text-muted-foreground font-mono px-4">
            {page} / {totalPages}
          </span>
          {page < totalPages && (
            <button
              onClick={() => updateParam('page', String(page + 1))}
              className="btn-ghost text-sm px-4 py-2"
            >
              {t.common.next} →
            </button>
          )}
        </div>
      )}
    </AdminLayout>
  );
}

// ── Revoke button modal ──────────────────────────────────────────────────────

function RevokeButton({
  certId,
  onRevoke,
  labels,
}: {
  certId: string;
  onRevoke: (reason: string) => void;
  labels: any;
}) {
  const [show, setShow] = useState(false);
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRevoke = async () => {
    setLoading(true);
    try {
      await onRevoke(reason);
      setShow(false);
      setReason('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setShow(true)}
        className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono"
      >
        {labels.revoke}
      </button>
      {show && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShow(false)} />
          <div className="relative bg-card border border-border rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-bold text-foreground mb-2 font-heading">
              {labels.revoke}
            </h3>
            <p className="text-sm text-muted-foreground mb-4 font-body leading-relaxed">
              {labels.revokeWarning}
            </p>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              placeholder={labels.revokeReason}
              className="input resize-none mb-4"
              autoFocus
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShow(false)}
                className="btn-ghost flex-1 text-sm"
              >
                Bekor qilish
              </button>
              <button
                onClick={handleRevoke}
                disabled={loading || !reason.trim()}
                className="btn-danger flex-1 text-sm"
              >
                {loading ? 'Yuklanmoqda...' : labels.revoke}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default function AdminCertificatesPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <CertificatesContent />
    </Suspense>
  );
}