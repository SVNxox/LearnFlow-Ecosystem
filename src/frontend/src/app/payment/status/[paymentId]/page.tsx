'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api, handleApiError } from '@/lib/api';
import { useTranslation } from '@/lib/i18n/useTranslation';

interface PaymentStatus {
  id: string;
  status: 'pending' | 'processing' | 'succeeded' | 'failed' | 'cancelled' | 'refunded';
  amount: string;
  currency: string;
  payment_method?: string;
}

export default function PaymentStatusPage() {
  const { paymentId } = useParams<{ paymentId: string }>();
  const { t } = useTranslation();
  const [payment, setPayment] = useState<PaymentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const [telegramUrl, setTelegramUrl] = useState<string | null>(null);
  const [loadingTelegram, setLoadingTelegram] = useState(false);

  useEffect(() => {
    loadPaymentStatus();
    intervalRef.current = setInterval(loadPaymentStatus, 3000);
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [paymentId]);

  const loadPaymentStatus = async () => {
    try {
      const data = await api.payment.getDetail(paymentId);
      setPayment(data);

      if (['succeeded', 'failed', 'cancelled', 'refunded'].includes(data.status)) {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const simulateSuccess = async () => {
    try {
      await api.payment.simulateSuccess(paymentId);
      await loadPaymentStatus();
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const getTelegramPaymentUrl = async () => {
    if (!payment) return;
    setLoadingTelegram(true);
    try {
      const data = await api.payment.getTelegramInvoice(payment.id);
      setTelegramUrl(data.invoice_url);
      window.open(data.invoice_url, '_blank');
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoadingTelegram(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
          <p className="text-sm text-muted-foreground mt-4 font-body">
            {t.paymentStatus.loading}
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="card p-8 text-center max-w-md">
          <div className="text-5xl mb-4">⚠️</div>
          <p className="text-destructive mb-4 font-body">{error}</p>
          <Link href="/" className="text-primary hover:text-primary/80 font-body">
            {t.paymentStatus.backToHome}
          </Link>
        </div>
      </div>
    );
  }

  if (!payment) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="card p-8 text-center">
          <div className="text-5xl mb-4">🔍</div>
          <p className="text-muted-foreground font-body">{t.paymentStatus.notFound}</p>
        </div>
      </div>
    );
  }

  const formatAmount = (amount: string | number | undefined, currency: string) => {
    if (!amount) return '0';
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    if (isNaN(num)) return '0';
    return num.toLocaleString();
  };

  const getStatusConfig = () => {
    const statusKey = payment.status as keyof typeof t.paymentStatus.statuses;
    const statusText = t.paymentStatus.statuses[statusKey] || t.paymentStatus.statuses.pending;

    switch (payment.status) {
      case 'succeeded':
        return {
          icon: '✅',
          ...statusText,
          color: 'var(--color-success)',
          bgColor: 'var(--color-success-bg)',
          borderColor: 'var(--color-success)',
        };
      case 'pending':
      case 'processing':
        return {
          icon: '⏳',
          ...statusText,
          color: 'var(--color-warning)',
          bgColor: 'var(--color-warning-bg)',
          borderColor: 'var(--color-warning)',
        };
      case 'failed':
        return {
          icon: '❌',
          ...statusText,
          color: 'var(--color-error)',
          bgColor: 'var(--color-error-bg)',
          borderColor: 'var(--color-error)',
        };
      case 'refunded':
        return {
          icon: '💰',
          ...statusText,
          color: 'var(--color-purple)',
          bgColor: 'rgba(167,139,250,0.1)',
          borderColor: 'var(--color-purple)',
        };
      case 'cancelled':
        return {
          icon: '🚫',
          ...statusText,
          color: 'var(--color-muted-foreground)',
          bgColor: 'var(--color-muted)',
          borderColor: 'var(--color-muted-foreground)',
        };
      default:
        return {
          icon: 'ℹ️',
          title: t.paymentStatus.title,
          description: `${t.paymentStatus.title}: ${payment.status}`,
          color: 'var(--color-info)',
          bgColor: 'var(--color-info-bg)',
          borderColor: 'var(--color-info)',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="max-w-md mx-auto px-4">
        {/* Status Card */}
        <div
          className="card p-8 text-center mb-6"
          style={{
            backgroundColor: config.bgColor,
            borderColor: config.borderColor + '40',
          }}
        >
          {/* Icon */}
          <div
            className="inline-flex w-24 h-24 rounded-full items-center justify-center text-6xl mb-5"
            style={{ backgroundColor: config.bgColor }}
          >
            {config.icon}
          </div>

          {/* Title */}
          <h1
            className="text-2xl font-bold mb-2 font-heading"
            style={{ color: config.color }}
          >
            {config.title}
          </h1>
          <p className="text-muted-foreground mb-6 font-body">
            {config.description}
          </p>

          {/* Amount */}
          <div className="bg-card border border-border rounded-xl p-4 mb-6">
            <p className="text-xs text-muted-foreground font-mono uppercase mb-1">
              {t.paymentStatus.amount}
            </p>
            <p className="text-3xl font-bold text-foreground font-heading">
              {formatAmount(payment.amount, payment.currency)}{' '}
              <span className="text-lg text-muted-foreground">{payment.currency || 'UZS'}</span>
            </p>
            {payment.payment_method && (
              <p className="text-xs text-muted-foreground mt-2 font-mono capitalize">
                💳 {payment.payment_method}
              </p>
            )}
          </div>

          {/* Pending actions */}
          {payment.status === 'pending' && (
            <div className="space-y-3">
              <button
                onClick={getTelegramPaymentUrl}
                disabled={loadingTelegram}
                className="btn-primary w-full"
              >
                {loadingTelegram ? t.paymentStatus.loadingTelegram : t.paymentStatus.telegramPay}
              </button>

              {process.env.NODE_ENV === 'development' && (
                <div className="bg-info/10 border border-info/30 rounded-xl p-3">
                  <p className="text-xs text-info mb-2 font-mono">
                    {t.paymentStatus.testMode}
                  </p>
                  <button
                    onClick={simulateSuccess}
                    className="btn-ghost w-full text-sm"
                  >
                    {t.paymentStatus.simulateSuccess}
                  </button>
                </div>
              )}

              <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground font-body">
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary" />
                {t.paymentStatus.autoRefresh}
              </div>
            </div>
          )}

          {/* Succeeded actions */}
          {payment.status === 'succeeded' && (
            <div className="space-y-3">
              <Link href="/my-courses" className="btn-primary w-full block text-center">
                {t.paymentStatus.actions.myCourses}
              </Link>
              <Link href="/" className="btn-ghost w-full block text-center">
                {t.paymentStatus.actions.backToHome}
              </Link>
            </div>
          )}

          {/* Failed actions */}
          {payment.status === 'failed' && (
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="btn-primary w-full"
              >
                {t.paymentStatus.actions.retry}
              </button>
              <Link href="/" className="btn-ghost w-full block text-center">
                {t.paymentStatus.actions.backToHome}
              </Link>
            </div>
          )}

          {/* Cancelled/Refunded actions */}
          {(payment.status === 'cancelled' || payment.status === 'refunded') && (
            <Link href="/" className="btn-ghost w-full block text-center">
              {t.paymentStatus.actions.backToHome}
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}