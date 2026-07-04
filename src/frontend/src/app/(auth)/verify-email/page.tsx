'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { GraduationCap } from 'lucide-react';
import { api, handleApiError } from '@/lib/api';
import { useTranslation } from '@/lib/i18n/useTranslation';

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { t } = useTranslation();

  const token = searchParams.get('token');
  const email = searchParams.get('email') ?? '';

  const [status, setStatus] = useState<'pending' | 'verifying' | 'success' | 'error'>('pending');
  const [message, setMessage] = useState('');
  const [resendLoading, setResendLoading] = useState(false);
  const [resendMessage, setResendMessage] = useState('');
  const [resendError, setResendError] = useState('');
  const [countdown, setCountdown] = useState(0);

  // Auto-verify if token present
  useEffect(() => {
    if (!token) return;

    const verify = async () => {
      setStatus('verifying');
      try {
        await api.auth.verifyEmail(token);
        setStatus('success');
        setTimeout(() => router.push('/login?verified=1'), 2500);
      } catch (err) {
        setStatus('error');
        setMessage(handleApiError(err));
      }
    };

    verify();
  }, [token, router]);

  // Countdown for resend
  useEffect(() => {
    if (countdown <= 0) return;
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown]);

  const handleResend = async () => {
    if (!email || resendLoading || countdown > 0) return;
    setResendLoading(true);
    setResendError('');
    setResendMessage('');

    try {
      await api.auth.resendVerification(email);
      setResendMessage(t.auth.verifyEmail.resendSuccess);
      setCountdown(120);
    } catch (err) {
      setResendError(handleApiError(err));
    } finally {
      setResendLoading(false);
    }
  };

  // ── Auto-verify view (with token) ──
  if (token) {
    return (
      <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          {/* Logo */}
          <Link href="/" className="flex items-center justify-center gap-2.5 mb-6">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <GraduationCap size={20} className="text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold text-foreground font-heading tracking-tight">
              LearnFlow
            </span>
          </Link>

          <div className="card py-8 px-4 sm:px-10 text-center">
            {status === 'verifying' && (
              <>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
                <p className="text-muted-foreground font-body">{t.auth.verifyEmail.verifying}</p>
              </>
            )}

            {status === 'success' && (
              <>
                <div
                  className="inline-flex w-20 h-20 rounded-full items-center justify-center text-5xl mb-4"
                  style={{ backgroundColor: 'var(--color-success-bg)' }}
                >
                  ✅
                </div>
                <h2 className="text-2xl font-bold text-success mb-2 font-heading">
                  {t.auth.verifyEmail.success}
                </h2>
                <p className="text-muted-foreground font-body">
                  {t.auth.verifyEmail.successDesc}
                </p>
              </>
            )}

            {status === 'error' && (
              <>
                <div
                  className="inline-flex w-20 h-20 rounded-full items-center justify-center text-5xl mb-4"
                  style={{ backgroundColor: 'var(--color-error-bg)' }}
                >
                  ❌
                </div>
                <h2 className="text-2xl font-bold text-destructive mb-2 font-heading">
                  {t.auth.verifyEmail.failed}
                </h2>
                <p className="text-destructive mb-6 font-body">{message}</p>
                <p className="text-sm text-muted-foreground mb-4 font-body">
                  {t.auth.verifyEmail.failedDesc}
                </p>
                <Link
                  href="/verify-email"
                  className="btn-primary inline-block"
                >
                  {t.auth.verifyEmail.requestNewLink}
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ── Check email view (without token) ──
  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-2.5 mb-6">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <GraduationCap size={20} className="text-primary-foreground" />
          </div>
          <span className="text-2xl font-bold text-foreground font-heading tracking-tight">
            LearnFlow
          </span>
        </Link>

        <div className="card py-8 px-4 sm:px-10">
          {/* Header */}
          <div className="text-center mb-6">
            <div
              className="inline-flex w-20 h-20 rounded-full items-center justify-center text-5xl mb-4"
              style={{ backgroundColor: 'var(--color-info-bg)' }}
            >
              📧
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2 font-heading">
              {t.auth.verifyEmail.title}
            </h2>
            <p className="text-muted-foreground mb-2 font-body">
              {t.auth.verifyEmail.subtitle}:
            </p>
            {email && (
              <p className="font-semibold text-foreground mb-4 break-all font-mono text-sm">
                {email}
              </p>
            )}
          </div>

          {/* Next steps */}
          <div className="bg-info/5 border border-info/30 p-4 rounded-xl mb-6">
            <p className="text-sm text-info mb-3 font-semibold font-body">
              {t.auth.verifyEmail.nextSteps}
            </p>
            <ol className="text-sm text-foreground list-decimal list-inside space-y-2 font-body">
              <li>{t.auth.verifyEmail.step1} ({email})</li>
              <li>{t.auth.verifyEmail.step2}</li>
              <li>{t.auth.verifyEmail.step3}</li>
              <li>{t.auth.verifyEmail.step4}</li>
            </ol>
            <p className="text-xs text-muted-foreground mt-3 font-body">
              {t.auth.verifyEmail.linkValid}
            </p>
          </div>

          {/* Resend section */}
          <div className="border-t border-border pt-6">
            <p className="text-center text-sm text-muted-foreground mb-3 font-body">
              {t.auth.verifyEmail.noEmail}
            </p>

            {resendMessage && (
              <div className="mb-3 bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm font-body">
                {resendMessage}
              </div>
            )}
            {resendError && (
              <div className="mb-3 bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
                {resendError}
              </div>
            )}

            <button
              onClick={handleResend}
              disabled={resendLoading || countdown > 0 || !email}
              className="btn-ghost w-full"
            >
              {resendLoading
                ? t.auth.verifyEmail.resending
                : countdown > 0
                ? t.auth.verifyEmail.resendCountdown.replace('{seconds}', String(countdown))
                : t.auth.verifyEmail.resend}
            </button>

            {!email && (
              <p className="mt-2 text-center text-xs text-muted-foreground font-body">
                <Link href="/register" className="text-primary hover:text-primary/80">
                  {t.auth.verifyEmail.registerFirst}
                </Link>
              </p>
            )}

            <p className="mt-4 text-center text-xs text-muted-foreground font-body">
              {t.auth.verifyEmail.spamHint}
            </p>
          </div>

          {/* Back to login */}
          <div className="mt-6 text-center">
            <Link href="/login" className="text-sm text-primary hover:text-primary/80 font-semibold font-body">
              {t.auth.verifyEmail.backToLogin}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}