'use client';

import { useState } from 'react';
import Link from 'next/link';
import { GraduationCap } from 'lucide-react';
import { api, handleApiError } from '@/lib/api';
import { useTranslation } from '@/lib/i18n/useTranslation';

export default function PasswordResetRequestPage() {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.auth.requestPasswordReset(email);
      setSent(true);
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
            {t.passwordReset.request.title}
          </h1>
          <p className="text-sm text-muted-foreground mb-6 font-body">
            {t.passwordReset.request.subtitle}
          </p>

          {sent ? (
            <div className="bg-info/5 border border-info/30 text-info px-4 py-3 rounded-xl text-sm font-body">
              ✅ {t.passwordReset.request.success}
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                  {t.passwordReset.request.email}
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
                    {t.passwordReset.request.submitting}
                  </span>
                ) : (
                  `📧 ${t.passwordReset.request.submit}`
                )}
              </button>
            </form>
          )}

          <Link
            href="/login"
            className="block text-center text-sm text-muted-foreground hover:text-foreground mt-4 font-body"
          >
            {t.passwordReset.request.backToLogin}
          </Link>
        </div>
      </div>
    </div>
  );
}