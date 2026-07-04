'use client';

import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';
import {
  ArrowRight, BookOpen, Users, Award, Star, CheckCircle,
  Zap, Clock, GraduationCap, TrendingUp, Globe, AlertCircle,
  Play, ChevronRight, Flame, LogOut, Settings, User,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { CourseListItem } from '@/types/learning';

// ── Dashboard preview widget ──────────────────────────────────────────────────

function DashboardPreview() {
  return (
    <div className="relative">
      <div
        className="absolute -inset-6 rounded-3xl pointer-events-none"
        style={{ background: 'radial-gradient(ellipse at center, rgba(129,140,248,0.1) 0%, transparent 70%)' }}
      />

      <div className="relative bg-card border border-border rounded-2xl overflow-hidden shadow-2xl">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-primary/20 flex items-center justify-center">
              <GraduationCap size={14} className="text-primary" />
            </div>
            <span className="text-sm font-semibold text-foreground font-body">Mening progressim</span>
          </div>
          <span className="code-badge text-primary">faol</span>
        </div>

        <div className="p-5 space-y-4">
          <div>
            <div className="flex justify-between mb-1.5">
              <span className="text-sm text-foreground font-medium font-body">Python dasturlash asoslari</span>
              <span className="text-xs text-primary font-bold font-mono">73%</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill bg-primary" style={{ width: '73%' }} />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Modul', value: '4 / 6', color: 'text-primary' },
              { label: 'Baho', value: '88/100', color: 'text-[
              { label: 'Streak', value: '12 kun', color: 'text-accent' },
            ].map((s) => (
              <div key={s.label} className="bg-muted rounded-xl p-3">
                <p className={`text-base font-extrabold font-heading ${s.color}`}>{s.value}</p>
                <p className="text-xs text-muted-foreground mt-0.5 font-body">{s.label}</p>
              </div>
            ))}
          </div>

          <div className="border border-primary/20 rounded-xl p-4 bg-primary/5">
            <p className="text-xs text-muted-foreground mb-1 font-body">Keyingi dars</p>
            <p className="text-sm font-semibold text-foreground mb-3 font-body">
              4.3 — Fayllar va istisnolar bilan ishlash
            </p>
            <button className="w-full py-2 bg-primary text-primary-foreground text-sm font-bold rounded-lg font-body">
              Davom ettirish
            </button>
          </div>

          <div className="space-y-2">
            {[
              { text: 'Dars 4.2 tugatildi ✓', time: '2 soat oldin', color: '
              { text: 'Uy vazifasi 
              { text: 'Modul 3 testi — 92/100', time: '2 kun oldin', color: '
            ].map((a, i) => (
              <div key={i} className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: a.color }} />
                <span className="text-xs text-muted-foreground flex-1 font-body">{a.text}</span>
                <span className="text-xs text-muted-foreground font-mono">{a.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── User Dropdown Menu ────────────────────────────────────────────────────────

function UserDropdown() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }

    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [menuOpen]);

  if (!user) return null;

  const userName = user.info?.first_name
    ? `${user.info.first_name} ${user.info?.last_name || ''}`.trim()
    : user.email.split('@')[0];

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setMenuOpen(!menuOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-border bg-card hover:border-primary/40 transition-colors"
      >
        <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center">
          <User size={11} className="text-primary" />
        </div>
        <span className="text-sm text-foreground font-body hidden sm:block">
          {userName}
        </span>
        <ChevronRight size={12} className={`text-muted-foreground transition-transform ${menuOpen ? 'rotate-90' : ''}`} />
      </button>

      {menuOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />

          <div className="absolute right-0 top-11 z-50 w-52 bg-card border border-border rounded-xl shadow-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-border">
              <p className="text-sm font-semibold text-foreground font-body">
                {userName}
              </p>
              <p className="text-xs text-muted-foreground font-mono">{user.email}</p>
            </div>

            <nav className="p-1.5">
              {[
                { href: '/dashboard', label: 'Boshqaruv paneli', icon: BookOpen },
                { href: '/certificates', label: 'Sertifikatlar', icon: Award },
                { href: '/profile', label: 'Sozlamalar', icon: Settings },
              ].map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-colors font-body"
                >
                  <item.icon size={14} />
                  {item.label}
                </Link>
              ))}
              <button
                onClick={() => {
                  logout();
                  setMenuOpen(false);
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-destructive hover:bg-destructive/10 transition-colors font-body"
              >
                <LogOut size={14} />
                Chiqish
              </button>
            </nav>
          </div>
        </>
      )}
    </div>
  );
}

// ── Helpers ───────────────────────────────────────────────────────────────────

// Определяем уровень курса по estimated_weeks
function getCourseLevel(weeks?: number): string {
  if (!weeks) return 'O\'rta';
  if (weeks <= 6) return 'Boshlang\'ich';
  if (weeks <= 12) return 'O\'rta';
  return 'Yuqori';
}

// Форматируем количество студентов
function formatStudents(count: number): string {
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K+`;
  }
  return count.toString();
}

// Получаем тег для курса
function getCourseTag(course: CourseListItem): { label: string; color: string } | null {
  if (course.active_enrollment_count > 500) {
    return { label: 'Mashhur', color: '
  }
  // Можно добавить логику для "Yangi" по дате создания
  return null;
}

// ── Main landing page ─────────────────────────────────────────────────────────

export default function HomePage() {
  const { user } = useAuth();
  const [courses, setCourses] = useState<CourseListItem[]>([]);
  const [stats, setStats] = useState({
    totalCourses: 0,
    totalStudents: 0,
    loading: true,
  });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Загружаем курсы и статистику из реального API
  useEffect(() => {
    const loadData = async () => {
      try {
        // Загружаем курсы (публичный endpoint)
        const data = await api.learning.getCourses({ page_size: 6 });
        const coursesList = data.results || [];

        // Показываем только опубликованные курсы (первые 3)
        setCourses(coursesList.slice(0, 3));

        // Считаем статистику
        const totalStudents = coursesList.reduce(
          (sum, c) => sum + (c.active_enrollment_count || 0), 0
        );

        setStats({
          totalCourses: data.count || coursesList.length,
          totalStudents,
          loading: false,
        });
      } catch (err) {
        console.error('[HomePage] Failed to load data:', err);
        setStats(s => ({ ...s, loading: false }));
      }
    };
    loadData();
  }, []);

  // Динамическая статистика
  const STATS = [
    { value: stats.totalStudents > 0 ? formatStudents(stats.totalStudents) : '—', label: 'Talabalar' },
    { value: stats.totalCourses > 0 ? stats.totalCourses.toString() : '—', label: 'Kurslar' },
    { value: '48 soat', label: 'O\'rtacha tekshiruv vaqti' },
    { value: '4.9', label: 'Reyting' },
  ];

  const FEATURES = [
    { icon: Users, label: 'Jonli mentorlar', desc: 'Amaliyotchi dasturchilardan kod-revyu', color: '
    { icon: CheckCircle, label: 'Avtomatik tekshiruv', desc: 'Kod va testlarni bir zumda tekshirish', color: '
    { icon: Award, label: 'Sertifikatlar', desc: 'learnflow.uz orqali tasdiqlanadigan', color: '
    { icon: Globe, label: 'Online + Offline', desc: 'Sizga qulay formatda o\'qish', color: '
  ];

  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">

      {/* ─── Navbar ─────────────────────────────────────────────────────── */}
      <header className="fixed top-0 left-0 right-0 z-50 h-14 glass border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-full flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
              <GraduationCap size={14} className="text-primary-foreground" />
            </div>
            <span className="text-base font-bold text-foreground font-heading tracking-tight">
              LearnFlow
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-1">
            {[
              { href: '/courses', label: 'Kurslar' },
              { href: '/about', label: 'Biz haqimizda' },
              { href: '/certificates/verify/demo', label: 'Sertifikat tekshirish' },
            ].map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground rounded-lg hover:bg-muted transition-colors font-body"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            {user ? (
              <UserDropdown />
            ) : (
              <>
                <Link
                  href="/login"
                  className="hidden sm:block text-sm text-muted-foreground hover:text-foreground transition-colors font-body"
                >
                  Kirish
                </Link>
                <Link
                  href="/register"
                  className="btn-primary text-sm py-2 px-4"
                >
                  Ro'yxatdan o'tish
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* ─── Hero ───────────────────────────────────────────────────────── */}
      <section className="relative min-h-screen flex items-center overflow-hidden pt-14">
        <div className="absolute inset-0 bg-grid pointer-events-none opacity-100" />
        <div
          className="absolute top-1/4 left-1/4 w-[600px] h-[600px] rounded-full pointer-events-none"
          style={{
            background: 'radial-gradient(circle, rgba(129,140,248,0.12) 0%, transparent 70%)',
            transform: 'translate(-50%, -50%)',
          }}
        />
        <div
          className="absolute bottom-0 right-1/4 w-[400px] h-[400px] rounded-full pointer-events-none"
          style={{
            background: 'radial-gradient(circle, rgba(251,191,36,0.07) 0%, transparent 70%)',
            transform: 'translate(50%, 50%)',
          }}
        />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 w-full py-20">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-primary/30 bg-primary/10 mb-8">
                <Zap size={12} className="text-primary" />
                <span className="text-xs text-primary font-semibold font-mono">
                  MVP 95% · O'zbekistonda ishga tushirilgan
                </span>
              </div>

              <h1 className="text-5xl md:text-7xl font-extrabold text-foreground leading-[0.95] tracking-tight mb-6 font-heading">
                IT karera<br />
                <span className="text-primary">shu yerdan</span><br />
                boshlanadi.
              </h1>

              <p className="text-lg text-muted-foreground leading-relaxed mb-10 max-w-md font-body">
                Jonli mentorlar, avtomatik kod tekshiruvi va tasdiqlanadigan sertifikatlar bilan to'liq LMS platforma.
              </p>

              <div className="flex flex-wrap gap-4 mb-12">
                <Link
                  href="/register"
                  className="group inline-flex items-center gap-2 btn-primary"
                >
                  O'qishni boshlash
                  <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  href="/courses"
                  className="group inline-flex items-center gap-2 btn-ghost"
                >
                  <BookOpen size={14} className="text-primary" />
                  Kurslarni ko'rish
                </Link>
              </div>

              <div className="flex items-center gap-6">
                <div className="flex -space-x-2">
                  {[
                    'photo-1507003211169-0a1dd7228f2d',
                    'photo-1494790108755-2616b612b786',
                    'photo-1500648767791-00dcc994a43e',
                    'photo-1438761681033-6461ffad8d80',
                  ].map((id, i) => (
                    <img
                      key={i}
                      src={`https://images.unsplash.com/${id}?w=40&h=40&fit=crop&auto=format`}
                      alt="Student"
                      className="w-9 h-9 rounded-full border-2 border-background object-cover"
                    />
                  ))}
                </div>
                <div>
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} size={12} className="fill-accent text-accent" />
                    ))}
                    <span className="text-sm font-semibold text-foreground ml-1">4.9</span>
                  </div>
                  <p className="text-xs text-muted-foreground font-body">
                    {stats.loading
                      ? 'Yuklanmoqda...'
                      : stats.totalStudents > 0
                        ? `${formatStudents(stats.totalStudents)} talabalar`
                        : 'Talabalar kutmoqda'}
                  </p>
                </div>
              </div>
            </div>

            <div className="hidden lg:block">
              <DashboardPreview />
            </div>
          </div>
        </div>
      </section>

      {/* ─── Stats bar ──────────────────────────────────────────────────── */}
      <section className="border-y border-border bg-card/50 py-12 md:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.loading ? (
            // Skeleton loading
            Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="text-center">
                <div className="h-10 bg-muted rounded animate-pulse mx-auto mb-2 w-24" />
                <div className="h-4 bg-muted rounded animate-pulse mx-auto w-16" />
              </div>
            ))
          ) : (
            STATS.map((s) => (
              <div key={s.label} className="text-center">
                <p className="text-3xl md:text-4xl font-extrabold text-foreground font-heading">
                  {s.value}
                </p>
                <p className="text-sm text-muted-foreground mt-2 font-body">{s.label}</p>
              </div>
            ))
          )}
        </div>
      </section>

      {/* ─── Features ───────────────────────────────────────────────────── */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-14">
          <p className="section-label mb-4">Nega LearnFlow</p>
          <h2 className="text-4xl md:text-5xl font-extrabold text-foreground font-heading">
            IT karera uchun<br />hamma narsa.
          </h2>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURES.map((f) => (
            <div key={f.label} className="card p-6 hover:border-primary/30 transition-all group">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                style={{ backgroundColor: f.color + '15' }}
              >
                <f.icon size={20} style={{ color: f.color }} />
              </div>
              <h3 className="text-base font-bold text-foreground mb-1 font-heading">{f.label}</h3>
              <p className="text-sm text-muted-foreground font-body leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ─── Courses ────────────────────────────────────────────────────── */}
      <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-end justify-between mb-12">
          <div>
            <p className="section-label mb-4">Kurslar katalogi</p>
            <h2 className="text-4xl md:text-5xl font-extrabold text-foreground font-heading">
              Ishga qabul qiladigan<br />texnologiyalar.
            </h2>
          </div>
          <Link
            href="/courses"
            className="hidden md:flex items-center gap-1.5 text-sm text-primary hover:text-primary/80 transition-colors font-body"
          >
            Barcha kurslar <ChevronRight size={14} />
          </Link>
        </div>

        {stats.loading ? (
          // Skeleton loading для курсов
          <div className="grid md:grid-cols-3 gap-5">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="card overflow-hidden">
                <div className="aspect-[16/9] bg-muted animate-pulse" />
                <div className="p-5 space-y-3">
                  <div className="h-3 bg-muted rounded animate-pulse w-1/2" />
                  <div className="h-5 bg-muted rounded animate-pulse w-3/4" />
                  <div className="h-3 bg-muted rounded animate-pulse w-full" />
                </div>
              </div>
            ))}
          </div>
        ) : courses.length === 0 ? (
          // Пустое состояние
          <div className="card p-12 text-center">
            <div className="text-5xl mb-4">📚</div>
            <h3 className="text-lg font-semibold text-foreground mb-2 font-heading">
              Hozircha kurslar yo'q
            </h3>
            <p className="text-sm text-muted-foreground mb-6 font-body">
              Yangi kurslar tez orada qo'shiladi.
            </p>
            <Link href="/courses" className="btn-primary inline-flex items-center gap-2">
              <BookOpen size={14} />
              Barcha kurslarni ko'rish
            </Link>
          </div>
        ) : (
          // Реальные курсы из API
          <div className="grid md:grid-cols-3 gap-5">
            {courses.map((course) => {
              const tag = getCourseTag(course);
              return (
                <Link
                  key={course.id}
                  href={`/courses/${course.slug}`}
                  className="group card overflow-hidden hover:border-primary/30 transition-all hover:-translate-y-1 duration-200"
                >
                  {/* Thumbnail */}
                  <div className="relative aspect-[16/9] bg-muted overflow-hidden">
                    {course.thumbnail_url ? (
                      <img
                        src={course.thumbnail_url}
                        alt={course.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-4xl bg-gradient-to-br from-primary/20 to-accent/20">
                        📚
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-card via-transparent to-transparent opacity-80" />
                    {tag && (
                      <div
                        className="absolute top-3 left-3 text-xs font-bold px-2.5 py-1 rounded-full font-mono"
                        style={{
                          backgroundColor: tag.color + '20',
                          color: tag.color,
                          border: `1px solid ${tag.color}40`,
                        }}
                      >
                        {tag.label}
                      </div>
                    )}
                  </div>

                  {/* Body */}
                  <div className="p-5">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-xs text-muted-foreground font-mono">
                        {getCourseLevel(course.estimated_weeks)}
                      </span>
                      <span className="w-1 h-1 rounded-full bg-border" />
                      <span className="text-xs text-muted-foreground font-mono">
                        {course.estimated_weeks ? `${course.estimated_weeks} hafta` : '—'}
                      </span>
                    </div>

                    <h3 className="text-lg font-bold text-foreground mb-3 font-heading group-hover:text-primary transition-colors line-clamp-2">
                      {course.title}
                    </h3>

                    {course.category && (
                      <div className="flex flex-wrap gap-1.5 mb-4">
                        <span className="text-xs px-2 py-0.5 rounded-md bg-primary/10 text-primary font-mono">
                          {course.category.name}
                        </span>
                        {course.supports_online && (
                          <span className="text-xs px-2 py-0.5 rounded-md bg-muted text-muted-foreground font-body">
                            🌐 Online
                          </span>
                        )}
                        {course.supports_offline && (
                          <span className="text-xs px-2 py-0.5 rounded-md bg-muted text-muted-foreground font-body">
                            🏫 Offline
                          </span>
                        )}
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t border-border">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Users size={12} />
                          <span className="text-xs font-body">
                            {course.active_enrollment_count || 0} talaba
                          </span>
                        </div>
                      </div>
                      <span className="text-sm font-semibold text-primary flex items-center gap-1 font-body">
                        Batafsil <ArrowRight size={13} />
                      </span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}

        <div className="mt-8 text-center md:hidden">
          <Link href="/courses" className="btn-ghost inline-flex items-center gap-2">
            Barcha kurslar <ChevronRight size={14} />
          </Link>
        </div>
      </section>

      {/* ─── CTA Banner ─────────────────────────────────────────────────── */}
      <section className="pb-24 max-w-7xl mx-auto px-4 sm:px-6">
        <div
          className="relative rounded-3xl overflow-hidden px-8 md:px-16 py-16 text-center"
          style={{
            background: 'linear-gradient(135deg, 
            border: '1px solid rgba(129,140,248,0.2)',
          }}
        >
          <div
            className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] pointer-events-none"
            style={{ background: 'radial-gradient(ellipse at top, rgba(129,140,248,0.15) 0%, transparent 70%)' }}
          />

          <div className="relative max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-accent/30 bg-accent/10 mb-6">
              <Flame size={12} className="text-accent" />
              <span className="text-xs text-accent font-semibold font-mono">Bugundan boshlang</span>
            </div>

            <h2 className="text-4xl md:text-5xl font-extrabold text-foreground mb-4 font-heading">
              Sizning IT karerangiz bir bosishdan boshlanadi.
            </h2>
            <p className="text-base text-muted-foreground mb-10 font-body">
              {stats.loading
                ? 'Allaqachon LearnFlow bilan karera qurayotgan talabalarga qo\'shiling.'
                : stats.totalStudents > 0
                  ? `Allaqachon LearnFlow bilan karera qurayotgan ${formatStudents(stats.totalStudents)} talabalarga qo'shiling.`
                  : 'Allaqachon LearnFlow bilan karera qurayotgan talabalarga qo\'shiling.'}
            </p>

            <div className="flex flex-wrap gap-4 justify-center">
              <Link href="/register" className="group btn-primary inline-flex items-center gap-2 py-4 px-8">
                Bepul boshlash
                <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link href="/dashboard/student" className="btn-ghost inline-flex items-center gap-2 py-4 px-8">
                <Users size={15} /> Demo dashboard
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Footer ─────────────────────────────────────────────────────── */}
      <footer className="border-t border-border bg-card/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
                  <GraduationCap size={14} className="text-primary-foreground" />
                </div>
                <span className="text-base font-bold font-heading">LearnFlow</span>
              </div>
              <p className="text-sm text-muted-foreground font-body leading-relaxed">
                O'zbekistonda professional IT ta'lim.
              </p>
            </div>

            {[
              {
                label: 'O\'qish',
                links: [
                  { href: '/courses', label: 'Kurslar katalogi' },
                  { href: '/courses?category=Backend', label: 'Backend' },
                  { href: '/courses?category=Frontend', label: 'Frontend' },
                  { href: '/courses?category=Data', label: 'Data Science' },
                ],
              },
              {
                label: 'Platforma',
                links: [
                  { href: '/dashboard/student', label: 'Talaba dashboardi' },
                  { href: '/certificates', label: 'Sertifikatlar' },
                  { href: '/certificates/verify/demo', label: 'Sertifikat tekshirish' },
                ],
              },
              {
                label: 'Kompaniya',
                links: [
                  { href: '/about', label: 'Biz haqimizda' },
                  { href: '/contact', label: 'Kontaktlar' },
                ],
              },
            ].map((col) => (
              <div key={col.label}>
                <p className="text-sm font-semibold text-foreground uppercase tracking-wider mb-4 font-mono">
                  {col.label}
                </p>
                <ul className="space-y-2">
                  {col.links.map((l) => (
                    <li key={l.href}>
                      <Link
                        href={l.href}
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors font-body"
                      >
                        {l.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground font-mono">
              © 2026 LearnFlow. Barcha huquqlar himoyalangan.
            </p>
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground font-mono">
              <span className="w-2 h-2 rounded-full bg-[
              Barcha tizimlar ishlayapti
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}