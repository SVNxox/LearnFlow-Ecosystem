'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { useAuth } from '@/lib/auth-context';
import { api, handleApiError } from '@/lib/api';
import { UserSession, UserSettings } from '@/types/api';
import { ConfirmModal } from '@/components/ui';
import { formatDateTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

type Tab = 'profile' | 'security' | 'notifications' | 'sessions';

export default function ProfilePage() {
  const { user, refreshUser, logout } = useAuth();
  const { t } = useTranslation();
  const [tab, setTab] = useState<Tab>('profile');

  const tabs: { key: Tab; labelKey: keyof typeof t.profile.tabs }[] = [
    { key: 'profile', labelKey: 'profile' },
    { key: 'security', labelKey: 'security' },
    { key: 'notifications', labelKey: 'notifications' },
    { key: 'sessions', labelKey: 'sessions' },
  ];

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-6 mt-10">
        <h1 className="text-2xl font-bold text-foreground font-heading">
          {t.profile.title}
        </h1>
        <p className="text-sm text-muted-foreground mt-1 font-body">
          {t.profile.subtitle}
        </p>
      </div>

      {/* Tabs */}
      <div className="filter-pills mb-6">
        {tabs.map(({ key, labelKey }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`filter-pill ${tab === key ? 'filter-pill-active' : 'filter-pill-inactive'}`}
          >
            {t.profile.tabs[labelKey]}
          </button>
        ))}
      </div>

      <div className="max-w-xl">
        {tab === 'profile' && user && <ProfileTab user={user} onSaved={refreshUser} />}
        {tab === 'security' && <SecurityTab />}
        {tab === 'notifications' && <NotificationsTab />}
        {tab === 'sessions' && <SessionsTab onLogoutAll={logout} />}
      </div>
    </DashboardLayout>
  );
}

function ProfileTab({ user, onSaved }: { user: NonNullable<ReturnType<typeof useAuth>['user']>; onSaved: () => Promise<void> }) {
  const { t } = useTranslation();
  const [firstName, setFirstName] = useState(user.info?.first_name || '');
  const [lastName, setLastName] = useState(user.info?.last_name || '');
  const [phone, setPhone] = useState(user.info?.phone || '');
  const [bio, setBio] = useState(user.info?.bio || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const initials = `${user.info?.first_name?.[0] || user.email[0]}${user.info?.last_name?.[0] || ''}`.toUpperCase();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess(false);
    try {
      await api.auth.updateProfile({ first_name: firstName, last_name: lastName, phone, bio });
      await onSaved();
      setSuccess(true);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card p-6 space-y-5">
      {/* Avatar */}
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xl font-bold font-heading">
          {initials}
        </div>
        <div>
          <p className="font-semibold text-foreground font-heading">{user.info?.first_name} {user.info?.last_name}</p>
          <p className="text-sm text-muted-foreground font-mono">{user.email}</p>
        </div>
      </div>

      {/* Name fields */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
            {t.profile.profileTab.firstName}
          </label>
          <input
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            className="input"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
            {t.profile.profileTab.lastName}
          </label>
          <input
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            className="input"
          />
        </div>
      </div>

      {/* Phone */}
      <div>
        <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
          {t.profile.profileTab.phone}
        </label>
        <input
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder={t.profile.profileTab.phonePlaceholder}
          className="input font-mono"
        />
      </div>

      {/* Bio */}
      <div>
        <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
          {t.profile.profileTab.bio}
        </label>
        <textarea
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          rows={3}
          className="input resize-none"
        />
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm font-body">
          {t.profile.profileTab.saved}
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={saving}
        className="btn-primary"
      >
        {saving ? t.profile.profileTab.saving : `💾 ${t.profile.profileTab.save}`}
      </button>
    </form>
  );
}

function SecurityTab() {
  const { t } = useTranslation();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    if (newPassword !== confirmPassword) {
      setError(t.profile.securityTab.passwordMismatch);
      return;
    }
    setSaving(true);
    try {
      await api.auth.changePassword({ old_password: oldPassword, new_password: newPassword });
      setSuccess(true);
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card p-6 space-y-5">
      <div>
        <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
          🔒 {t.profile.securityTab.currentPassword}
        </label>
        <input
          type="password"
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
          required
          className="input"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
          🔑 {t.profile.securityTab.newPassword}
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
          🔑 {t.profile.securityTab.confirmPassword}
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
      {success && (
        <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm font-body">
          {t.profile.securityTab.success}
        </div>
      )}

      <button
        type="submit"
        disabled={saving}
        className="btn-primary"
      >
        {saving ? t.profile.securityTab.saving : `🔐 ${t.profile.securityTab.changePassword}`}
      </button>
    </form>
  );
}

function NotificationsTab() {
  const { t } = useTranslation();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.auth
      .getSettings()
      .then(setSettings)
      .catch((err) => setError(handleApiError(err)))
      .finally(() => setLoading(false));
  }, []);

  const toggle = async (key: keyof UserSettings) => {
    if (!settings) return;
    const updated = { ...settings, [key]: !settings[key] };
    setSettings(updated);
    setSaving(true);
    setError('');
    try {
      const result = await api.auth.updateSettings({ [key]: updated[key] });
      setSettings(result);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
      </div>
    );
  }
  if (!settings) {
    return (
      <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
        {error}
      </div>
    );
  }

  const rows: { key: keyof UserSettings; labelKey: keyof typeof t.profile.notificationsTab; icon: string }[] = [
    { key: 'notify_email', labelKey: 'email', icon: '📧' },
    { key: 'notify_telegram', labelKey: 'telegram', icon: '✈️' },
    { key: 'notify_web', labelKey: 'web', icon: '🌐' },
  ];

  return (
    <div className="card p-6 space-y-4">
      {rows.map((row) => (
        <div
          key={row.key}
          className="flex items-center justify-between p-3 rounded-xl hover:bg-muted/30 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="text-xl">{row.icon}</span>
            <span className="text-sm text-foreground font-body">
              {t.profile.notificationsTab[row.labelKey]}
            </span>
          </div>
          <button
            onClick={() => toggle(row.key)}
            disabled={saving}
            className={`relative w-11 h-6 rounded-full transition-colors ${
              settings[row.key] ? 'bg-primary' : 'bg-muted'
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 w-5 h-5 bg-primary-foreground rounded-full transition-transform ${
                settings[row.key] ? 'translate-x-5' : ''
              }`}
            />
          </button>
        </div>
      ))}
    </div>
  );
}

function SessionsTab({ onLogoutAll }: { onLogoutAll: () => void }) {
  const { t } = useTranslation();
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [revoking, setRevoking] = useState<string | null>(null);
  const [confirmLogoutAll, setConfirmLogoutAll] = useState(false);
  const [loggingOutAll, setLoggingOutAll] = useState(false);

  const load = () => {
    setLoading(true);
    api.auth
      .getSessions()
      .then(setSessions)
      .catch((err) => setError(handleApiError(err)))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleRevoke = async (id: string) => {
    setRevoking(id);
    try {
      await api.auth.revokeSession(id);
      load();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setRevoking(null);
    }
  };

  const handleLogoutAll = async () => {
    setLoggingOutAll(true);
    try {
      await api.auth.logoutAll();
    } catch {
      // ignore
    } finally {
      onLogoutAll();
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
        </div>
      ) : sessions.length === 0 ? (
        <div className="card p-8 text-center">
          <div className="text-4xl mb-3">🔒</div>
          <p className="text-sm text-muted-foreground font-body">
            {t.profile.sessionsTab.noSessions}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map((s) => (
            <div
              key={s.id}
              className="card p-4 flex items-center justify-between gap-4"
            >
              <div className="flex items-start gap-3 min-w-0 flex-1">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                  style={{ backgroundColor: 'var(--color-info)' + '15' }}
                >
                  💻
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-foreground font-body truncate">
                    {s.device_name || t.profile.sessionsTab.unknownDevice}
                  </p>
                  <p className="text-xs text-muted-foreground font-mono mt-0.5">
                    {s.ip_address && `${s.ip_address} · `}
                    {formatDateTime(s.created_at)}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleRevoke(s.id)}
                disabled={revoking === s.id}
                className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono disabled:opacity-50 flex-shrink-0"
              >
                {revoking === s.id ? '...' : t.profile.sessionsTab.revoke}
              </button>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={() => setConfirmLogoutAll(true)}
        className="btn-danger w-full"
      >
        {t.profile.sessionsTab.logoutAll}
      </button>

      <ConfirmModal
        open={confirmLogoutAll}
        title={t.profile.sessionsTab.logoutAllConfirm}
        description={t.profile.sessionsTab.logoutAllDesc}
        confirmLabel={t.profile.sessionsTab.logoutAllButton}
        danger
        loading={loggingOutAll}
        onConfirm={handleLogoutAll}
        onCancel={() => setConfirmLogoutAll(false)}
      />
    </div>
  );
}