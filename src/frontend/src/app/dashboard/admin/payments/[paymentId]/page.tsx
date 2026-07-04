'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { StatusBadge } from '@/components/ui';
import { formatDateTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

interface PaymentDetail {
  id: string;
  user_id: string;
  user_email: string;
  user_name: string;
  enrollment_id: string;
  course_title: string;
  amount: string;
  currency: string;
  status: string;
  payment_method: string;
  provider: string;
  provider_payment_id: string;
  idempotency_key: string;
  created_at: string;
  succeeded_at: string | null;
  failed_at: string | null;
  refunded_at: string | null;
  metadata: Record<string, unknown>;
}

export default function PaymentDetailPage() {
  const { paymentId } = useParams<{ paymentId: string }>();
  const { t } = useTranslation();
  const [payment, setPayment] = useState<PaymentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPayment();
  }, [paymentId]);

  const loadPayment = async () => {
    try {
      const data = await adminApi.getPaymentDetail(paymentId);
      setPayment(data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AdminLayout roles={['admin', 'staff']}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
        </div>
      </AdminLayout>
    );
  }

  if (error || !payment) {
    return (
      <AdminLayout roles={['admin', 'staff']}>
        <div className="text-center py-12">
          <div className="text-5xl mb-4">💳</div>
          <p className="text-destructive mb-4 font-body">{error || t.payments.paymentNotFound}</p>
          <Link href="/dashboard/admin/payments" className="text-primary hover:underline font-body">
            ← {t.payments.backToPayments}
          </Link>
        </div>
      </AdminLayout>
    );
  }

  const formatAmount = (amount: string, currency: string) => {
    const num = parseFloat(amount);
    if (currency === 'UZS') {
      return `${num.toLocaleString('ru-RU')} UZS`;
    }
    return `$${num.toFixed(2)}`;
  };

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Breadcrumbs */}
      <nav className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground font-body">
          <li>
            <Link href="/dashboard/admin/payments" className="hover:text-foreground transition-colors">
              {t.payments.title}
            </Link>
          </li>
          <li>/</li>
          <li className="text-foreground font-medium font-mono">{payment.id.slice(0, 8)}...</li>
        </ol>
      </nav>

      <h1 className="text-xl font-bold text-foreground mb-6 font-heading">
        {t.payments.details}
      </h1>

      <div className="max-w-4xl space-y-6">
        {/* Status + Amount */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <StatusBadge status={payment.status} />
            <div className="text-right">
              <p className="text-xs text-muted-foreground uppercase font-mono">{t.payments.amount}</p>
              <p className="text-3xl font-bold text-foreground font-heading">
                {formatAmount(payment.amount, payment.currency)}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs text-muted-foreground uppercase font-mono">{t.payments.paymentMethod}</p>
              <p className="text-lg font-medium text-foreground mt-1 font-body">
                {t.payments.methods[payment.payment_method as keyof typeof t.payments.methods] || payment.payment_method}
              </p>
            </div>
          </div>
        </div>

        {/* User Info */}
        <div className="card p-6">
          <h3 className="text-sm font-semibold text-foreground mb-4 font-heading">
            {t.payments.userInfo}
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground font-mono">{t.payments.name}</p>
              <p className="text-sm text-foreground mt-1 font-body">{payment.user_name || '—'}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-mono">{t.payments.email}</p>
              <p className="text-sm text-foreground mt-1 font-body">{payment.user_email || '—'}</p>
            </div>
          </div>
        </div>

        {/* Course Info */}
        {payment.course_title && (
          <div className="card p-6">
            <h3 className="text-sm font-semibold text-foreground mb-4 font-heading">
              {t.payments.courseInfo}
            </h3>
            <div>
              <p className="text-xs text-muted-foreground font-mono">{t.payments.course}</p>
              <p className="text-sm text-foreground mt-1 font-body">{payment.course_title}</p>
            </div>
          </div>
        )}

        {/* Payment Details */}
        <div className="card p-6">
          <h3 className="text-sm font-semibold text-foreground mb-4 font-heading">
            {t.payments.paymentDetails}
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground font-mono">{t.payments.paymentId}</p>
              <p className="text-sm text-foreground mt-1 font-mono break-all">{payment.id}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-mono">{t.payments.provider}</p>
              <p className="text-sm text-foreground mt-1 font-body capitalize">{payment.provider || '—'}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-mono">{t.payments.providerPaymentId}</p>
              <p className="text-sm text-foreground mt-1 font-mono break-all">{payment.provider_payment_id || '—'}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-mono">{t.payments.idempotencyKey}</p>
              <p className="text-sm text-foreground mt-1 font-mono break-all">{payment.idempotency_key || '—'}</p>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="card p-6">
          <h3 className="text-sm font-semibold text-foreground mb-4 font-heading">
            {t.payments.timeline}
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground font-mono">{t.payments.created}</p>
              <p className="text-sm text-foreground mt-1 font-body">{formatDateTime(payment.created_at)}</p>
            </div>
            {payment.succeeded_at && (
              <div>
                <p className="text-xs text-muted-foreground font-mono">{t.payments.succeeded}</p>
                <p className="text-sm text-success mt-1 font-body">{formatDateTime(payment.succeeded_at)}</p>
              </div>
            )}
            {payment.failed_at && (
              <div>
                <p className="text-xs text-muted-foreground font-mono">{t.payments.failed}</p>
                <p className="text-sm text-destructive mt-1 font-body">{formatDateTime(payment.failed_at)}</p>
              </div>
            )}
            {payment.refunded_at && (
              <div>
                <p className="text-xs text-muted-foreground font-mono">{t.payments.refunded}</p>
                <p className="text-sm text-purple mt-1 font-body">{formatDateTime(payment.refunded_at)}</p>
              </div>
            )}
          </div>
        </div>

        {/* Metadata */}
        {payment.metadata && Object.keys(payment.metadata).length > 0 && (
          <div className="card p-6">
            <h3 className="text-sm font-semibold text-foreground mb-4 font-heading">
              {t.payments.metadata}
            </h3>
            <pre className="bg-muted p-3 rounded-xl text-xs overflow-auto font-mono text-foreground">
              {JSON.stringify(payment.metadata, null, 2)}
            </pre>
          </div>
        )}

        {/* Back button */}
        <div>
          <Link
            href="/dashboard/admin/payments"
            className="text-sm text-primary hover:text-primary/80 font-semibold font-body"
          >
            ← {t.payments.backToPayments}
          </Link>
        </div>
      </div>
    </AdminLayout>
  );
}