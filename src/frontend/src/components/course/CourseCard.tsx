import Link from 'next/link';
import { CourseListItem } from '@/types/learning';
import { useTranslation } from '@/lib/i18n/useTranslation';

export interface CourseCardProps {
  course: CourseListItem;
}

const GRADIENTS = [
  'from-blue-500 to-indigo-600',
  'from-violet-500 to-purple-600',
  'from-emerald-500 to-teal-600',
  'from-orange-500 to-rose-500',
];

function gradientFor(id: string) {
  let hash = 0;
  for (let i = 0; i < id.length; i++) hash = (hash + id.charCodeAt(i)) % GRADIENTS.length;
  return GRADIENTS[hash];
}

// ✅ ИСПРАВЛЕННАЯ функция форматирования цены
function formatPrice(price: string | number | undefined | null, currency: string | undefined | null): string {
  // Если price не определён или пустой
  if (price === undefined || price === null || price === '') {
    return 'Bepul';
  }

  // Преобразуем в число
  const num = typeof price === 'string' ? parseFloat(price) : price;

  // Если не удалось преобразовать или равно 0
  if (isNaN(num) || num === 0) {
    return 'Bepul';
  }

  // Форматируем в зависимости от валюты
  if (currency === 'UZS') {
    return `${num.toLocaleString('ru-RU')} so'm`;
  } else if (currency === 'USD') {
    return `$${num.toFixed(2)}`;
  }

  // По умолчанию
  return `${num.toLocaleString('ru-RU')} ${currency || 'so\'m'}`;
}

export default function CourseCard({ course }: CourseCardProps) {
  const { t } = useTranslation();

  // ✅ ИСПРАВЛЕННАЯ проверка на бесплатность
  const isFree = !course.price ||
                 course.price === '' ||
                 course.price === '0' ||
                 course.price === '0.00' ||
                 parseFloat(course.price) === 0;

  return (
    <Link
      href={`/courses/${course.slug}`}
      className="card overflow-hidden flex flex-col h-full hover:border-primary/30 transition-all duration-200 group"
    >
      {/* Thumbnail */}
      <div
        className={`h-36 bg-gradient-to-br ${gradientFor(course.id)} flex items-center justify-center text-white text-4xl relative overflow-hidden`}
      >
        {course.thumbnail_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={course.thumbnail_url} alt={course.title} className="w-full h-full object-cover" />
        ) : (
          '💻'
        )}

        {/* Price Badge */}
        <div className={`absolute top-3 right-3 px-3 py-1 rounded-lg text-xs font-bold font-mono ${
          isFree 
            ? 'bg-success text-success-foreground' 
            : 'bg-accent text-accent-foreground'
        }`}>
          {isFree ? '🆓 Bepul' : '💰 Pullik'}
        </div>
      </div>

      {/* Content */}
      <div className="p-5 flex flex-col flex-1">
        {/* Category */}
        {course.category && (
          <span className="text-xs font-semibold text-primary mb-1 font-mono">
            {course.category.name}
          </span>
        )}

        {/* Title */}
        <h3 className="text-base font-semibold text-foreground mb-1 line-clamp-2 font-heading group-hover:text-primary transition-colors">
          {course.title}
        </h3>

        {/* Description */}
        <p className="text-sm text-muted-foreground mb-4 line-clamp-2 flex-1 font-body">
          {course.short_description}
        </p>

        {/* Meta info */}
        <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
          <div className="flex gap-1.5 flex-wrap">
            {course.supports_online && (
              <span className="px-2 py-0.5 rounded-full bg-info/10 text-info font-mono">
                {t.courses.online}
              </span>
            )}
            {course.supports_offline && (
              <span className="px-2 py-0.5 rounded-full bg-purple/10 text-purple font-mono">
                {t.courses.offline}
              </span>
            )}
          </div>
          {course.estimated_weeks && (
            <span className="font-mono">
              {course.estimated_weeks} {t.courses.weeks}
            </span>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-border">
          <div className="text-xs text-muted-foreground font-mono">
            {course.active_enrollment_count} {t.courses.studentsEnrolled}
          </div>

          {/* ✅ Price - теперь правильно отображается */}
          <div className={`text-sm font-bold font-heading ${
            isFree ? 'text-success' : 'text-accent'
          }`}>
            {formatPrice(course.price, course.currency)}
          </div>
        </div>
      </div>
    </Link>
  );
}

export function CourseCardSkeleton() {
  return (
    <div className="card overflow-hidden animate-pulse">
      <div className="h-36 bg-muted" />
      <div className="p-5 space-y-3">
        <div className="h-3 bg-muted rounded w-1/3" />
        <div className="h-4 bg-muted rounded w-full" />
        <div className="h-4 bg-muted rounded w-2/3" />
        <div className="h-3 bg-muted rounded w-1/2 mt-4" />
      </div>
    </div>
  );
}