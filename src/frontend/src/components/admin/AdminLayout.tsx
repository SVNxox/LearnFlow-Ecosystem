'use client';

import { ReactNode } from 'react';
import { RequireRole } from './RequireRole';
import { AdminSidebar } from './AdminSidebar';
import { useAuth } from '@/lib/auth-context';
import { getPrimaryRole } from '@/types/api';

export interface AdminLayoutProps {
  children: ReactNode;
  roles: ('admin' | 'staff')[];
}

function SidebarForCurrentUser() {
  const { user } = useAuth();
  const role = user && getPrimaryRole(user) === 'admin' ? 'admin' : 'staff';
  return <AdminSidebar role={role} />;
}

export default function AdminLayout({ children, roles }: AdminLayoutProps) {
  return (
    <RequireRole roles={roles}>
      <div className="min-h-screen bg-background">
        <SidebarForCurrentUser />
        <main className="ml-60 min-h-screen">
          <div className="p-6">{children}</div>
        </main>
      </div>
    </RequireRole>
  );
}