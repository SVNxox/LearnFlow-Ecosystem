'use client';

import { ReactNode, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { getPrimaryRole, UserRole } from '@/types/api';
import { LoadingSpinner, Navbar } from '@/components/ui';

export interface DashboardLayoutProps {
  children: ReactNode;
  allowedRoles?: UserRole[];
}

export default function DashboardLayout({ children, allowedRoles }: DashboardLayoutProps) {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (loading) return;

    if (!user) {
      router.replace('/login');
      return;
    }

    if (allowedRoles && !allowedRoles.includes(getPrimaryRole(user))) {
      router.replace('/dashboard');
    }
  }, [user, loading, router, allowedRoles]);

  if (loading || !user) {
    return <LoadingSpinner fullScreen message="Yuklanmoqda..." />;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>
    </div>
  );
}