'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, handleApiError } from '@/lib/api';
import { CourseDetail } from '@/types/learning';
import { useTranslation } from '@/lib/i18n/useTranslation';

const PAYMENT_METHODS = [
  { id: 'card', icon: '💳', provider: 'stripe' },
  { id: 'click', icon: '🟦', provider: 'click' },
  { id: 'payme', icon: '🟩', provider: 'payme' },
];

export default function CheckoutPage() {
  const { slug } = useParams<{ slug: string }>();
  const router = useRouter();
  const { t } = useTranslation();

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [selectedMethod, setSelectedMethod] = useState('card');
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCourse();
  }, [slug]);

  const loadCourse = async () => {
    try {
      const data = await api.learning.getCourse(slug);
      setCourse(data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async () => {
    if (!course) return;

    setProcessing(true);
    setError('');

    try {
      const method = PAYMENT_METHODS.find(m => m.id === selectedMethod);

      const payment = await api.payment.create({
        course_id: course.id,
        amount: course.price,
        currency: course.currency || 'UZS',
        provider: method?.provider || 'stripe',
        payment_method: selectedMethod,
      });

      router.push(`/payment/status/${payment.id}`);
    } catch (err) {
      setError(handleApiError(err));
      setProcessing(false);
    }
  };

  const formatAmount = (amount: string, currency: string) => {
    const num = parseFloat(amount);
    if (currency === 'UZS') {
      return `${num.toLocaleString('ru-RU')} UZS`;
    }
    return `$${num.toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (!course) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-5xl mb-4">📚</div>
          <p className="text-muted-foreground mb-4 font-body">
            {error || t.checkout.courseNotFound}
          </p>
          {error && (
            <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4 font-body">
              {error}
            </div>
          )}
          <Link href="/courses" className="text-primary hover:text-primary/80 font-body">
            {t.checkout.backToCourses}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="max-w-2xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/courses/${slug}`}
            className="text-sm text-primary hover:text-primary/80 font-body"
          >
            {t.checkout.backToCourse}
          </Link>
          <h1 className="text-2xl font-bold text-foreground mt-4 font-heading">
            {t.checkout.title}
          </h1>
        </div>

        {/* Course Info */}
        <div className="card p-6 mb-6">
          <div className="flex gap-4">
            {course.thumbnail_url && (
              <img
                src={course.thumbnail_url}
                alt={course.title}
                className="w-32 h-20 object-cover rounded-xl border border-border"
              />
            )}
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-foreground font-heading">
                {course.title}
              </h2>
              <p className="text-2xl font-bold text-primary mt-2 font-heading">
                {formatAmount(course.price, course.currency || 'UZS')}
              </p>
            </div>
          </div>
        </div>

        {/* Payment Methods */}
        <div className="card p-6 mb-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 font-heading">
            {t.checkout.paymentMethod}
          </h3>

          <div className="space-y-3">
            {PAYMENT_METHODS.map((method) => {
              const methodKey = method.id as keyof typeof t.checkout.methods;
              const isSelected = selectedMethod === method.id;

              return (
                <label
                  key={method.id}
                  className={`flex items-center gap-4 p-4 border-2 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50 hover:bg-muted/30'
                  }`}
                >
                  <input
                    type="radio"
                    name="payment_method"
                    value={method.id}
                    checked={isSelected}
                    onChange={(e) => setSelectedMethod(e.target.value)}
                    className="w-4 h-4 text-primary focus:ring-primary/30"
                  />
                  <span className="text-3xl">{method.icon}</span>
                  <div className="flex-1">
                    <p className="font-semibold text-foreground font-body">
                      {t.checkout.methods[methodKey].name}
                    </p>
                    <p className="text-sm text-muted-foreground font-body">
                      {t.checkout.methods[methodKey].description}
                    </p>
                  </div>
                </label>
              );
            })}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl mb-6 font-body">
            {error}
          </div>
        )}

        {/* Pay button */}
        <button
          onClick={handleCheckout}
          disabled={processing}
          className="btn-primary w-full py-3 text-base"
        >
          {processing ? (
            <span className="inline-flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              {t.checkout.processing}
            </span>
          ) : (
            `💳 ${t.checkout.pay} ${formatAmount(course.price, course.currency || 'UZS')}`
          )}
        </button>

        <p className="text-xs text-muted-foreground text-center mt-4 font-body">
          {t.checkout.secure}
        </p>
      </div>
    </div>
  );
}