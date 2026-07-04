'use client';

import { useState } from 'react';
import { Assignment } from '@/types/api';
import { handleApiError } from '@/lib/api';
import FileUploadZone, { UploadedFileInfo } from './FileUploadZone';
import { Button } from '@/components/ui';
import { useTranslation } from '@/lib/i18n/useTranslation';

export type SubmissionType = 'github_repository' | 'file_upload' | 'text_answer' | 'external_link';

export interface SubmissionFormData {
  submission_type: SubmissionType;
  payload: Record<string, unknown>;
  notes?: string;
}

export interface SubmissionFormProps {
  assignment: Assignment;
  onSubmit: (data: SubmissionFormData) => Promise<void>;
}

const TABS: { type: SubmissionType; labelKey: keyof typeof import('@/lib/i18n/uz').uz.submissionForm.tabs; icon: string }[] = [
  { type: 'github_repository', labelKey: 'github_repository', icon: '🐙' },
  { type: 'file_upload', labelKey: 'file_upload', icon: '📁' },
  { type: 'text_answer', labelKey: 'text_answer', icon: '📝' },
  { type: 'external_link', labelKey: 'external_link', icon: '🔗' },
];

export default function SubmissionForm({ assignment, onSubmit }: SubmissionFormProps) {
  const { t } = useTranslation();
  const allowedTypes = assignment.submission_types_allowed?.length
    ? assignment.submission_types_allowed
    : TABS.map((tab) => tab.type);

  const [type, setType] = useState<SubmissionType>(allowedTypes[0] as SubmissionType);
  const [githubUrl, setGithubUrl] = useState('');
  const [liveUrl, setLiveUrl] = useState('');
  const [textAnswer, setTextAnswer] = useState('');
  const [externalUrl, setExternalUrl] = useState('');
  const [uploadedFile, setUploadedFile] = useState<UploadedFileInfo | null>(null);
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const wordCount = textAnswer.trim() ? textAnswer.trim().split(/\s+/).length : 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    let payload: Record<string, unknown>;
    switch (type) {
      case 'github_repository':
        if (!githubUrl) return setError(t.submissionForm.errors.githubRequired);
        payload = { github_url: githubUrl, live_url: liveUrl || undefined };
        break;
      case 'file_upload':
        if (!uploadedFile) return setError(t.submissionForm.errors.fileRequired);
        payload = uploadedFile;
        break;
      case 'text_answer':
        if (!textAnswer.trim()) return setError(t.submissionForm.errors.answerRequired);
        payload = { text: textAnswer };
        break;
      case 'external_link':
        if (!externalUrl) return setError(t.submissionForm.errors.urlRequired);
        payload = { url: externalUrl };
        break;
    }

    setLoading(true);
    try {
      await onSubmit({ submission_type: type, payload, notes: notes || undefined });
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const visibleTabs = TABS.filter((tab) => allowedTypes.includes(tab.type));

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Tabs */}
      {visibleTabs.length > 1 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {visibleTabs.map((tab) => (
            <button
              key={tab.type}
              type="button"
              onClick={() => setType(tab.type)}
              className={`p-4 border-2 rounded-xl text-center transition-all duration-200 ${
                type === tab.type
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50 hover:bg-muted/30'
              }`}
            >
              <div className="text-2xl mb-1">{tab.icon}</div>
              <div className="text-xs font-semibold text-foreground font-body">
                {t.submissionForm.tabs[tab.labelKey]}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* GitHub Repository */}
      {type === 'github_repository' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
              {t.submissionForm.githubUrl}
            </label>
            <input
              type="url"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder={t.submissionForm.githubUrlPlaceholder}
              className="input font-mono"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
              {t.submissionForm.liveUrl}
            </label>
            <input
              type="url"
              value={liveUrl}
              onChange={(e) => setLiveUrl(e.target.value)}
              placeholder={t.submissionForm.liveUrlPlaceholder}
              className="input font-mono"
            />
          </div>
        </div>
      )}

      {/* File Upload */}
      {type === 'file_upload' && (
        <FileUploadZone
          assignmentId={assignment.id}
          accept={assignment.allowed_file_extensions?.split(',').map((s) => s.trim()).filter(Boolean)}
          maxSizeMB={assignment.max_file_size_mb || 50}
          onUploaded={setUploadedFile}
        />
      )}

      {/* Text Answer */}
      {type === 'text_answer' && (
        <div>
          <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
            {t.submissionForm.answer}
          </label>
          <textarea
            value={textAnswer}
            onChange={(e) => setTextAnswer(e.target.value)}
            rows={10}
            placeholder={t.submissionForm.answerPlaceholder}
            className="input resize-none"
          />
          <p className="mt-1 text-xs text-muted-foreground font-mono">
            {wordCount} {t.submissionForm.words}
          </p>
        </div>
      )}

      {/* External Link */}
      {type === 'external_link' && (
        <div>
          <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
            {t.submissionForm.url}
          </label>
          <input
            type="url"
            value={externalUrl}
            onChange={(e) => setExternalUrl(e.target.value)}
            placeholder={t.submissionForm.urlPlaceholder}
            className="input font-mono"
          />
        </div>
      )}

      {/* Notes (for non-text types) */}
      {type !== 'text_answer' && (
        <div>
          <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
            {t.submissionForm.notes}
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder={t.submissionForm.notesPlaceholder}
            className="input resize-none"
          />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
          {error}
        </div>
      )}

      {/* Submit */}
      <div className="flex justify-end">
        <Button type="submit" loading={loading} size="lg">
          🚀 {t.submissionForm.submit}
        </Button>
      </div>
    </form>
  );
}