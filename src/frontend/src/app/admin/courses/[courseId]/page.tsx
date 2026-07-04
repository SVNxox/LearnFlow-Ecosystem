'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { CourseDetail, CourseCategory } from '@/types/api';
import EnrollmentsTab from '@/components/admin/CourseEditor/EnrollmentsTab';
import CurriculumTab from '@/components/admin/CourseEditor/CurriculumTab';
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

type Tab = 'settings' | 'curriculum' | 'enrollments' | 'analytics';

export default function CourseEditPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const router = useRouter();
  const { t } = useTranslation();

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [categories, setCategories] = useState<CourseCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [tab, setTab] = useState<Tab>('settings');
  const [slugManuallyEdited, setSlugManuallyEdited] = useState(false);

  const [form, setForm] = useState({
    title: '',
    slug: '',
    description: '',
    short_description: '',
    thumbnail_url: '',
    category_id: null as string | null,
    status: 'draft' as 'draft' | 'published' | 'archived',
    supports_online: true,
    supports_offline: false,
    language: 'uz',
    estimated_weeks: 8,
    is_sequential: true,
    price: '0',
    currency: 'UZS',
  });

  useEffect(() => {
    loadCourse();
    loadCategories();
  }, [courseId]);

  const loadCourse = async () => {
    try {
      const data = await adminApi.getCourse(courseId);
      setCourse(data);
      setForm({
        title: data.title || '',
        slug: data.slug || '',
        description: data.description || '',
        short_description: data.short_description || '',
        thumbnail_url: data.thumbnail_url || '',
        category_id: data.category?.id || null,
        status: data.status || 'draft',
        supports_online: data.supports_online ?? true,
        supports_offline: data.supports_offline ?? false,
        language: data.language || 'uz',
        estimated_weeks: data.estimated_weeks || 8,
        is_sequential: data.is_sequential ?? true,
        price: data.price || '0',
        currency: data.currency || 'UZS',
      });
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await adminApi.getCategories();
      setCategories(data);
    } catch (err) {
      console.error('Error loading categories:', err);
    }
  };

  const handleTitleChange = (title: string) => {
    setForm((f) => ({ ...f, title }));
    if (!slugManuallyEdited) {
      setForm((f) => ({ ...f, title, slug: generateSlug(title) }));
    }
  };

  const handleSlugChange = (slug: string) => {
    setSlugManuallyEdited(true);
    setForm((f) => ({ ...f, slug }));
  };

  const handleSave = async () => {
    if (!form.title.trim()) {
      setError(t.courses.titleRequiredError);
      return;
    }
    if (!form.supports_online && !form.supports_offline) {
      setError(t.courses.atLeastOneFormat);
      return;
    }

    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const payload = {
        title: form.title.trim(),
        slug: form.slug || generateSlug(form.title),
        description: form.description,
        short_description: form.short_description,
        thumbnail_url: form.thumbnail_url,
        category_id: form.category_id,
        status: form.status,
        supports_online: form.supports_online,
        supports_offline: form.supports_offline,
        language: form.language,
        estimated_weeks: form.estimated_weeks,
        is_sequential: form.is_sequential,
        price: form.price,
        currency: form.currency,
      };

      await adminApi.updateCourse(courseId, payload);
      setSuccess(t.courses.courseUpdated);
      setSlugManuallyEdited(false);

      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <AdminLayout roles={['admin', 'staff']}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
        </div>
      </AdminLayout>
    );
  }

  if (!course) {
    return (
      <AdminLayout roles={['admin', 'staff']}>
        <div className="text-center py-12">
          <div className="text-5xl mb-4">📚</div>
          <p className="text-destructive mb-4 font-body">{t.courses.courseNotFound}</p>
          <Link href="/admin/courses" className="text-primary hover:underline font-body">
            ← {t.courses.backToCourses}
          </Link>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Breadcrumbs */}
      <nav className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground font-body">
          <li>
            <Link href="/admin/courses" className="hover:text-foreground transition-colors">
              {t.courses.title}
            </Link>
          </li>
          <li>/</li>
          <li className="text-foreground font-medium truncate max-w-md">{course.title}</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-foreground font-heading">
          {t.courses.editCourse}
        </h1>
        <Link
          href={`/courses/${course.slug}`}
          target="_blank"
          className="text-sm text-primary hover:text-primary/80 font-semibold font-body"
        >
          {t.courses.viewCourse}
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border mb-6">
        {([
          ['settings', t.courses.settings],
          ['curriculum', `${t.courses.curriculum} (${course.modules?.length || 0} ${t.courses.modules})`],
          ['enrollments', t.courses.enrollmentsTab],
          ['analytics', t.courses.analytics],
        ] as [Tab, string][]).map(([tTab, label]) => (
          <button
            key={tTab}
            onClick={() => setTab(tTab)}
            className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-colors font-body ${
              tab === tTab
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Settings Tab */}
      {tab === 'settings' && (
        <div className="max-w-2xl card p-6">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSave();
            }}
            className="space-y-5"
          >
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
                  className="input"
                  placeholder={t.courses.courseTitle}
                />
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
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.courses.category}
              </label>
              <select
                value={form.category_id || ''}
                onChange={(e) => setForm({ ...form, category_id: e.target.value || null })}
                className="input"
              >
                <option value="">{t.courses.noCategory}</option>
                {categories.filter((c) => c.is_active).map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.icon && `${cat.icon} `}{cat.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Short description */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.courses.shortDescriptionRequired}
              </label>
              <input
                value={form.short_description}
                onChange={(e) => setForm({ ...form, short_description: e.target.value })}
                maxLength={500}
                className="input"
                placeholder={t.courses.briefDescription}
              />
            </div>

            {/* Full description */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
                {t.courses.fullDescriptionRequired}
              </label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={5}
                className="input resize-none"
                placeholder={t.courses.detailedDescription}
              />
            </div>

            {/* Thumbnail */}
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
                  onChange={(e) => setForm({ ...form, status: e.target.value as 'draft' | 'published' | 'archived' })}
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
                  onChange={(e) => setForm({ ...form, language: e.target.value })}
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
                onChange={(e) => setForm({ ...form, estimated_weeks: Number(e.target.value) })}
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
                  onChange={(e) => setForm({ ...form, price: e.target.value })}
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
                  onChange={(e) => setForm({ ...form, currency: e.target.value })}
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
                    onChange={(e) => setForm({ ...form, supports_online: e.target.checked })}
                    className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30"
                  />
                  🌐 {t.courses.online}
                </label>
                <label className="flex items-center gap-2 text-sm text-foreground font-body cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.supports_offline}
                    onChange={(e) => setForm({ ...form, supports_offline: e.target.checked })}
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
                onChange={(e) => setForm({ ...form, is_sequential: e.target.checked })}
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

            {/* Messages */}
            {error && (
              <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm">
                {error}
              </div>
            )}
            {success && (
              <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm">
                {success}
              </div>
            )}

            {/* Save button */}
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
                  {t.courses.saving}
                </span>
              ) : (
                `💾 ${t.courses.saveChanges}`
              )}
            </button>
          </form>
        </div>
      )}

      {/* Curriculum Tab */}
      {tab === 'curriculum' && (
        <CurriculumTab
          courseId={courseId}
          courseSlug={course.slug}
          modules={course.modules || []}
          onRefresh={loadCourse}
        />
      )}

      {/* Enrollments Tab */}
      {tab === 'enrollments' && (
        <EnrollmentsTab courseId={courseId} courseTitle={course.title} />
      )}

      {/* Analytics Tab */}
      {tab === 'analytics' && (
        <div className="card p-8 text-center">
          <div className="text-5xl mb-4">📊</div>
          <p className="text-sm text-muted-foreground font-body">
            {t.courses.analyticsComingSoon}
          </p>
        </div>
      )}
    </AdminLayout>
  );
}