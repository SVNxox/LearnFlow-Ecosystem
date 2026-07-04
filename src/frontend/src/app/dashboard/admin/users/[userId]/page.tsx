'use client';

import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { AdminUser, UserSession } from '@/types/api';
import { StatusBadge } from '@/components/ui';
import { formatDateTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

type Tab = 'profile' | 'sessions';

export default function AdminUserDetailPage() {
  const { userId } = useParams<{ userId: string }>();
  const sp = useSearchParams();
  const { t } = useTranslation();
  const justCreated = sp.get('created') === '1';

  const [user, setUser] = useState<AdminUser | null>(null);
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState<Tab>('profile');

  // Profile edit
  const [editForm, setEditForm] = useState({ first_name: '', last_name: '', phone: '', bio: '' });
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Modals
  const [blockModal, setBlockModal] = useState(false);
  const [blockReason, setBlockReason] = useState('');
  const [roleModal, setRoleModal] = useState(false);
  const [newRole, setNewRole] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getUser(userId);
      setUser(data);
      setEditForm({
        first_name: data.info?.first_name || '',
        last_name: data.info?.last_name || '',
        phone: data.info?.phone || '',
        bio: data.info?.bio || '',
      });
      setNewRole(data.roles[0] || 'student');
    } catch (err) { setError(handleApiError(err)); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [userId]);

  const loadSessions = async () => {
    try { setSessions(await adminApi.getUserSessions(userId)); } catch {}
  };

  useEffect(() => { if (tab === 'sessions') loadSessions(); }, [tab]);

  const handleSaveProfile = async () => {
    setSaving(true); setSaveSuccess(false);
    try {
      await adminApi.updateUser(userId, editForm);
      setSaveSuccess(true);
      load();
    } catch (err) { setError(handleApiError(err)); }
    finally { setSaving(false); }
  };

  const handleBlockToggle = async () => {
    setActionLoading(true);
    try {
      if (user?.is_blocked) await adminApi.unblockUser(userId);
      else await adminApi.blockUser(userId, blockReason);
      setBlockModal(false);
      setBlockReason('');
      load();
    } catch (err) { setError(handleApiError(err)); }
    finally { setActionLoading(false); }
  };

  const handleChangeRole = async () => {
    setActionLoading(true);
    try {
      await adminApi.changeUserRole(userId, newRole);
      setRoleModal(false);
      load();
    } catch (err) { setError(handleApiError(err)); }
    finally { setActionLoading(false); }
  };

  const handleRevokeAllSessions = async () => {
    if (!confirm(t.users.revokeAllConfirm)) return;
    try { await adminApi.revokeAllUserSessions(userId); loadSessions(); } catch {}
  };

  if (loading) {
    return (
      <AdminLayout roles={['admin']}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
        </div>
      </AdminLayout>
    );
  }

  if (!user) {
    return (
      <AdminLayout roles={['admin']}>
        <div className="text-center py-12">
          <div className="text-5xl mb-4">👤</div>
          <p className="text-destructive mb-4 font-body">{error || t.users.userNotFound}</p>
          <Link href="/dashboard/admin/users" className="text-primary hover:underline font-body">
            ← {t.users.backToUsers}
          </Link>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout roles={['admin']}>
      {/* Breadcrumb */}
      <Link
        href="/dashboard/admin/users"
        className="text-sm text-muted-foreground hover:text-foreground mb-4 inline-block font-body"
      >
        ← {t.users.backToUsers}
      </Link>

      {/* Success message */}
      {justCreated && (
        <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm mb-4">
          ✓ {t.users.userCreated}
        </div>
      )}

      {/* Header */}
      <div className="flex items-start gap-6 mb-6">
        <div className="w-16 h-16 rounded-full bg-primary/20 text-primary flex items-center justify-center text-2xl font-bold flex-shrink-0 font-heading">
          {(user.info?.first_name?.[0] || user.email[0]).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold text-foreground font-heading">
            {user.info?.first_name} {user.info?.last_name}
          </h1>
          <p className="text-sm text-muted-foreground font-mono mt-1">{user.email}</p>
          <div className="flex items-center gap-2 mt-3 flex-wrap">
            {user.roles.map((r) => (
              <StatusBadge key={r} status={r} />
            ))}
            <StatusBadge status={user.is_blocked ? 'blocked' : 'active'} />
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setRoleModal(true)}
            className="btn-ghost text-xs"
          >
            {t.users.changeRole}
          </button>
          <button
            onClick={() => setBlockModal(true)}
            className={user.is_blocked ? 'btn-primary text-xs' : 'btn-danger text-xs'}
          >
            {user.is_blocked ? t.users.unblockUser : t.users.blockUser}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border mb-6">
        {(['profile', 'sessions'] as Tab[]).map((tTab) => (
          <button
            key={tTab}
            onClick={() => setTab(tTab)}
            className={`pb-3 px-4 text-sm font-semibold capitalize transition-colors ${
              tab === tTab
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {t.users[tTab]}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="max-w-2xl">
        {tab === 'profile' && (
          <div className="card p-6 space-y-4">
            {/* Error */}
            {error && (
              <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm">
                {error}
              </div>
            )}

            {/* Success */}
            {saveSuccess && (
              <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm">
                {t.users.saved}
              </div>
            )}

            {/* Form */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                  {t.users.firstName}
                </label>
                <input
                  value={editForm.first_name}
                  onChange={(e) => setEditForm((f) => ({ ...f, first_name: e.target.value }))}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                  {t.users.lastName}
                </label>
                <input
                  value={editForm.last_name}
                  onChange={(e) => setEditForm((f) => ({ ...f, last_name: e.target.value }))}
                  className="input"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.users.phone}
              </label>
              <input
                value={editForm.phone}
                onChange={(e) => setEditForm((f) => ({ ...f, phone: e.target.value }))}
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.users.bio}
              </label>
              <textarea
                value={editForm.bio}
                onChange={(e) => setEditForm((f) => ({ ...f, bio: e.target.value }))}
                rows={3}
                className="input resize-none"
              />
            </div>

            <button
              onClick={handleSaveProfile}
              disabled={saving}
              className="btn-primary"
            >
              {saving ? t.users.saving : t.users.saveChanges}
            </button>
          </div>
        )}

        {tab === 'sessions' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <p className="text-sm text-muted-foreground font-body">
                {sessions.length} {t.users.activeSessions}
              </p>
              {sessions.length > 0 && (
                <button
                  onClick={handleRevokeAllSessions}
                  className="btn-danger text-xs"
                >
                  {t.users.revokeAll}
                </button>
              )}
            </div>

            <div className="space-y-3">
              {sessions.length === 0 ? (
                <div className="card p-8 text-center">
                  <div className="text-3xl mb-3">🔒</div>
                  <p className="text-sm text-muted-foreground font-body">
                    {t.users.noActiveSessions}
                  </p>
                </div>
              ) : (
                sessions.map((s) => (
                  <div key={s.id} className="card p-4">
                    <p className="text-sm font-semibold text-foreground font-body">
                      {s.device_name || t.users.unknownDevice}
                    </p>
                    <p className="text-xs text-muted-foreground font-mono mt-1">
                      {s.ip_address} · {formatDateTime(s.created_at)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Block/Unblock modal */}
      {blockModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setBlockModal(false)} />
          <div className="relative bg-card border border-border rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-bold text-foreground mb-4 font-heading">
              {user.is_blocked ? t.users.unblockUser : t.users.blockUser}
            </h3>
            {!user.is_blocked && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                  {t.users.reason} *
                </label>
                <textarea
                  value={blockReason}
                  onChange={(e) => setBlockReason(e.target.value)}
                  rows={3}
                  className="input resize-none"
                  autoFocus
                />
              </div>
            )}
            <div className="flex gap-3">
              <button
                onClick={() => setBlockModal(false)}
                className="btn-ghost flex-1 text-sm"
              >
                {t.users.cancel}
              </button>
              <button
                onClick={handleBlockToggle}
                disabled={actionLoading || (!user.is_blocked && !blockReason.trim())}
                className={user.is_blocked ? 'btn-primary flex-1 text-sm' : 'btn-danger flex-1 text-sm'}
              >
                {actionLoading ? '...' : user.is_blocked ? t.users.unblockUser : t.users.blockUser}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Change role modal */}
      {roleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setRoleModal(false)} />
          <div className="relative bg-card border border-border rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-bold text-foreground mb-4 font-heading">
              {t.users.changeRole}
            </h3>
            <select
              value={newRole}
              onChange={(e) => setNewRole(e.target.value)}
              className="input mb-4"
            >
              {['student', 'mentor', 'staff', 'admin'].map((r) => (
                <option key={r} value={r}>
                  {t.users.roles[r]}
                </option>
              ))}
            </select>
            <div className="flex gap-3">
              <button
                onClick={() => setRoleModal(false)}
                className="btn-ghost flex-1 text-sm"
              >
                {t.users.cancel}
              </button>
              <button
                onClick={handleChangeRole}
                disabled={actionLoading}
                className="btn-primary flex-1 text-sm"
              >
                {actionLoading ? '...' : t.users.changeRole}
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}