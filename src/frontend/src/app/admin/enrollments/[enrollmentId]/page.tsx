'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { AdminEnrollment } from '@/types/api';
import { StatusBadge, ConfirmModal } from '@/components/ui';
import { formatDateTime } from '@/utils/helpers';

const ACTIONS: { key: 'activate' | 'suspend' | 'complete' | 'drop'; label: string; needsReason?: boolean; danger?: boolean }[] = [
  { key: 'activate', label: 'Activate' },
  { key: 'suspend', label: 'Suspend', needsReason: true, danger: true },
  { key: 'complete', label: 'Mark Completed' },
  { key: 'drop', label: 'Drop', needsReason: true, danger: true },
];

export default function AdminEnrollmentDetailPage() {
  const { enrollmentId } = useParams<{ enrollmentId: string }>();
  const [enrollment, setEnrollment] = useState<AdminEnrollment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pendingAction, setPendingAction] = useState<typeof ACTIONS[number] | null>(null);
  const [reason, setReason] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setEnrollment(await adminApi.getEnrollment(enrollmentId));
    } catch (err) { setError(handleApiError(err)); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [enrollmentId]);

  const handleAction = async () => {
    if (!pendingAction) return;
    setActionLoading(true);
    try {
      if (pendingAction.key === 'activate') await adminApi.activateEnrollment(enrollmentId);
      else if (pendingAction.key === 'suspend') await adminApi.suspendEnrollment(enrollmentId, reason);
      else if (pendingAction.key === 'complete') await adminApi.completeEnrollment(enrollmentId);
      else if (pendingAction.key === 'drop') await adminApi.dropEnrollment(enrollmentId, reason);
      setPendingAction(null);
      setReason('');
      load();
    } catch (err) { setError(handleApiError(err)); }
    finally { setActionLoading(false); }
  };

  if (loading) return <AdminLayout roles={['admin']}><p className="text-sm text-gray-500">Loading...</p></AdminLayout>;
  if (!enrollment) return <AdminLayout roles={['admin']}><p className="text-sm text-red-600">{error || 'Not found.'}</p></AdminLayout>;

  return (
    <AdminLayout roles={['admin']}>
      <Link href="/dashboard/admin/enrollments" className="text-sm text-gray-500 hover:text-gray-700 mb-4 inline-block">← Enrollments</Link>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{enrollment.user_name || enrollment.user_email}</h1>
          <p className="text-sm text-gray-500 mt-1">{enrollment.course_title}</p>
        </div>
        <StatusBadge status={enrollment.status} />
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4">{error}</div>}

      <div className="max-w-lg bg-white rounded-lg border border-gray-200 p-5 mb-6">
        <dl className="space-y-3 text-sm">
          <div className="flex justify-between"><dt className="text-gray-500">Email</dt><dd className="text-gray-900">{enrollment.user_email}</dd></div>
          <div className="flex justify-between"><dt className="text-gray-500">Format</dt><dd className="text-gray-900 capitalize">{enrollment.delivery_format}</dd></div>
          <div className="flex justify-between"><dt className="text-gray-500">Enrolled at</dt><dd className="text-gray-900">{formatDateTime(enrollment.enrolled_at)}</dd></div>
          {enrollment.completed_at && <div className="flex justify-between"><dt className="text-gray-500">Completed at</dt><dd className="text-gray-900">{formatDateTime(enrollment.completed_at)}</dd></div>}
          {enrollment.dropped_at && <div className="flex justify-between"><dt className="text-gray-500">Dropped at</dt><dd className="text-gray-900">{formatDateTime(enrollment.dropped_at)}</dd></div>}
        </dl>
      </div>

      <div className="flex flex-wrap gap-2">
        {ACTIONS.map((a) => (
          <button key={a.key} onClick={() => setPendingAction(a)}
            className={`px-4 py-2 rounded-lg text-sm font-medium border ${
              a.danger ? 'text-red-600 border-red-200 hover:bg-red-50' : 'text-gray-700 border-gray-200 hover:bg-gray-50'
            }`}>
            {a.label}
          </button>
        ))}
      </div>

      {pendingAction?.needsReason ? (
        <div className={`fixed inset-0 z-50 flex items-center justify-center p-4`}>
          <div className="absolute inset-0 bg-black/40" onClick={() => setPendingAction(null)} />
          <div className="relative bg-white rounded-xl shadow-xl border border-gray-200 max-w-sm w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">{pendingAction.label}</h3>
            <textarea value={reason} onChange={(e) => setReason(e.target.value)} rows={3}
              placeholder="Reason..." className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm mb-4" />
            <div className="flex justify-end gap-2">
              <button onClick={() => setPendingAction(null)} className="px-4 py-2 text-sm border border-gray-200 rounded-lg">Cancel</button>
              <button onClick={handleAction} disabled={actionLoading || !reason.trim()}
                className="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">
                {actionLoading ? '...' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <ConfirmModal
          open={!!pendingAction && !pendingAction.needsReason}
          title={pendingAction?.label || ''}
          description={`Are you sure you want to ${pendingAction?.label.toLowerCase()} this enrollment?`}
          loading={actionLoading}
          onConfirm={handleAction}
          onCancel={() => setPendingAction(null)}
        />
      )}
    </AdminLayout>
  );
}
