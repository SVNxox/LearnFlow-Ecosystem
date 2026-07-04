'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { GraduationCap } from 'lucide-react';
import { api, handleApiError } from '@/lib/api';
import { CertificateVerificationResult } from '@/types/api';
import { LoadingSpinner } from '@/components/ui';
import { formatDate } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

export default function VerifyCertificatePage() {
  const params = useParams<{ code: string }>();
  const { t } = useTranslation();
  const [result, setResult] = useState<CertificateVerificationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    api.certificates
      .verifyCertificate(params.code)
      .then((data) => active && setResult(data))
      .catch((err) => active && setError(handleApiError(err)))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [params.code]);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <nav className="h-16 flex items-center px-6 border-b border-border bg-card/50 backdrop-blur-sm">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <GraduationCap size={16} className="text-primary-foreground" />
          </div>
          <span className="text-lg font-bold text-foreground font-heading tracking-tight">
            LearnFlow
          </span>
        </Link>
        <span className="ml-auto text-xs text-muted-foreground font-mono">
          {t.certificateVerify.title}
        </span>
      </nav>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        {loading ? (
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="text-sm text-muted-foreground mt-4 font-body">
              {t.certificateVerify.verifying}
            </p>
          </div>
        ) : result?.valid ? (
          <div className="max-w-md w-full">
            {/* Success header */}
            <div className="text-center mb-6">
              <div
                className="inline-flex w-20 h-20 rounded-full items-center justify-center text-5xl mb-4"
                style={{ backgroundColor: 'var(--color-success-bg)' }}
              >
                ✅
              </div>
              <h1 className="text-2xl font-bold text-success font-heading">
                {t.certificateVerify.valid}
              </h1>
            </div>

            {/* Certificate details */}
            <div className="card p-6 space-y-4">
              <Row label={t.certificateVerify.student} value={result.student_name} />
              <Row label={t.certificateVerify.course} value={result.course_title} />
              <Row
                label={t.certificateVerify.completionDate}
                value={result.completion_date ? formatDate(result.completion_date) : undefined}
              />
              <Row
                label={t.certificateVerify.issuedAt}
                value={result.issued_at ? formatDate(result.issued_at) : undefined}
              />
              <Row label={t.certificateVerify.certificateNumber} value={result.certificate_number} />
              {result.final_score && (
                <Row label={t.certificateVerify.finalScore} value={`${result.final_score}`} />
              )}
            </div>

            {/* Back button */}
            <div className="mt-6 text-center">
              <Link href="/" className="text-sm text-primary hover:text-primary/80 font-body">
                ← {t.certificateVerify.backToHome}
              </Link>
            </div>
          </div>
        ) : (
          <div className="max-w-md w-full text-center">
            <div className="card p-8">
              <div
                className="inline-flex w-20 h-20 rounded-full items-center justify-center text-5xl mb-4"
                style={{ backgroundColor: 'var(--color-error-bg)' }}
              >
                ❌
              </div>
              <h1 className="text-2xl font-bold text-destructive mb-2 font-heading">
                {t.certificateVerify.invalid}
              </h1>
              <p className="text-sm text-muted-foreground mb-6 font-body">
                {result?.detail || error || t.certificateVerify.invalidDesc}
              </p>
              <Link href="/" className="btn-primary inline-block">
                ← {t.certificateVerify.backToHome}
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="text-center text-xs text-muted-foreground py-6 font-mono border-t border-border">
        ✨ {t.certificateVerify.verifiedBy}
      </footer>
    </div>
  );
}

function Row({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <div className="flex items-center justify-between text-sm py-2 border-b border-border last:border-0">
      <span className="text-muted-foreground font-body">{label}</span>
      <span className="font-semibold text-foreground font-mono text-right max-w-[60%] break-words">
        {value}
      </span>
    </div>
  );
}