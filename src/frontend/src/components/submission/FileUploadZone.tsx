'use client';

import { useCallback, useState } from 'react';
import { api, handleApiError } from '@/lib/api';
import { uploadToS3 } from '@/lib/upload';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface UploadedFileInfo {
  s3_key: string;
  file_id: string;
  filename: string;
}

export interface FileUploadZoneProps {
  assignmentId: string;
  accept?: string[];
  maxSizeMB?: number;
  onUploaded: (file: UploadedFileInfo) => void;
}

export default function FileUploadZone({ assignmentId, accept, maxSizeMB = 50, onUploaded }: FileUploadZoneProps) {
  const { t } = useTranslation();
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploaded, setUploaded] = useState<UploadedFileInfo | null>(null);

  const validate = (file: File): boolean => {
    const maxBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
      setError(t.fileUpload.sizeError.replace('{max}', String(maxSizeMB)));
      return false;
    }
    if (accept && accept.length > 0) {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!accept.map((a) => a.toLowerCase()).includes(ext)) {
        setError(t.fileUpload.formatError.replace('{formats}', accept.join(', ')));
        return false;
      }
    }
    return true;
  };

  const handleFile = async (file: File) => {
    setError('');
    if (!validate(file)) return;

    setUploading(true);
    setProgress(0);
    try {
      const { upload_url, s3_key, file_id } = await api.submissions.getPresignedUploadUrl({
        filename: file.name,
        content_type: file.type || 'application/octet-stream',
        assignment_id: assignmentId,
      });

      await uploadToS3(file, upload_url, setProgress);

      const info: UploadedFileInfo = { s3_key, file_id, filename: file.name };
      setUploaded(info);
      onUploaded(info);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="w-full">
      <div
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-200 ${
          dragActive
            ? 'border-primary bg-primary/10 scale-[1.02]'
            : 'border-border hover:border-primary/50 hover:bg-muted/30'
        } ${uploading ? 'opacity-60' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          accept={accept?.join(',')}
          disabled={uploading}
        />

        {uploading ? (
          <div className="space-y-3">
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-muted-foreground font-body">
              {t.fileUpload.uploading} {progress}%
            </p>
          </div>
        ) : uploaded ? (
          <div className="space-y-2">
            <div className="text-4xl mb-2">✅</div>
            <p className="text-sm font-semibold text-success font-body">
              {t.fileUpload.uploaded} {uploaded.filename}
            </p>
            <p className="text-xs text-muted-foreground font-body">
              {t.fileUpload.clickToChange}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-4xl mb-2">📤</div>
            <p className="text-sm text-foreground font-body">
              <span className="font-semibold text-primary">{t.fileUpload.selectFile}</span>{' '}
              {t.fileUpload.orDrop}
            </p>
            <p className="text-xs text-muted-foreground font-mono">
              {accept?.join(', ') || t.fileUpload.anyFile} (max {maxSizeMB}MB)
            </p>
          </div>
        )}
      </div>
      {error && (
        <p className="mt-2 text-sm text-destructive font-body">{error}</p>
      )}
    </div>
  );
}