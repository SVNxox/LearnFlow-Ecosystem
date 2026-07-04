'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { getPrimaryRole, UserRole } from '@/types/api';
import { LoadingSpinner } from '@/components/ui';

export function RequireRole({
  roles,
  children,
}: {
  roles: UserRole[];
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace('/login');
      return;
    }
    const role = getPrimaryRole(user);
    if (!roles.includes(role)) {
      router.replace(`/dashboard/${role}`);
    }
  }, [user, loading, roles, router]);

  if (loading || !user) return <LoadingSpinner fullScreen message="Yuklanmoqda..." />;

  const role = getPrimaryRole(user);
  if (!roles.includes(role)) return <LoadingSpinner fullScreen />;

  return <>{children}</>;
}
