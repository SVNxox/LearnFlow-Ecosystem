'use client';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import {GraduationCap, Bell, LogOut, Settings, User, BookOpen, Award, ChevronRight} from 'lucide-react';
import {useEffect, useRef, useState} from 'react';

function UserDropdown() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
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
      {/* Trigger Button */}
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

      {/* Dropdown Menu */}
      {menuOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />

          {/* Menu */}
          <div className="absolute right-0 top-11 z-50 w-52 bg-card border border-border rounded-xl shadow-xl overflow-hidden">
            {/* User Info */}
            <div className="px-4 py-3 border-b border-border">
              <p className="text-sm font-semibold text-foreground font-body">
                {userName}
              </p>
              <p className="text-xs text-muted-foreground font-mono">{user.email}</p>
            </div>

            {/* Menu Items */}
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

export function Navbar() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 glass border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-full flex items-center gap-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 mr-4">
          <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
            <GraduationCap size={14} className="text-primary-foreground" />
          </div>
          <span className="text-base font-bold text-foreground font-heading tracking-tight hidden sm:block">
            LearnFlow
          </span>
        </Link>

        {/* Nav links */}
        {user && (
          <nav className="flex items-center gap-1">
            <Link href="/courses" className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground rounded-lg hover:bg-muted transition-colors font-body">
              Курсы
            </Link>
            <Link href="/my-courses" className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground rounded-lg hover:bg-muted transition-colors font-body">
              Мои курсы
            </Link>
          </nav>
        )}

        {/*<div className="ml-auto flex items-center gap-2">*/}
        {/*  {user ? (*/}
        {/*    <>*/}
        {/*      /!* Notification bell *!/*/}
        {/*      <button className="relative w-9 h-9 rounded-xl border border-border bg-card flex items-center justify-center hover:border-primary/40 transition-colors">*/}
        {/*        <Bell size={15} className="text-muted-foreground" />*/}
        {/*        <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-accent" />*/}
        {/*      </button>*/}

        {/*      /!* User menu *!/*/}
        {/*      <div className="relative">*/}
        {/*        <button*/}
        {/*          onClick={() => setMenuOpen(!menuOpen)}*/}
        {/*          className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-border bg-card hover:border-primary/40 transition-colors"*/}
        {/*        >*/}
        {/*          <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center">*/}
        {/*            <User size={11} className="text-primary" />*/}
        {/*          </div>*/}
        {/*          <span className="text-sm text-foreground font-body hidden sm:block">*/}
        {/*            {user.info?.first_name ?? user.email.split('@')[0]}*/}
        {/*          </span>*/}
        {/*        </button>*/}

        {/*        {menuOpen && (*/}
        {/*          <>*/}
        {/*            <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />*/}
        {/*            <div className="absolute right-0 top-11 z-50 w-52 bg-card border border-border rounded-xl shadow-xl overflow-hidden">*/}
        {/*              <div className="px-4 py-3 border-b border-border">*/}
        {/*                <p className="text-sm font-semibold text-foreground font-body">*/}
        {/*                  {user.info?.first_name} {user.info?.last_name}*/}
        {/*                </p>*/}
        {/*                <p className="text-xs text-muted-foreground font-mono">{user.email}</p>*/}
        {/*              </div>*/}
        {/*              <nav className="p-1.5">*/}
        {/*                {[*/}
        {/*                  { href: '/dashboard', label: 'Дашборд', icon: BookOpen },*/}
        {/*                  { href: '/certificates', label: 'Сертификаты', icon: Award },*/}
        {/*                  { href: '/profile', label: 'Настройки', icon: Settings },*/}
        {/*                ].map((item) => (*/}
        {/*                  <Link*/}
        {/*                    key={item.href}*/}
        {/*                    href={item.href}*/}
        {/*                    onClick={() => setMenuOpen(false)}*/}
        {/*                    className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-colors font-body"*/}
        {/*                  >*/}
        {/*                    <item.icon size={14} />*/}
        {/*                    {item.label}*/}
        {/*                  </Link>*/}
        {/*                ))}*/}
        {/*                <button*/}
        {/*                  onClick={() => { logout(); setMenuOpen(false); }}*/}
        {/*                  className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-destructive hover:bg-destructive/10 transition-colors font-body"*/}
        {/*                >*/}
        {/*                  <LogOut size={14} />*/}
        {/*                  Выйти*/}
        {/*                </button>*/}
        {/*              </nav>*/}
        {/*            </div>*/}
        {/*          </>*/}
        {/*        )}*/}
        {/*      </div>*/}
        {/*    </>*/}
        {/*  ) : (*/}
        {/*    <>*/}
        {/*      <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground transition-colors font-body">*/}
        {/*        Войти*/}
        {/*      </Link>*/}
        {/*      <Link href="/register" className="btn-primary text-sm py-2 px-4">*/}
        {/*        Регистрация*/}
        {/*      </Link>*/}
        {/*    </>*/}
        {/*  )}*/}
        {/*</div>*/}

        {/* CTA buttons / User Menu */}
        <div className="ml-auto flex items-center gap-2">
          {user ? (
            // ✅ Авторизованный пользователь — показываем dropdown
            <UserDropdown />
          ) : (
            // ✅ Неавторизованный пользователь — показываем кнопки
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
  );
}