'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { api, handleApiError } from '@/lib/api';
import { PendingAssessmentReview } from '@/types/api';
import { LoadingSpinner } from '@/components/ui';
import { AssessmentQueueList } from '@/components/mentor/WorkQueueList';
import { useTranslation } from '@/lib/i18n/useTranslation';

export default function MentorAssessmentQueuePage() {
  const { t } = useTranslation();
  const [items, setItems] = useState<PendingAssessmentReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    api.assessment
      .getPendingReviews()
      .then((res) => active && setItems(res.items))
      .catch((err) => active && setError(handleApiError(err)))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  return (
    <DashboardLayout allowedRoles={['mentor']}>
      {/* Header */}
      <div className="mt-10 mb-6">
        <h1 className="text-2xl font-bold text-foreground font-heading">
          {t.mentor.assessmentQueue.title}
        </h1>
        <p className="text-sm text-muted-foreground mt-1 font-body">
          {t.mentor.assessmentQueue.subtitle}
        </p>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
          {error}
        </div>
      ) : (
        <AssessmentQueueList items={items} />
      )}
    </DashboardLayout>
  );
}