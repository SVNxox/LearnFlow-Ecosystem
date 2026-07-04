'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { api, handleApiError } from '@/lib/api';
import { adminApi } from '@/lib/admin-api';
import { CourseListItem } from '@/types/learning';
import { CourseCard, CourseCardSkeleton } from '@/components/course';
import { Navbar, EmptyState } from '@/components/ui';
import { Search, Filter, X, SlidersHorizontal, ArrowUpDown } from 'lucide-react';
import { useTranslation } from '@/lib/i18n/useTranslation';

const PAGE_SIZE = 12;

// Уровни курсов на основе estimated_weeks
const LEVELS = [
  { value: '', label: 'Barcha darajalar' },
  { value: 'beginner', label: '🌱 Boshlang\'ich', min: 0, max: 6 },
  { value: 'intermediate', label: '🚀 O\'rta', min: 7, max: 12 },
  { value: 'advanced', label: '⚡ Yuqori', min: 13, max: 999 },
];

// Ценовые категории
const PRICES = [
  { value: '', label: 'Barcha narxlar' },
  { value: 'free', label: '🆓 Bepul' },
  { value: 'paid', label: '💰 Pullik' },
];

// Сортировка
const SORT_OPTIONS = [
  { value: 'popular', label: '🔥 Mashhur' },
  { value: 'newest', label: '✨ Yangi' },
  { value: 'students', label: '👥 Ko\'p talabalar' },
  { value: 'duration_asc', label: '⏱ Qisqa kurslar' },
  { value: 'duration_desc', label: '⏱ Uzun kurslar' },
];

function CoursesContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { t } = useTranslation();

  // Параметры из URL
  const search = searchParams.get('search') || '';
  const format = searchParams.get('format') || '';
  const language = searchParams.get('language') || '';
  const category = searchParams.get('category') || '';
  const level = searchParams.get('level') || '';
  const price = searchParams.get('price') || '';
  const sort = searchParams.get('sort') || 'popular';
  const page = parseInt(searchParams.get('page') || '1', 10);

  // Состояния
  const [searchInput, setSearchInput] = useState(search);
  const [courses, setCourses] = useState<CourseListItem[]>([]);
  const [categories, setCategories] = useState<Array<{ id: string; name: string; slug: string }>>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Загрузка курсов
  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.learning.getCourses({
          search: search || undefined,
          language: language || undefined,
          category: category || undefined,
          page,
          page_size: PAGE_SIZE,
        });
        if (!active) return;

        let filteredCourses = data.results || [];

        // Фильтрация по формату (на клиенте)
        if (format === 'online') {
          filteredCourses = filteredCourses.filter(c => c.supports_online);
        } else if (format === 'offline') {
          filteredCourses = filteredCourses.filter(c => c.supports_offline);
        }

        // Фильтрация по уровню (на клиенте)
        if (level) {
          const levelConfig = LEVELS.find(l => l.value === level);
          if (levelConfig) {
            filteredCourses = filteredCourses.filter(c =>
              c.estimated_weeks &&
              c.estimated_weeks >= levelConfig.min &&
              c.estimated_weeks <= levelConfig.max
            );
          }
        }

        // Фильтрация по цене (на клиенте)
        if (price === 'free') {
          filteredCourses = filteredCourses.filter(c =>
            !c.price || parseFloat(c.price) === 0
          );
        } else if (price === 'paid') {
          filteredCourses = filteredCourses.filter(c =>
            c.price && parseFloat(c.price) > 0
          );
        }

        // Сортировка (на клиенте)
        filteredCourses = [...filteredCourses].sort((a, b) => {
          switch (sort) {
            case 'popular':
            case 'students':
              return (b.active_enrollment_count || 0) - (a.active_enrollment_count || 0);
            case 'duration_asc':
              return (a.estimated_weeks || 0) - (b.estimated_weeks || 0);
            case 'duration_desc':
              return (b.estimated_weeks || 0) - (a.estimated_weeks || 0);
            case 'newest':
            default:
              return 0;
          }
        });

        setCourses(filteredCourses);
        setTotalPages(data.total_pages || 1);
        setCount(data.count || 0);
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => { active = false; };
  }, [search, format, language, category, level, price, sort, page]);

  // Обновление параметров URL
  const updateParams = useCallback(
    (updates: Record<string, string | null>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(updates).forEach(([key, value]) => {
        if (value) params.set(key, value);
        else params.delete(key);
      });
      // Сбрасываем страницу при изменении фильтров
      if (!('page' in updates)) {
        params.delete('page');
      }
      router.push(`/courses?${params.toString()}`);
    },
    [router, searchParams]
  );

  // Автоматический поиск с debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== search) {
        updateParams({ search: searchInput || null });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchInput, search, updateParams]);

  // Загрузка курсов
  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.learning.getCourses({
          search: search || undefined,
          format: format || undefined,
          language: language || undefined,
          category: category || undefined,
          page,
          page_size: PAGE_SIZE,
        });
        if (!active) return;

        let filteredCourses = data.results || [];

        // Фильтрация по уровню (на клиенте)
        if (level) {
          const levelConfig = LEVELS.find(l => l.value === level);
          if (levelConfig) {
            filteredCourses = filteredCourses.filter(c =>
              c.estimated_weeks &&
              c.estimated_weeks >= levelConfig.min &&
              c.estimated_weeks <= levelConfig.max
            );
          }
        }

        // Фильтрация по цене (на клиенте)
        if (price === 'free') {
          filteredCourses = filteredCourses.filter(c =>
            !c.price || parseFloat(c.price) === 0
          );
        } else if (price === 'paid') {
          filteredCourses = filteredCourses.filter(c =>
            c.price && parseFloat(c.price) > 0
          );
        }

        // Сортировка (на клиенте)
        filteredCourses = [...filteredCourses].sort((a, b) => {
          switch (sort) {
            case 'popular':
              return (b.active_enrollment_count || 0) - (a.active_enrollment_count || 0);
            case 'students':
              return (b.active_enrollment_count || 0) - (a.active_enrollment_count || 0);
            case 'duration_asc':
              return (a.estimated_weeks || 0) - (b.estimated_weeks || 0);
            case 'duration_desc':
              return (b.estimated_weeks || 0) - (a.estimated_weeks || 0);
            case 'newest':
            default:
              return 0; // По умолчанию - как приходит с сервера
          }
        });

        setCourses(filteredCourses);
        setTotalPages(data.total_pages || 1);
        setCount(data.count || 0);
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    };
    load();
    return () => { active = false; };
  }, [search, format, language, category, level, price, sort, page]);

  // Сброс всех фильтров
  const resetFilters = () => {
    setSearchInput('');
    router.push('/courses');
  };

  // Активные фильтры
  const activeFiltersCount = [search, format, language, category, level, price].filter(Boolean).length;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mt-10 mb-6">
          <h1 className="text-3xl font-bold text-foreground font-heading">
            {t.coursesPage.title}
          </h1>
          <p className="text-muted-foreground text-sm mt-1 font-body">
            {count > 0
              ? `${count} ta kurs topildi`
              : t.coursesPage.subtitle}
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative max-w-2xl">
            <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder={t.coursesPage.search}
              className="input pl-11 pr-10 py-3 w-full"
            />
            {searchInput && (
              <button
                type="button"
                onClick={() => setSearchInput('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>

        {/* Filters Toggle & Sort */}
        <div className="flex flex-wrap items-center gap-3 mb-6">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-ghost inline-flex items-center gap-2 ${
              activeFiltersCount > 0 ? 'border-primary/40 text-primary' : ''
            }`}
          >
            <SlidersHorizontal size={16} />
            Filtrlar
            {activeFiltersCount > 0 && (
              <span className="ml-1 px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-semibold">
                {activeFiltersCount}
              </span>
            )}
          </button>

          {/* Sort Dropdown */}
          <div className="relative">
            <select
              value={sort}
              onChange={(e) => updateParams({ sort: e.target.value })}
              className="input py-2.5 pr-10 text-sm cursor-pointer"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <ArrowUpDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          </div>

          {activeFiltersCount > 0 && (
            <button
              onClick={resetFilters}
              className="text-sm text-destructive hover:text-destructive/80 font-semibold font-body"
            >
              <X size={14} className="inline mr-1" />
              Tozalash
            </button>
          )}
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="card p-5 mb-6 space-y-5">
            {/* Format */}
            <div>
              <p className="text-xs font-semibold text-foreground uppercase tracking-wider mb-3 font-mono">
                Format
              </p>
              <div className="flex flex-wrap gap-2">
                {[
                  { value: '', label: 'Barchasi' },
                  { value: 'online', label: '🌐 Onlayn' },
                  { value: 'offline', label: '🏫 Oflayn' },
                ].map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => updateParams({ format: opt.value || null })}
                    className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all font-body ${
                      format === opt.value
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground hover:text-foreground hover:bg-muted/80'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Language */}
            <div>
              <p className="text-xs font-semibold text-foreground uppercase tracking-wider mb-3 font-mono">
                {t.coursesPage.language}
              </p>
              <div className="flex flex-wrap gap-2">
                {[
                  { value: '', label: 'Ixtiyoriy' },
                  { value: 'ru', label: 'Русский' },
                  { value: 'en', label: 'English' },
                  { value: 'uz', label: 'O\'zbekcha' },
                ].map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => updateParams({ language: opt.value || null })}
                    className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all font-body ${
                      language === opt.value
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground hover:text-foreground hover:bg-muted/80'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Category */}
            {categories.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-foreground uppercase tracking-wider mb-3 font-mono">
                  Kategoriya
                </p>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => updateParams({ category: null })}
                    className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all font-body ${
                      !category
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground hover:text-foreground hover:bg-muted/80'
                    }`}
                  >
                    Barchasi
                  </button>
                  {categories.map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => updateParams({ category: cat.id })}
                      className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all font-body ${
                        category === cat.id
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground hover:text-foreground hover:bg-muted/80'
                      }`}
                    >
                      {cat.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Level */}
            <div>
              <p className="text-xs font-semibold text-foreground uppercase tracking-wider mb-3 font-mono">
                Daraja
              </p>
              <div className="flex flex-wrap gap-2">
                {LEVELS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => updateParams({ level: opt.value || null })}
                    className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all font-body ${
                      level === opt.value
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground hover:text-foreground hover:bg-muted/80'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Price */}
            <div>
              <p className="text-xs font-semibold text-foreground uppercase tracking-wider mb-3 font-mono">
                Narx
              </p>
              <div className="flex flex-wrap gap-2">
                {PRICES.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => updateParams({ price: opt.value || null })}
                    className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all font-body ${
                      price === opt.value
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground hover:text-foreground hover:bg-muted/80'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div>
          {error && (
            <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-6 font-body">
              {error}
            </div>
          )}

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
              {Array.from({ length: 9 }).map((_, i) => (
                <CourseCardSkeleton key={i} />
              ))}
            </div>
          ) : courses.length === 0 ? (
            <div className="card p-12 text-center">
              <div className="text-5xl mb-4">🔍</div>
              <h3 className="text-lg font-semibold text-foreground mb-2 font-heading">
                {t.coursesPage.noCourses}
              </h3>
              <p className="text-sm text-muted-foreground mb-6 font-body">
                {t.coursesPage.noCoursesDesc}
              </p>
              {activeFiltersCount > 0 && (
                <button onClick={resetFilters} className="btn-primary inline-flex items-center gap-2">
                  <X size={14} />
                  Filtrlarni tozalash
                </button>
              )}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                {courses.map((course) => (
                  <CourseCard key={course.id} course={course} />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-10">
                  <button
                    disabled={page <= 1}
                    onClick={() => updateParams({ page: String(page - 1) })}
                    className="btn-ghost text-sm disabled:opacity-40"
                  >
                    {t.coursesPage.pagination.previous}
                  </button>
                  {Array.from({ length: totalPages }, (_, i) => i + 1)
                    .filter((p) => Math.abs(p - page) <= 2 || p === 1 || p === totalPages)
                    .map((p, idx, arr) => (
                      <span key={p} className="flex items-center">
                        {idx > 0 && arr[idx - 1] !== p - 1 && (
                          <span className="px-1 text-muted-foreground">…</span>
                        )}
                        <button
                          onClick={() => updateParams({ page: String(p) })}
                          className={`w-9 h-9 rounded-xl text-sm font-semibold transition-all ${
                            p === page
                              ? 'bg-primary text-primary-foreground'
                              : 'border border-border text-muted-foreground hover:bg-muted hover:text-foreground'
                          }`}
                        >
                          {p}
                        </button>
                      </span>
                    ))}
                  <button
                    disabled={page >= totalPages}
                    onClick={() => updateParams({ page: String(page + 1) })}
                    className="btn-ghost text-sm disabled:opacity-40"
                  >
                    {t.coursesPage.pagination.next}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function CoursesPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <CoursesContent />
    </Suspense>
  );
}