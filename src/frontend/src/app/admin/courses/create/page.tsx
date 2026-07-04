'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { CreateCourseBody } from '@/types/api';
import CourseCategoryManager from '@/components/admin/CourseCategoryManager';
import { useTranslation } from '@/lib/i18n/useTranslation';
import ThumbnailUploader from '@/components/admin/ThumbnailUploader';

const LANGUAGES = [
  { value: 'ru', labelKey: 'ru' as const },
  { value: 'en', labelKey: 'en' as const },
  { value: 'uz', labelKey: 'uz' as const },
];

const STATUSES = [
  { value: 'draft', labelKey: 'draft' as const },
  { value: 'published', labelKey: 'published' as const },
  { value: 'archived', labelKey: 'archived' as const },
];

// Транслитерация для slug
const translitMap: Record<string, string> = {
  'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
  'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
  'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
  'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
  'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
  'ў': 'u', 'ғ': 'g', 'қ': 'q', 'ҳ': 'h',
};

function generateSlug(name: string): string {
  return name
    .toLowerCase()
    .split('')
    .map((char) => translitMap[char] ?? char)
    .join('')
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

// Минимальная длина названия курса (должна совпадать с бэкендом)
const MIN_TITLE_LENGTH = 3;

export default function CreateCoursePage() {
  const router = useRouter();
  const { t } = useTranslation();

  const [form, setForm] = useState<CreateCourseBody>({
    title: '',
    slug: '',
    description: '',
    short_description: '',
    thumbnail_url: '',
    category_id: null,
    status: 'draft',
    supports_online: true,
    supports_offline: false,
    language: 'uz',
    estimated_weeks: 8,
    is_sequential: true,
    price: '0',
    currency: 'UZS',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [slugManuallyEdited, setSlugManuallyEdited] = useState(false);
  const [imageError, setImageError] = useState('');
  const [imageLoading, setImageLoading] = useState(false);

  const handleTitleChange = (title: string) => {
    setForm((f) => ({ ...f, title }));
    if (!slugManuallyEdited) {
      setForm((f) => ({ ...f, title, slug: generateSlug(title) }));
    }
    // Очищаем ошибку при вводе
    if (error.includes('title_too_short')) {
      setError('');
    }
  };

  const handleSlugChange = (slug: string) => {
    setSlugManuallyEdited(true);
    setForm((f) => ({ ...f, slug }));
  };

  const handleThumbnailChange = (url: string) => {
    setForm((f) => ({ ...f, thumbnail_url: url }));
    setImageError('');
    setImageLoading(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Клиентская валидация
    if (!form.title.trim()) {
      setError(t.courses.titleRequiredError);
      return;
    }
    if (form.title.trim().length < MIN_TITLE_LENGTH) {
      setError(`Kurs nomi kamida ${MIN_TITLE_LENGTH} ta belgidan iborat bo'lishi kerak`);
      return;
    }
    if (!form.supports_online && !form.supports_offline) {
      setError(t.courses.atLeastOneFormat);
      return;
    }

    setSaving(true);

    try {
      const payload = {
        ...form,
        slug: form.slug || generateSlug(form.title),
      };

      const course = await adminApi.createCourse(payload);
      const id = (course as { id?: string }).id;
      router.push(id ? `/admin/courses/${id}?created=1` : '/admin/courses');
    } catch (err: any) {
      // Обработка специфических ошибок бэкенда
      const errorMessage = err?.response?.data?.error || err?.message || '';

      if (errorMessage.includes('title_too_short')) {
        setError(`Kurs nomi kamida ${MIN_TITLE_LENGTH} ta belgidan iborat bo'lishi kerak`);
      } else if (errorMessage.includes('title_too_long')) {
        setError('Kurs nomi juda uzun. Maksimal 200 ta belgi');
      } else if (errorMessage.includes('slug_already_exists')) {
        setError('Bu slug allaqachon mavjud. Iltimos, boshqa nom tanlang');
      } else if (errorMessage.includes('invalid_price')) {
        setError('Noto\'g\'ri narx formati');
      } else {
        // Общая обработка ошибок
        setError(handleApiError(err));
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Breadcrumb */}
      <Link
        href="/admin/courses"
        className="text-sm text-muted-foreground hover:text-foreground mb-4 inline-block font-body"
      >
        ← {t.courses.backToCourses}
      </Link>

      {/* Header */}
      <h1 className="text-xl font-bold text-foreground mb-6 font-heading">
        {t.courses.createCourse}
      </h1>

      <div className="max-w-2xl card p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Title + Slug */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.courses.titleRequired}
              </label>
              <input
                value={form.title}
                onChange={(e) => handleTitleChange(e.target.value)}
                required
                minLength={MIN_TITLE_LENGTH}
                maxLength={200}
                className="input"
                placeholder={t.courses.courseTitle}
              />
              <p className="mt-1 text-xs text-muted-foreground font-body">
                {form.title.length}/200 belgi (min {MIN_TITLE_LENGTH})
              </p>
            </div>
            <div>
              <label className="flex items-center gap-1.5 text-sm font-medium text-foreground mb-1.5 font-body">
                {t.courses.slug}
                {slugManuallyEdited && (
                  <span className="text-xs text-warning font-mono">
                    {t.courses.slugEdited}
                  </span>
                )}
              </label>
              <div className="flex gap-1">
                <input
                  type="text"
                  value={form.slug}
                  onChange={(e) => handleSlugChange(e.target.value)}
                  className="input flex-1 font-mono"
                  placeholder={form.title ? generateSlug(form.title) : t.courses.autoGenerated}
                />
                {slugManuallyEdited && (
                  <button
                    type="button"
                    onClick={() => {
                      setSlugManuallyEdited(false);
                      setForm((f) => ({ ...f, slug: generateSlug(f.title) }));
                    }}
                    className="btn-ghost text-xs px-3"
                    title={t.courses.regenerateSlug}
                  >
                    ↻
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Category */}
          <CourseCategoryManager
            selectedCategoryId={form.category_id}
            onSelectCategory={(categoryId) => setForm((f) => ({ ...f, category_id: categoryId }))}
          />

          {/* Short description */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
              {t.courses.shortDescriptionRequired}
            </label>
            <input
              value={form.short_description}
              onChange={(e) => setForm((f) => ({ ...f, short_description: e.target.value }))}
              maxLength={500}
              className="input"
              placeholder={t.courses.briefDescription}
            />
            <p className="mt-1 text-xs text-muted-foreground font-body">
              {form.short_description.length}/500 belgi
            </p>
          </div>

          {/* Full description */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
              {t.courses.fullDescriptionRequired}
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={5}
              className="input resize-none"
              placeholder={t.courses.detailedDescription}
            />
          </div>

          {/* Thumbnail URL */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
              {t.courses.thumbnailUrl}
            </label>
            <ThumbnailUploader
              value={form.thumbnail_url}
              onChange={(url) => setForm((f) => ({ ...f, thumbnail_url: url }))}
            />
          </div>

          {/* Status + Language */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.courses.status}
              </label>
              <select
                value={form.status}
                onChange={(e) => setForm((f) => ({ ...f, status: e.target.value as 'draft' | 'published' | 'archived' }))}
                className="input"
              >
                {STATUSES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {t.courses.statuses[s.labelKey]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.courses.language}
              </label>
              <select
                value={form.language}
                onChange={(e) => setForm((f) => ({ ...f, language: e.target.value }))}
                className="input"
              >
                {LANGUAGES.map((l) => (
                  <option key={l.value} value={l.value}>
                    {t.courses.languages[l.labelKey]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Estimated weeks */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
              {t.courses.estimatedWeeks}
            </label>
            <input
              type="number"
              min="1"
              value={form.estimated_weeks}
              onChange={(e) => setForm((f) => ({ ...f, estimated_weeks: Number(e.target.value) }))}
              className="input max-w-xs"
            />
          </div>

          {/* Price + Currency */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.courses.priceHint}
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={form.price}
                onChange={(e) => setForm((f) => ({ ...f, price: e.target.value }))}
                className="input"
                placeholder="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.courses.currency}
              </label>
              <select
                value={form.currency}
                onChange={(e) => setForm((f) => ({ ...f, currency: e.target.value }))}
                className="input"
              >
                <option value="UZS">{t.courses.currencies.UZS}</option>
                <option value="USD">{t.courses.currencies.USD}</option>
              </select>
            </div>
          </div>

          {/* Delivery format */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2 font-body">
              {t.courses.deliveryFormat}
            </label>
            <div className="flex gap-6">
              <label className="flex items-center gap-2 text-sm text-foreground font-body cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.supports_online}
                  onChange={(e) => setForm((f) => ({ ...f, supports_online: e.target.checked }))}
                  className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30"
                />
                🌐 {t.courses.online}
              </label>
              <label className="flex items-center gap-2 text-sm text-foreground font-body cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.supports_offline}
                  onChange={(e) => setForm((f) => ({ ...f, supports_offline: e.target.checked }))}
                  className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30"
                />
                🏫 {t.courses.offline}
              </label>
            </div>
          </div>

          {/* Sequential */}
          <label className="flex items-center gap-2 text-sm text-foreground font-body cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_sequential}
              onChange={(e) => setForm((f) => ({ ...f, is_sequential: e.target.checked }))}
              className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30"
            />
            {t.courses.sequentialLessons}
          </label>

          {/* Preview URL */}
          {form.title && (
            <div className="bg-muted border border-border rounded-xl p-3 text-xs">
              <span className="text-muted-foreground font-body">{t.courses.previewUrl}:</span>{' '}
              <span className="font-mono text-primary">
                /courses/{form.slug || generateSlug(form.title)}
              </span>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm font-body">
              ⚠️ {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={saving}
            className="btn-primary w-full"
          >
            {saving ? (
              <span className="inline-flex items-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                {t.courses.creating}
              </span>
            ) : (
              `✨ ${t.courses.createCourse}`
            )}
          </button>
        </form>
      </div>
    </AdminLayout>
  );
}