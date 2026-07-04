'use client';

import { useCallback, useState, useRef } from 'react';
import { Upload, Link, X, Image as ImageIcon, Loader2 } from 'lucide-react';
import { adminApi } from '@/lib/admin-api';
import { uploadToS3 } from '@/lib/upload';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface ThumbnailUploaderProps {
  value: string;
  onChange: (url: string) => void;
}

type UploadMode = 'url' | 'upload';

export default function ThumbnailUploader({ value, onChange }: ThumbnailUploaderProps) {
  const { t } = useTranslation();
  const [mode, setMode] = useState<UploadMode>(value ? 'url' : 'upload');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [imageLoading, setImageLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateImage = (file: File): boolean => {
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'];

    if (file.size > maxSize) {
      setError('Fayl hajmi 5MB dan oshmasligi kerak');
      return false;
    }
    if (!allowedTypes.includes(file.type)) {
      setError('Faqat JPG, PNG, WebP yoki GIF formatlar qo\'llab-quvvatlanadi');
      return false;
    }
    return true;
  };

  const handleFileUpload = async (file: File) => {
    setError('');
    if (!validateImage(file)) return;

    setUploading(true);
    setProgress(0);

    try {
      // Получаем presigned URL для загрузки
      const { upload_url, s3_key } = await adminApi.getCourseThumbnailUploadUrl({
        filename: file.name,
        content_type: file.type,
      });

      // Загружаем файл в MinIO
      await uploadToS3(file, upload_url, setProgress);

      // Получаем публичный URL для изображения
      const publicUrl = await adminApi.getCourseThumbnailUrl(s3_key);

      onChange(publicUrl);
      setMode('url');
    } catch (err: any) {
      setError(err?.message || 'Rasmni yuklashda xatolik yuz berdi');
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
    setImageLoading(true);
  };

  const clearImage = () => {
    onChange('');
    setError('');
    setImageLoading(false);
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
            accept="image/jpeg,image/jpg,image/png,image/webp,image/gif"
            onChange={handleFileSelect}
            className="hidden"
            id="thumbnail-upload"
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
            <label
              htmlFor="thumbnail-upload"
              className="cursor-pointer block"
            >
              <div className="space-y-2">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                  <ImageIcon size={24} className="text-primary" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground font-body">
                    Rasmni tanlang yoki shu yerga tashlang
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 font-body">
                    JPG, PNG, WebP yoki GIF (max 5MB)
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
            placeholder="https://example.com/image.jpg"
            className="input font-mono"
          />
          <p className="text-xs text-muted-foreground font-body">
            To'g'ridan-to'g'ri rasm URL kiriting (masalan: Unsplash, ImgBB)
          </p>
        </div>
      )}

      {/* Preview */}
      {value && (
        <div className="relative inline-block">
          {imageLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-muted rounded-xl">
              <Loader2 size={24} className="animate-spin text-primary" />
            </div>
          )}
          <img
            src={value}
            alt="Thumbnail preview"
            className={`w-40 h-24 object-cover rounded-xl border border-border transition-opacity ${
              imageLoading ? 'opacity-50' : 'opacity-100'
            }`}
            onLoad={() => {
              setImageLoading(false);
              setError('');
            }}
            onError={() => {
              setImageLoading(false);
              setError('Rasm yuklanmadi. URL noto\'g\'ri bo\'lishi mumkin.');
            }}
          />
          <button
            type="button"
            onClick={clearImage}
            className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-destructive text-destructive-foreground flex items-center justify-center hover:bg-destructive/90 transition-colors"
          >
            <X size={14} />
          </button>
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