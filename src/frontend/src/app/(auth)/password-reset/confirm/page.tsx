'use client';

import { Suspense, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { GraduationCap } from 'lucide-react';
import { api, handleApiError } from '@/lib/api';
import { useTranslation } from '@/lib/i18n/useTranslation';

function ConfirmForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { t } = useTranslation();
  const token = searchParams.get('token') || '';

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (newPassword !== confirmPassword) {
      setError(t.passwordReset.confirm.errors.passwordMismatch);
      return;
    }
    if (!token) {
      setError(t.passwordReset.confirm.errors.invalidToken);
      return;
    }
    setLoading(true);
    try {
      await api.auth.confirmPasswordReset({ token, new_password: newPassword });
      router.push('/login?reset=1');
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      {/* Background glow */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at top, rgba(129,140,248,0.15) 0%, transparent 70%)',
        }}
      />

      <div className="relative max-w-sm w-full">
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-2.5 mb-8">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <GraduationCap size={20} className="text-primary-foreground" />
          </div>
          <span className="text-2xl font-bold text-foreground font-heading tracking-tight">
            LearnFlow
          </span>
        </Link>

        <div className="card p-6">
          <h1 className="text-lg font-semibold text-foreground mb-1 font-heading">
            {t.passwordReset.confirm.title}
          </h1>
          <p className="text-sm text-muted-foreground mb-6 font-body">
            {t.passwordReset.confirm.subtitle}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                🔑 {t.passwordReset.confirm.newPassword}
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                🔑 {t.passwordReset.confirm.confirmPassword}
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="input"
              />
            </div>

            {error && (
              <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  {t.passwordReset.confirm.submitting}
                </span>
              ) : (
                `🔐 ${t.passwordReset.confirm.submit}`
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function PasswordResetConfirmPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    }>
      <ConfirmForm />
    </Suspense>
  );
}