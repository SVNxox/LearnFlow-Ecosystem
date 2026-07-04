'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { getPrimaryRole } from '@/types/api';

/**
 * /dashboard — общий роутер дашборда.
 * Читает роль пользователя и перенаправляет на нужный дашборд:
 *   admin  → /dashboard/admin
 *   staff  → /dashboard/staff
 *   mentor → /dashboard/mentor
 *   student → /dashboard/student
 */
export default function DashboardPage() {
  const router      = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (loading) return;

    if (!user) {
      router.replace('/login');
      return;
    }

    const role = getPrimaryRole(user);
    switch (role) {
      case 'admin':   router.replace('/dashboard/admin');   break;
      case 'staff':   router.replace('/dashboard/staff');   break;
      case 'mentor':  router.replace('/dashboard/mentor');  break;
      case 'student':
      default:        router.replace('/dashboard/student'); break;
    }
  }, [user, loading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
        <p className="text-gray-500">Loading your dashboard…</p>
      </div>
    </div>
  );
}