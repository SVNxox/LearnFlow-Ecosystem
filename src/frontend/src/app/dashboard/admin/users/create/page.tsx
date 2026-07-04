'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { CreateUserBody } from '@/types/api';
import { useTranslation } from '@/lib/i18n/useTranslation';

function generatePassword() {
  const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789@
  return Array.from({ length: 16 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}

// Компонент input вынесен на верхний уровень
const F = ({
  label,
  name,
  type = 'text',
  form,
  setForm,
  ...props
}: {
  label: string;
  name: keyof CreateUserBody;
  type?: string;
  form: CreateUserBody;
  setForm: React.Dispatch<React.SetStateAction<CreateUserBody>>;
  [k: string]: unknown;
}) => {
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setForm((f) => ({ ...f, [name]: value }));
  }, [name, setForm]);

  return (
    <div>
      <label className="block text-sm font-medium text-foreground mb-1.5 font-body">{label}</label>
      <input
        type={type}
        value={String(form[name] ?? '')}
        onChange={handleChange}
        className="input"
        {...props as React.InputHTMLAttributes<HTMLInputElement>}
      />
    </div>
  );
};

export default function CreateUserPage() {
  const router = useRouter();
  const { t } = useTranslation();

  const [form, setForm] = useState<CreateUserBody>({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'student',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const [createdUser, setCreatedUser] = useState<{
    id: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role: string;
  } | null>(null);

  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const user = await adminApi.createUser(form);
      setCreatedUser({
        id: user.id,
        email: form.email,
        password: form.password,
        first_name: form.first_name,
        last_name: form.last_name,
        role: form.role,
      });
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const handleCopyPassword = useCallback(async () => {
    if (!createdUser) return;
    try {
      await navigator.clipboard.writeText(createdUser.password);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [createdUser]);

  const handleCopyCredentials = useCallback(async () => {
    if (!createdUser) return;
    const text = `Email: ${createdUser.email}\nPassword: ${createdUser.password}`;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [createdUser]);

  const handleCreateAnother = () => {
    setCreatedUser(null);
    setForm({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: 'student',
    });
    setError('');
  };

  const handlePasswordGenerate = useCallback(() => {
    setForm((f) => ({ ...f, password: generatePassword() }));
  }, []);

  const handleRoleChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setForm((f) => ({ ...f, role: e.target.value as CreateUserBody['role'] }));
  }, []);

  // ✅ ЭКРАН УСПЕХА
  if (createdUser) {
    return (
      <AdminLayout roles={['admin']}>
        <Link
          href="/dashboard/admin/users"
          className="text-sm text-muted-foreground hover:text-foreground mb-4 inline-block font-body"
        >
          ← {t.users.backToList}
        </Link>

        <div className="max-w-lg mx-auto">
          {/* Заголовок успеха */}
          <div className="bg-success/10 border border-success/30 rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="flex-shrink-0 w-10 h-10 bg-success rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-primary-foreground"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-success font-heading">
                {t.users.userCreated}
              </h2>
            </div>
            <p className="text-sm text-success ml-13 font-body">
              {createdUser.first_name} {createdUser.last_name} ({createdUser.email})
            </p>
          </div>

          {/* Карточка с учётными данными */}
          <div className="card p-6 mb-6">
            <h3 className="text-lg font-semibold text-foreground mb-4 font-heading">
              🔐 {t.users.credentials}
            </h3>
            <p className="text-sm text-destructive mb-4 bg-destructive/10 border border-destructive/30 rounded-xl p-3 font-body">
              ⚠️ <strong>{t.users.importantWarning}</strong>
            </p>

            {/* Email */}
            <div className="mb-4">
              <label className="block text-xs font-medium text-muted-foreground mb-1 font-mono uppercase">
                {t.users.email}
              </label>
              <div className="flex items-center gap-2">
                <code className="flex-1 bg-muted border border-border rounded-lg px-3 py-2 text-sm font-mono text-foreground break-all">
                  {createdUser.email}
                </code>
              </div>
            </div>

            {/* Password */}
            <div className="mb-4">
              <label className="block text-xs font-medium text-muted-foreground mb-1 font-mono uppercase">
                {t.users.password}
              </label>
              <div className="flex items-center gap-2">
                <code className="flex-1 bg-warning/10 border border-warning/30 rounded-lg px-3 py-2 text-sm font-mono text-foreground break-all">
                  {createdUser.password}
                </code>
                <button
                  type="button"
                  onClick={handleCopyPassword}
                  className="btn-primary text-sm flex-shrink-0"
                >
                  {copied ? t.users.copied : t.users.copy}
                </button>
              </div>
            </div>

            {/* Кнопка копирования всего */}
            <button
              type="button"
              onClick={handleCopyCredentials}
              className="btn-ghost w-full text-sm mb-4"
            >
              {t.users.copyCredentials}
            </button>

            {/* Информация о роли */}
            <div className="text-sm text-foreground font-body">
              <span className="text-muted-foreground">{t.users.role}:</span>{' '}
              <span className="px-2 py-1 bg-primary/20 text-primary rounded-lg text-xs font-semibold font-mono">
                {t.users.roles[createdUser.role as keyof typeof t.users.roles]}
              </span>
            </div>
          </div>

          {/* Кнопки действий */}
          <div className="flex flex-col gap-2">
            <Link
              href={`/dashboard/admin/users/${createdUser.id}`}
              className="btn-primary w-full"
            >
              {t.users.goToUser}
            </Link>
            <button
              type="button"
              onClick={handleCreateAnother}
              className="btn-ghost w-full"
            >
              {t.users.createAnother}
            </button>
            <Link
              href="/dashboard/admin/users"
              className="w-full text-center text-sm text-muted-foreground hover:text-foreground py-2 font-body"
            >
              ← {t.users.backToList}
            </Link>
          </div>
        </div>
      </AdminLayout>
    );
  }

  // ✅ ЭКРАН ФОРМЫ
  return (
    <AdminLayout roles={['admin']}>
      <Link
        href="/dashboard/admin/users"
        className="text-sm text-muted-foreground hover:text-foreground mb-4 inline-block font-body"
      >
        ← {t.users.backToList}
      </Link>
      <h1 className="text-xl font-bold text-foreground mb-6 font-heading">{t.users.createUser}</h1>

      <div className="max-w-md card p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <F label={t.users.firstNameRequired} name="first_name" form={form} setForm={setForm} required />
            <F label={t.users.lastNameRequired} name="last_name" form={form} setForm={setForm} required />
          </div>
          <F label={t.users.emailRequired} name="email" type="email" form={form} setForm={setForm} required />

          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
              {t.users.passwordRequired}
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={form.password}
                onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                required
                className="input flex-1 font-mono"
              />
              <button
                type="button"
                onClick={handlePasswordGenerate}
                className="btn-ghost text-xs px-3 whitespace-nowrap"
              >
                {t.users.generate}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
              {t.users.roleRequired}
            </label>
            <select
              value={form.role}
              onChange={handleRoleChange}
              className="input"
            >
              <option value="student">{t.users.roles.student}</option>
              <option value="mentor">{t.users.roles.mentor}</option>
              <option value="staff">{t.users.roles.staff}</option>
              <option value="admin">{t.users.roles.admin}</option>
            </select>
          </div>

          {error && (
            <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="btn-primary w-full"
          >
            {saving ? (
              <>
                <svg
                  className="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                {t.users.creating}
              </>
            ) : (
              t.users.createUser
            )}
          </button>
        </form>
      </div>
    </AdminLayout>
  );
}