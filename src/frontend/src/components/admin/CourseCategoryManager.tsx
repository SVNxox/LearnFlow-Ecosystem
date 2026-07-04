'use client';

import { useState, useEffect } from 'react';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { useTranslation } from '@/lib/i18n/useTranslation';

interface CourseCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string;
  order: number;
  is_active: boolean;
  parent_id: string | null;
}

interface CourseCategoryManagerProps {
  selectedCategoryId?: string | null;
  onSelectCategory?: (categoryId: string | null) => void;
  showManagement?: boolean;
}

interface CategoryForm {
  name: string;
  slug: string;
  description: string;
  icon: string;
  order: number;
  is_active: boolean;
  parent_id: string | null;
}

const emptyForm: CategoryForm = {
  name: '',
  slug: '',
  description: '',
  icon: '',
  order: 0,
  is_active: true,
  parent_id: null,
};

// Функция для проверки, является ли строка URL
function isUrl(value: string): boolean {
  return value.startsWith('http://') || value.startsWith('https://');
}

// Компонент для отображения иконки
function CategoryIcon({ icon, size = 'md' }: { icon: string; size?: 'sm' | 'md' | 'lg' }) {
  if (!icon) return null;

  const sizeClasses = {
    sm: 'w-4 h-4 text-sm',
    md: 'w-6 h-6 text-xl',
    lg: 'w-8 h-8 text-2xl',
  };

  if (isUrl(icon)) {
    return (
      <img
        src={icon}
        alt="Category icon"
        className={`${sizeClasses[size]} rounded object-cover flex-shrink-0`}
        onError={(e) => {
          e.currentTarget.style.display = 'none';
        }}
      />
    );
  }

  return (
    <span className={`${sizeClasses[size]} flex items-center justify-center flex-shrink-0`}>
      {icon}
    </span>
  );
}

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

export default function CourseCategoryManager({
  selectedCategoryId,
  onSelectCategory,
  showManagement = false,
}: CourseCategoryManagerProps) {
  const { t } = useTranslation();
  const [categories, setCategories] = useState<CourseCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<CourseCategory | null>(null);
  const [form, setForm] = useState<CategoryForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [slugManuallyEdited, setSlugManuallyEdited] = useState(false);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const data = await adminApi.getCategories();
      setCategories(data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleNameChange = (name: string) => {
    setForm({ ...form, name });
    if (!slugManuallyEdited) {
      setForm((f) => ({ ...f, name, slug: generateSlug(name) }));
    }
  };

  const handleSlugChange = (slug: string) => {
    setSlugManuallyEdited(true);
    setForm({ ...form, slug });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError(t.categories.nameRequired);
      return;
    }

    setSaving(true);
    setError('');

    try {
      const payload = {
        ...form,
        slug: form.slug || generateSlug(form.name),
      };

      if (editingCategory) {
        await adminApi.updateCategory(editingCategory.id, payload);
      } else {
        await adminApi.createCategory(payload);
      }

      await loadCategories();
      resetForm();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (category: CourseCategory) => {
    setEditingCategory(category);
    setForm({
      name: category.name,
      slug: category.slug || '',
      description: category.description || '',
      icon: category.icon || '',
      order: category.order || 0,
      is_active: category.is_active ?? true,
      parent_id: category.parent_id || null,
    });
    setSlugManuallyEdited(false);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t.categories.deleteConfirm)) return;

    try {
      await adminApi.deleteCategory(id);
      await loadCategories();
      if (selectedCategoryId === id && onSelectCategory) {
        onSelectCategory(null);
      }
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingCategory(null);
    setForm(emptyForm);
    setSlugManuallyEdited(false);
    setError('');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Выбор категории */}
      {onSelectCategory && (
        <div>
          <label className="block text-sm font-medium text-foreground mb-1.5 font-body">
            {t.categories.category}
          </label>
          <select
            value={selectedCategoryId || ''}
            onChange={(e) => onSelectCategory(e.target.value || null)}
            className="input"
          >
            <option value="">{t.categories.noCategory}</option>
            {categories.filter((c) => c.is_active).map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.icon && !isUrl(cat.icon) && `${cat.icon} `}
                {cat.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Управление категориями */}
      {showManagement && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-foreground font-heading">
              {t.categories.title}
            </h3>
            <button
              onClick={() => {
                resetForm();
                setShowForm(true);
              }}
              className="text-xs font-semibold text-primary hover:text-primary/80 font-body"
            >
              {t.categories.addCategory}
            </button>
          </div>

          {/* Форма создания/редактирования */}
          {showForm && (
            <form onSubmit={handleSubmit} className="bg-muted border border-border rounded-xl p-4 mb-4 space-y-3">
              {/* Name + Slug */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.categories.nameLabel} *
                  </label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => handleNameChange(e.target.value)}
                    className="input text-sm"
                    placeholder={t.categories.namePlaceholder}
                    required
                  />
                </div>
                <div>
                  <label className="flex items-center gap-1.5 text-xs font-medium text-foreground mb-1 font-body">
                    {t.categories.slugLabel}
                    {slugManuallyEdited && (
                      <span className="text-xs text-warning font-mono">
                        {t.categories.slugEdited}
                      </span>
                    )}
                  </label>
                  <div className="flex gap-1">
                    <input
                      type="text"
                      value={form.slug}
                      onChange={(e) => handleSlugChange(e.target.value)}
                      className="input text-sm font-mono flex-1"
                      placeholder={form.name ? generateSlug(form.name) : t.categories.slugAutoGenerated}
                    />
                    {slugManuallyEdited && (
                      <button
                        type="button"
                        onClick={() => {
                          setSlugManuallyEdited(false);
                          setForm((f) => ({ ...f, slug: generateSlug(f.name) }));
                        }}
                        className="btn-ghost text-xs px-2"
                        title={t.categories.regenerateSlug}
                      >
                        ↻
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-xs font-medium text-foreground mb-1 font-body">
                  {t.categories.description}
                </label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  rows={2}
                  className="input text-sm resize-none"
                  placeholder={t.categories.descriptionPlaceholder}
                />
              </div>

              {/* Icon + Order */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.categories.icon}
                  </label>
                  <input
                    type="text"
                    value={form.icon}
                    onChange={(e) => setForm({ ...form, icon: e.target.value })}
                    className="input text-sm"
                    placeholder={t.categories.iconPlaceholder}
                  />
                  {/* Превью иконки */}
                  {form.icon && (
                    <div className="mt-2 flex items-center gap-2">
                      <span className="text-xs text-muted-foreground font-body">{t.categories.preview}:</span>
                      <CategoryIcon icon={form.icon} size="md" />
                      {isUrl(form.icon) && (
                        <span className="text-xs text-muted-foreground truncate max-w-[200px] font-mono">
                          {form.icon}
                        </span>
                      )}
                    </div>
                  )}
                </div>
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.categories.order}
                  </label>
                  <input
                    type="number"
                    value={form.order}
                    onChange={(e) => setForm({ ...form, order: Number(e.target.value) })}
                    className="input text-sm"
                    min="0"
                  />
                </div>
              </div>

              {/* Parent + Active */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-foreground mb-1 font-body">
                    {t.categories.parentCategory}
                  </label>
                  <select
                    value={form.parent_id || ''}
                    onChange={(e) => setForm({ ...form, parent_id: e.target.value || null })}
                    className="input text-sm"
                  >
                    <option value="">{t.categories.noParent}</option>
                    {categories
                      .filter((c) => c.id !== editingCategory?.id)
                      .map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.name}
                        </option>
                      ))}
                  </select>
                </div>
                <div className="flex items-end pb-1">
                  <label className="flex items-center gap-2 text-sm text-foreground font-body cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.is_active}
                      onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                      className="w-4 h-4 rounded border-border text-primary focus:ring-primary/30"
                    />
                    {t.categories.active}
                  </label>
                </div>
              </div>

              {/* Preview */}
              {form.name && (
                <div className="bg-card border border-border rounded-xl p-2 text-xs">
                  <span className="text-muted-foreground font-body">{t.categories.previewUrl}:</span>{' '}
                  <span className="font-mono text-primary">
                    /categories/{form.slug || generateSlug(form.name)}
                  </span>
                </div>
              )}

              {/* Buttons */}
              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="btn-primary text-sm"
                >
                  {saving ? t.categories.saving : editingCategory ? t.categories.update : t.categories.create}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="btn-ghost text-sm"
                >
                  {t.categories.cancel}
                </button>
              </div>
            </form>
          )}

          {/* Список категорий */}
          <div className="space-y-2">
            {categories.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-3xl mb-3">🏷️</div>
                <p className="text-sm text-muted-foreground font-body">
                  {t.categories.noCategories}
                </p>
              </div>
            ) : (
              categories.map((cat) => (
                <div
                  key={cat.id}
                  className="flex items-center justify-between p-3 bg-card border border-border rounded-xl"
                >
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <CategoryIcon icon={cat.icon} size="md" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-foreground truncate font-body">
                          {cat.name}
                        </p>
                        {!cat.is_active && (
                          <span className="text-xs bg-muted text-muted-foreground px-1.5 py-0.5 rounded font-mono">
                            {t.categories.inactive}
                          </span>
                        )}
                      </div>
                      {cat.description && (
                        <p className="text-xs text-muted-foreground truncate font-body">
                          {cat.description}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4 flex-shrink-0">
                    <button
                      onClick={() => handleEdit(cat)}
                      className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                    >
                      {t.categories.edit}
                    </button>
                    <button
                      onClick={() => handleDelete(cat.id)}
                      className="text-xs text-destructive hover:text-destructive/80 font-semibold font-mono"
                    >
                      {t.categories.delete}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}
    </div>
  );
}