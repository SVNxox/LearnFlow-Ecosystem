'use client';

import { useState, FormEvent, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { GraduationCap } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useTranslation } from '@/lib/i18n/useTranslation';

function LoginContent() {
  const { login } = useAuth();
  const searchParams = useSearchParams();
  const { t } = useTranslation();
  const verified = searchParams.get('verified') === '1';
  const reset = searchParams.get('reset') === '1';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ email, password });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Background glow */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at top, rgba(129,140,248,0.15) 0%, transparent 70%)',
        }}
      />

      <div className="relative sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-2.5 mb-6">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <GraduationCap size={20} className="text-primary-foreground" />
          </div>
          <span className="text-2xl font-bold text-foreground font-heading tracking-tight">
            LearnFlow
          </span>
        </Link>

        {/* Header */}
        <h2 className="text-center text-2xl font-bold text-foreground font-heading">
          {t.auth.login.title}
        </h2>
        <p className="mt-2 text-center text-sm text-muted-foreground font-body">
          {t.auth.login.subtitle}
        </p>
        <p className="mt-4 text-center text-sm text-muted-foreground font-body">
          {t.auth.login.noAccount}{' '}
          <Link href="/register" className="font-semibold text-primary hover:text-primary/80">
            {t.auth.login.createAccount}
          </Link>
        </p>
      </div>

      <div className="relative mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card py-8 px-4 sm:px-10">
          {/* Success messages */}
          {verified && (
            <div className="mb-4 bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm font-body">
              {t.auth.login.verified}
            </div>
          )}

          {reset && (
            <div className="mb-4 bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm font-body">
              {t.auth.login.resetSuccess}
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            {/* Error */}
            {error && (
              <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
                {error}
              </div>
            )}

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.auth.login.email}
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.auth.login.password}
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
              />
            </div>

            {/* Remember me & Forgot */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary/30"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-foreground font-body">
                  {t.auth.login.rememberMe}
                </label>
              </div>
              <div className="text-sm">
                <Link href="/password-reset" className="font-semibold text-primary hover:text-primary/80 font-body">
                  {t.auth.login.forgotPassword}
                </Link>
              </div>
            </div>

            {/* Submit */}
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
                  {t.auth.login.submitting}
                </span>
              ) : (
                `🔐 ${t.auth.login.submit}`
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" />
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
}