'use client';

import { useCallback, useState, useRef } from 'react';
import { Upload, Link, X, FileVideo, FileAudio, FileText, Loader2 } from 'lucide-react';
import { adminApi } from '@/lib/admin-api';
import { uploadToS3 } from '@/lib/upload';

export interface ContentUploaderProps {
  lessonId: string;
  value: string;
  onChange: (url: string) => void;
  accept?: string;
  acceptLabel?: string;
}

type UploadMode = 'url' | 'upload';

const ICONS = {
  video: FileVideo,
  audio: FileAudio,
  pdf: FileText,
  slides: FileText,
  default: FileText,
};

export default function ContentUploader({
  lessonId,
  value,
  onChange,
  accept = '*/*',
  acceptLabel = 'Fayl',
}: ContentUploaderProps) {
  const [mode, setMode] = useState<UploadMode>(value ? 'url' : 'upload');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const Icon = ICONS.default;

  const validateFile = (file: File): boolean => {
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (file.size > maxSize) {
      setError('Fayl hajmi 500MB dan oshmasligi kerak');
      return false;
    }
    return true;
  };

  const handleFileUpload = async (file: File) => {
    setError('');
    if (!validateFile(file)) return;

    setUploading(true);
    setProgress(0);

    try {
      const { upload_url, s3_key } = await adminApi.getLessonContentUploadUrl(lessonId, {
        filename: file.name,
        content_type: file.type,
      });

      await uploadToS3(file, upload_url, setProgress);

      const publicUrl = await adminApi.getLessonContentPublicUrl(s3_key);
      onChange(publicUrl);
      setMode('url');
    } catch (err: any) {
      setError(err?.message || 'Faylni yuklashda xatolik');
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleUrlChange = (url: string) => {
    onChange(url);
    setError('');
    setLoading(true);
  };

  const clearValue = () => {
    onChange('');
    setError('');
    setLoading(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-3">
      {/* Mode Switcher */}
      <div className="flex gap-2 p-1 bg-muted rounded-xl">
        <button
          type="button"
          onClick={() => setMode('upload')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            mode === 'upload'
              ? 'bg-card text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Upload size={14} />
          Yuklash
        </button>
        <button
          type="button"
          onClick={() => setMode('url')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            mode === 'url'
              ? 'bg-card text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Link size={14} />
          URL
        </button>
      </div>

      {/* Upload Mode */}
      {mode === 'upload' && (
        <div
          className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all ${
            dragActive
              ? 'border-primary bg-primary/5'
              : 'border-border hover:border-primary/50'
          } ${uploading ? 'opacity-60 pointer-events-none' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={accept}
            onChange={handleFileSelect}
            className="hidden"
            id="content-upload"
          />

          {uploading ? (
            <div className="space-y-3">
              <Loader2 size={32} className="animate-spin mx-auto text-primary" />
              <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                <div
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-muted-foreground font-body">
                Yuklanmoqda... {progress}%
              </p>
            </div>
          ) : (
            <label htmlFor="content-upload" className="cursor-pointer block">
              <div className="space-y-2">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                  <Icon size={24} className="text-primary" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground font-body">
                    {acceptLabel} ni tanlang yoki shu yerga tashlang
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 font-body">
                    Maksimal 500MB
                  </p>
                </div>
              </div>
            </label>
          )}
        </div>
      )}

      {/* URL Mode */}
      {mode === 'url' && (
        <div className="space-y-2">
          <input
            type="url"
            value={value}
            onChange={(e) => handleUrlChange(e.target.value)}
            placeholder="https://..."
            className="input font-mono"
          />
        </div>
      )}

      {/* Preview */}
      {value && (
        <div className="relative inline-block">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-muted rounded-xl">
              <Loader2 size={24} className="animate-spin text-primary" />
            </div>
          )}
          <div className="flex items-center gap-3 bg-muted border border-border rounded-xl p-3">
            <Icon size={20} className="text-primary flex-shrink-0" />
            <span className="text-xs text-foreground font-mono truncate flex-1">
              {value}
            </span>
            <button
              type="button"
              onClick={clearValue}
              className="w-6 h-6 rounded-full bg-destructive/20 text-destructive flex items-center justify-center hover:bg-destructive/30 transition-colors flex-shrink-0"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-3 py-2 rounded-lg text-xs font-body">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}