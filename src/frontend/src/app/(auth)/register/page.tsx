'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { GraduationCap } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useTranslation } from '@/lib/i18n/useTranslation';

export default function RegisterPage() {
  const { register } = useAuth();
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError(t.auth.register.errors.passwordMismatch);
      return;
    }
    if (formData.password.length < 8) {
      setError(t.auth.register.errors.passwordLength);
      return;
    }

    setLoading(true);
    try {
      await register({
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-4 sm:px-6 lg:px-8">
      {/* Background glow */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at top, rgba(129,140,248,0.15) 0%, transparent 70%)',
        }}
      />

      <div className="relative sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo - компактный */}
        <Link href="/" className="flex items-center justify-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <GraduationCap size={16} className="text-primary-foreground" />
          </div>
          <span className="text-xl font-bold text-foreground font-heading tracking-tight">
            LearnFlow
          </span>
        </Link>

        {/* Header - компактный */}
        <h2 className="text-center text-xl font-bold text-foreground font-heading mb-1">
          {t.auth.register.title}
        </h2>
        <p className="text-center text-sm text-muted-foreground font-body mb-4">
          {t.auth.register.hasAccount}{' '}
          <Link href="/login" className="font-semibold text-primary hover:text-primary/80">
            {t.auth.register.signIn}
          </Link>
        </p>
      </div>

      <div className="relative sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card py-5 px-5 sm:px-6">
          <form className="space-y-3" onSubmit={handleSubmit}>
            {/* Error */}
            {error && (
              <div className="bg-destructive/10 border border-destructive/30 text-destructive px-3 py-2 rounded-lg text-xs font-body">
                {error}
              </div>
            )}

            {/* Name fields - в одну строку */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="first_name" className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.auth.register.firstName}
                </label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={handleChange}
                  className="input py-2 text-sm"
                />
              </div>
              <div>
                <label htmlFor="last_name" className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.auth.register.lastName}
                </label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={handleChange}
                  className="input py-2 text-sm"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-xs font-medium text-foreground mb-1 font-body">
                {t.auth.register.email}
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="input py-2 text-sm"
              />
            </div>

            {/* Password fields - в одну строку */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="password" className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.auth.register.password}
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="input py-2 text-sm"
                />
              </div>
              <div>
                <label htmlFor="confirmPassword" className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.auth.register.confirmPassword}
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="input py-2 text-sm"
                />
              </div>
            </div>

            {/* Password hint - компактный */}
            <p className="text-xs text-muted-foreground font-body -mt-1">
              {t.auth.register.passwordHint}
            </p>

            {/* Submit - компактная кнопка */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-2.5 text-sm"
            >
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  {t.auth.register.submitting}
                </span>
              ) : (
                `✨ ${t.auth.register.submit}`
              )}
            </button>
          </form>

          {/* Terms - компактный */}
          <p className="text-center text-xs text-muted-foreground font-body mt-3">
            {t.auth.register.terms}
          </p>
        </div>
      </div>
    </div>
  );
}