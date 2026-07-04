'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  GraduationCap, LayoutDashboard, Users, BookOpen, ListOrdered,
  CreditCard, Award, BarChart3, LogOut, ChevronRight, Inbox,
  CheckSquare, Calendar, TrendingUp, Palette,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

// ── Types ─────────────────────────────────────────────────────────────────────

type Role = 'admin' | 'staff' | 'mentor';

interface NavSection {
  label?: string;
  items: {
    href: string;
    label: string;
    icon: React.ElementType;
    badge?: number;
  }[];
}

const NAV_CONFIG: Record<Role, NavSection[]> = {
  admin: [
    {
      items: [
        { href: '/dashboard/admin', label: 'Boshqaruv paneli', icon: LayoutDashboard },
      ],
    },
    {
      label: 'Boshqaruv',
      items: [
        { href: '/dashboard/admin/users',       label: 'Foydalanuvchilar',       icon: Users },
        { href: '/admin/courses',               label: 'Kurslar',                icon: BookOpen },
        { href: '/dashboard/admin/enrollments', label: 'Ro\'yxatdan o\'tganlar', icon: ListOrdered },
      ],
    },
    {
      label: 'Moliya',
      items: [
        { href: '/dashboard/admin/payments',     label: 'To\'lovlar',     icon: CreditCard },
        { href: '/dashboard/admin/certificates', label: 'Sertifikatlar',  icon: Award },
        { href: '/dashboard/admin/certificates/templates', label: 'Shablonlar', icon: Palette },
      ],
    },
    {
      label: 'Tahlil',
      items: [
        { href: '/dashboard/admin/analytics', label: 'Statistika', icon: BarChart3 },
      ],
    },
  ],
  staff: [
    {
      items: [
        { href: '/dashboard/staff', label: 'Boshqaruv paneli', icon: LayoutDashboard },
      ],
    },
    {
      label: 'Kontent',
      items: [
        { href: '/admin/courses',               label: 'Kurslar',                icon: BookOpen },
        { href: '/dashboard/admin/enrollments', label: 'Ro\'yxatdan o\'tganlar', icon: ListOrdered },
      ],
    },
  ],
  mentor: [
    {
      items: [
        { href: '/dashboard/mentor', label: 'Boshqaruv paneli', icon: LayoutDashboard },
      ],
    },
    {
      label: 'Navbat',
      items: [
        { href: '/dashboard/mentor/assessments', label: 'Testlar', icon: CheckSquare, badge: 5 },
        { href: '/dashboard/mentor/submissions', label: 'Ishlar',  icon: Inbox,       badge: 12 },
      ],
    },
    {
      label: 'Talabalar',
      items: [
        { href: '/dashboard/mentor/students',   label: 'Mening talabalarim', icon: Users },
        { href: '/dashboard/mentor/attendance', label: 'Davomat',            icon: Calendar },
      ],
    },
    {
      label: 'Hisobotlar',
      items: [
        { href: '/dashboard/mentor/statistics', label: 'Statistika', icon: TrendingUp },
      ],
    },
  ],
};

// ── Sidebar component ─────────────────────────────────────────────────────────

export function AdminSidebar({ role }: { role: Role }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const sections = NAV_CONFIG[role];

  const name = user?.info?.first_name
    ? `${user.info.first_name} ${user.info.last_name ?? ''}`.trim()
    : user?.email?.split('@')[0] ?? '';

  const isActive = (href: string) =>
    pathname === href || (href !== '/dashboard/admin' && href !== '/dashboard/staff' && href !== '/dashboard/mentor' && pathname.startsWith(href));

  return (
    <aside className="w-60 flex-shrink-0 hidden lg:flex flex-col border-r border-sidebar-border bg-sidebar min-h-screen fixed left-0 top-0 z-20">
      {/* Logo */}
      <div className="h-14 flex items-center gap-2.5 px-5 border-b border-sidebar-border">
        <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
          <GraduationCap size={14} className="text-primary-foreground" />
        </div>
        <span className="text-base font-bold text-foreground font-heading tracking-tight">
          LearnFlow
        </span>
        <span className="ml-auto text-[10px] font-mono px-1.5 py-0.5 rounded-md bg-primary/10 text-primary capitalize">
          {role}
        </span>
      </div>

      {/* User */}
      <div className="px-4 py-3 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-bold text-primary font-mono">
              {name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-foreground font-body truncate">{name}</p>
            <p className="text-xs text-muted-foreground font-mono truncate">{user?.email}</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
        {sections.map((section, si) => (
          <div key={si}>
            {section.label && (
              <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-widest font-mono px-3 mb-1.5">
                {section.label}
              </p>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`
                      flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all
                      font-body
                      ${active
                        ? 'bg-primary/10 text-primary font-semibold'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'}
                    `}
                  >
                    <item.icon size={16} />
                    <span className="flex-1 truncate">{item.label}</span>
                    {item.badge && (
                      <span
                        className="text-[10px] px-1.5 py-0.5 rounded-md font-bold font-mono"
                        style={{ backgroundColor: 'var(--color-warning-bg)', color: 'var(--color-warning)' }}
                      >
                        {item.badge}
                      </span>
                    )}
                    {active && <ChevronRight size={12} className="text-primary flex-shrink-0" />}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-3 py-4 border-t border-sidebar-border">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all font-body"
        >
          <LogOut size={16} />
          Chiqish
        </button>
      </div>
    </aside>
  );
}

// ── Admin layout wrapper ──────────────────────────────────────────────────────

export function AdminLayout({
  children,
  role,
  title,
  subtitle,
  action,
}: {
  children: React.ReactNode;
  role: Role;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-background">
      <AdminSidebar role={role} />

      {/* Main content — offset by sidebar width */}
      <div className="flex-1 lg:ml-60">
        {/* Top bar */}
        <div className="sticky top-0 z-10 h-14 glass border-b border-border flex items-center px-6 gap-4">
          <div className="flex-1 min-w-0">
            <h1 className="text-base font-semibold text-foreground font-heading truncate">{title}</h1>
            {subtitle && (
              <p className="text-xs text-muted-foreground font-body">{subtitle}</p>
            )}
          </div>
          {action && <div className="flex-shrink-0">{action}</div>}
        </div>

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}

// ── Admin stat card ───────────────────────────────────────────────────────────

export function AdminStatCard({
  label,
  value,
  icon: Icon,
  color,
  sub,
  trend,
}: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
  sub?: string;
  trend?: { value: string; positive: boolean };
}) {
  return (
    <div className="stat-card">
      <div className="flex items-start justify-between mb-3">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: color + '18' }}
        >
          <Icon size={17} style={{ color }} />
        </div>
        {trend && (
          <span
            className="text-xs font-semibold font-mono"
            style={{ color: trend.positive ? 'var(--color-success)' : 'var(--color-error)' }}
          >
            {trend.positive ? '↑' : '↓'} {trend.value}
          </span>
        )}
      </div>
      <p className="stat-value">{value}</p>
      <p className="stat-label mt-0.5">{label}</p>
      {sub && (
        <p className="text-xs mt-1 font-mono" style={{ color }}>
          {sub}
        </p>
      )}
    </div>
  );
}

// ── Admin table ───────────────────────────────────────────────────────────────

export function AdminTable({
  headers,
  children,
  empty,
}: {
  headers: string[];
  children: React.ReactNode;
  empty?: boolean;
}) {
  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden">
      <table className="min-w-full divide-y divide-border">
        <thead>
          <tr className="bg-muted/50">
            {headers.map((h) => (
              <th
                key={h}
                className="px-5 py-3 text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wider font-mono"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {empty ? (
            <tr>
              <td colSpan={headers.length} className="px-5 py-10 text-center text-sm text-muted-foreground font-body">
                Ma'lumotlar yo'q
              </td>
            </tr>
          ) : (
            children
          )}
        </tbody>
      </table>
    </div>
  );
}

// Table row cell helper
export function Td({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <td className={`px-5 py-3.5 text-sm text-foreground font-body ${className}`}>
      {children}
    </td>
  );
}

// ── Filter pills helper ───────────────────────────────────────────────────────

export function FilterPills<T extends string>({
  options,
  active,
  onChange,
}: {
  options: { value: T; label: string }[];
  active: T;
  onChange: (v: T) => void;
}) {
  return (
    <div className="filter-pills">
      {options.map((o) => (
        <button
          key={o.value}
          onClick={() => onChange(o.value)}
          className={`filter-pill ${
            active === o.value ? 'filter-pill-active' : 'filter-pill-inactive'
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}