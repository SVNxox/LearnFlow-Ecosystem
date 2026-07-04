'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { api, handleApiError } from '@/lib/api';
import { Certificate } from '@/types/api';
import { LoadingSpinner, EmptyState, StatusBadge } from '@/components/ui';
import { formatDate } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

export default function CertificatesPage() {
  const { t } = useTranslation();
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    api.certificates
      .getMyCertificates()
      .then((data) => active && setCertificates(data))
      .catch((err) => active && setError(handleApiError(err)))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  const handleDownload = async (cert: Certificate) => {
    setDownloadingId(cert.id);
    try {
      const { download_url } = await api.certificates.downloadCertificate(cert.id);
      window.open(download_url, '_blank');
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setDownloadingId(null);
    }
  };

  const handleShare = async (cert: Certificate) => {
    const url = `${window.location.origin}/certificates/verify/${cert.verification_code}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopiedId(cert.id);
      setTimeout(() => setCopiedId(null), 1500);
    } catch {
      // ignore
    }
  };

  return (
    <DashboardLayout allowedRoles={['student']}>
      {/* Header */}
      <div className="mb-6 mt-10">
        <h1 className="text-2xl font-bold text-foreground font-heading">
          {t.myCertificates.title}
        </h1>
        <p className="text-sm text-muted-foreground mt-1 font-body">
          {t.myCertificates.subtitle}
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-6 font-body">
          {error}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : certificates.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="text-5xl mb-4">🎓</div>
          <h3 className="text-lg font-semibold text-foreground mb-2 font-heading">
            {t.myCertificates.noCertificates}
          </h3>
          <p className="text-sm text-muted-foreground max-w-sm mx-auto font-body">
            {t.myCertificates.noCertificatesDesc}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          {certificates.map((cert) => (
            <div
              key={cert.id}
              className="card p-6 hover:border-primary/30 transition-all duration-200"
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-3 mb-4">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                    style={{ backgroundColor: 'var(--color-accent)' + '20' }}
                  >
                    🎓
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-foreground leading-snug font-heading">
                      {cert.course_name_snapshot}
                    </h3>
                    <StatusBadge status={cert.status} />
                  </div>
                </div>
              </div>

              {/* Info */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground font-body">
                    {t.myCertificates.issuedAt}:
                  </span>
                  <span className="text-foreground font-mono text-xs">
                    {formatDate(cert.issued_at)}
                  </span>
                </div>
                {cert.final_score != null && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground font-body">
                      {t.myCertificates.finalScore}:
                    </span>
                    <span className="text-foreground font-semibold font-mono">
                      {cert.final_score}
                    </span>
                  </div>
                )}
              </div>

              {/* Verification code */}
              <button
                onClick={() => handleShare(cert)}
                className="w-full text-left text-xs text-muted-foreground hover:text-foreground mb-4 px-3 py-2 rounded-lg bg-muted font-mono truncate transition-colors"
              >
                🔑 {cert.verification_code}
                <span className="ml-2 text-primary">
                  ({copiedId === cert.id ? t.myCertificates.copied : t.myCertificates.copyCode})
                </span>
              </button>

              {/* Actions */}
              <div className="flex gap-2">
                {cert.status === 'issued' && (
                  <button
                    onClick={() => handleDownload(cert)}
                    disabled={downloadingId === cert.id}
                    className="btn-primary flex-1 text-sm"
                  >
                    {downloadingId === cert.id
                      ? t.myCertificates.downloading
                      : t.myCertificates.downloadPdf}
                  </button>
                )}
                <button
                  onClick={() => handleShare(cert)}
                  className="btn-ghost text-sm"
                >
                  {t.myCertificates.share}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}