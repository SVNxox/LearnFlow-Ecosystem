'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, handleApiError } from '@/lib/api';
import { Assignment, SubmissionDetail } from '@/types/api';
import { Navbar, LoadingSpinner } from '@/components/ui';
import { SubmissionForm, SubmissionFormData } from '@/components/submission';

export default function SubmitRevisionPage() {
  const params = useParams<{ submissionId: string }>();
  const router = useRouter();

  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.submissions.getSubmission(params.submissionId);
        if (!active) return;
        setSubmission(data);
        setAssignment(data.assignment);
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => {
      active = false;
    };
  }, [params.submissionId]);

  const handleSubmit = async (data: SubmissionFormData) => {
    await api.submissions.submitRevision(params.submissionId, data);
    router.push(`/submissions/${params.submissionId}`);
  };

  if (loading) return <LoadingSpinner fullScreen />;

  if (error || !assignment) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 py-16 text-center text-red-600">{error || 'Topilmadi.'}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link href={`/submissions/${params.submissionId}`} className="text-sm text-gray-500 hover:text-gray-700 mb-4 inline-block">
          ← Orqaga
        </Link>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h1 className="text-lg font-semibold text-gray-900 mb-1">{assignment.title}</h1>
          <p className="text-sm text-gray-500 mb-6">{assignment.description}</p>

          {submission?.status === 'changes_requested' && (
            <div className="bg-orange-50 border border-orange-200 text-orange-700 px-4 py-3 rounded-lg text-sm mb-6">
              Mentor o&apos;zgartirish so&apos;ragan. Ishingizni yangilab qayta yuboring.
            </div>
          )}

          <SubmissionForm assignment={assignment} onSubmit={handleSubmit} />
        </div>
      </div>
    </div>
  );
}
