'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { Payment } from '@/types/api';
import { StatusBadge } from '@/components/ui';
import { formatDateTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

const STATUS_TABS = [
  { value: '', labelKey: 'all' as const },
  { value: 'pending', labelKey: 'pending' as const },
  { value: 'processing', labelKey: 'processing' as const },
  { value: 'succeeded', labelKey: 'succeeded' as const },
  { value: 'failed', labelKey: 'failed' as const },
  { value: 'cancelled', labelKey: 'cancelled' as const },
  { value: 'refunded', labelKey: 'refunded' as const },
];

const METHOD_LABELS: Record<string, string> = {
  click: '💳 Click',
  payme: '💰 Payme',
  card: '💳 Karta',
  cash: '💵 Naqd pul',
  bank_transfer: '🏦 Bank o\'tkazmasi',
};

interface PaymentWithDetails extends Payment {
  user_email?: string;
  user_name?: string;
  course_title?: string;
}

function PaymentsContent() {
  const { t } = useTranslation();
  const router = useRouter();
  const sp = useSearchParams();
  const status = sp.get('status') || '';
  const page = parseInt(sp.get('page') || '1', 10);
  const searchFromUrl = sp.get('search') || '';

  const [payments, setPayments] = useState<PaymentWithDetails[]>([]);
  const [count, setCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchInput, setSearchInput] = useState(searchFromUrl);

  const updateParam = useCallback((key: string, value: string | null) => {
    const params = new URLSearchParams(sp.toString());
    if (value) params.set(key, value); else params.delete(key);
    if (key !== 'page') params.delete('page');
    router.push(`/dashboard/admin/payments?${params.toString()}`);
  }, [router, sp]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== searchFromUrl) {
        updateParam('search', searchInput || null);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchInput, searchFromUrl, updateParam]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    adminApi.getAllPayments({
      status: status || undefined,
      search: searchFromUrl || undefined,
      page
    })
      .then((data) => {
        if (!active) return;
        setPayments(data.results);
        setCount(data.count);
        setTotalPages(data.total_pages || 1);
      })
      .catch((err) => {
        if (!active) return;
        setError(handleApiError(err));
      })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [status, page, searchFromUrl]);

  // Статистика
  const succeededCount = payments.filter(p => p.status === 'succeeded').length;
  const pendingCount = payments.filter(p => p.status === 'pending').length;
  const totalAmount = payments
    .filter(p => p.status === 'succeeded')
    .reduce((sum, p) => sum + parseFloat(p.amount), 0);

  const formatAmount = (amount: string, currency: string) => {
    const num = parseFloat(amount);
    if (currency === 'UZS') {
      return `${num.toLocaleString('ru-RU')} UZS`;
    }
    return `$${num.toFixed(2)}`;
  };

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-foreground font-heading">
          {t.payments.title} ({count})
        </h1>
        <p className="text-sm text-muted-foreground mt-1 font-body">
          {t.payments.subtitle}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.payments.totalPayments}</p>
          <p className="stat-value mt-2">{count}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.payments.succeeded}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-success)' }}>{succeededCount}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.payments.pending}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-warning)' }}>{pendingCount}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.payments.totalRevenue}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-info)' }}>
            {formatAmount(totalAmount.toString(), 'UZS')}
          </p>
        </div>
      </div>

      {/* Status tabs */}
      <div className="filter-pills mb-4 flex-wrap">
        {STATUS_TABS.map(({ value, labelKey }) => (
          <button
            key={value}
            onClick={() => updateParam('status', value || null)}
            className={`filter-pill ${status === value ? 'filter-pill-active' : 'filter-pill-inactive'}`}
          >
            {t.payments.filters[labelKey]}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder={t.payments.search}
            className="input pl-10"
          />
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            🔍
          </span>
          {searchInput && (
            <button
              type="button"
              onClick={() => setSearchInput('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-card border border-border rounded-2xl overflow-hidden">
        <table className="min-w-full divide-y divide-border">
          <thead>
            <tr className="bg-muted/50">
              {[
                t.payments.user,
                t.payments.course,
                t.payments.amount,
                t.payments.method,
                t.payments.status,
                t.payments.date,
                t.payments.actions,
              ].map((h) => (
                <th
                  key={h}
                  className="px-5 py-3 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider font-mono"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <tr key={i}>
                  <td colSpan={7} className="px-5 py-4">
                    <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                  </td>
                </tr>
              ))
            ) : payments.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-5 py-12 text-center">
                  <div className="text-3xl mb-3">💳</div>
                  <p className="text-sm text-muted-foreground font-body">
                    {searchFromUrl ? t.payments.noPaymentsFound : t.payments.noPayments}
                  </p>
                </td>
              </tr>
            ) : (
              payments.map((p) => (
                <tr key={p.id} className="hover:bg-muted/30 transition-colors">
                  {/* User */}
                  <td className="px-5 py-3.5">
                    <div>
                      <p className="text-sm font-medium text-foreground font-body">
                        {p.user_name || p.user_email || '—'}
                      </p>
                      {p.user_name && p.user_email && (
                        <p className="text-xs text-muted-foreground font-mono mt-0.5">
                          {p.user_email}
                        </p>
                      )}
                    </div>
                  </td>

                  {/* Course */}
                  <td className="px-5 py-3.5 text-sm text-foreground font-body">
                    {p.course_title || '—'}
                  </td>

                  {/* Amount */}
                  <td className="px-5 py-3.5 text-sm font-semibold text-foreground font-mono">
                    {formatAmount(p.amount, p.currency)}
                  </td>

                  {/* Method */}
                  <td className="px-5 py-3.5 text-sm text-foreground font-body">
                    {METHOD_LABELS[p.payment_method] || p.payment_method}
                  </td>

                  {/* Status */}
                  <td className="px-5 py-3.5">
                    <StatusBadge status={p.status} />
                  </td>

                  {/* Date */}
                  <td className="px-5 py-3.5 text-xs text-muted-foreground font-mono">
                    {formatDateTime(p.created_at)}
                  </td>

                  {/* Actions */}
                  <td className="px-5 py-3.5">
                    <Link
                      href={`/dashboard/admin/payments/${p.id}`}
                      className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                    >
                      {t.payments.view}
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-6">
          {page > 1 && (
            <button
              onClick={() => updateParam('page', String(page - 1))}
              className="btn-ghost text-sm"
            >
              {t.payments.pagination.previous}
            </button>
          )}
          <span className="text-sm text-muted-foreground font-mono px-4">
            {t.payments.pagination.page} {page} {t.payments.pagination.of} {totalPages}
          </span>
          {page < totalPages && (
            <button
              onClick={() => updateParam('page', String(page + 1))}
              className="btn-ghost text-sm"
            >
              {t.payments.pagination.next}
            </button>
          )}
        </div>
      )}
    </AdminLayout>
  );
}

export default function AdminPaymentsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <PaymentsContent />
    </Suspense>
  );
}