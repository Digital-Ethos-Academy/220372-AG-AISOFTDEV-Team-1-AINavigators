import type { ComponentType } from 'react';
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { CalendarDays, LayoutDashboard, Settings, Sparkles, Users } from 'lucide-react';

import type { SystemRole } from '../../types/api';
import { useAuth } from '../../context/AuthContext';

const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
  `inline-flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-150 ${
    isActive
      ? 'bg-blue-50 text-blue-700 border border-blue-200 shadow-sm'
      : 'text-slate-600 hover:bg-slate-100'
  }`;

export default function AppLayout() {
  const location = useLocation();
  const { user: currentUser, logout } = useAuth();

  const navItems: Array<{
    to: string;
    label: string;
    icon: ComponentType<{ className?: string }>;
    roles?: SystemRole[];
  }> = [
    { to: '/dashboard', label: 'Portfolio Dashboard', icon: LayoutDashboard },
    { to: '/projects', label: 'Projects', icon: CalendarDays },
    { to: '/teams', label: 'Teams', icon: Users },
    { to: '/ai/chat', label: 'AI Assistant', icon: Sparkles, roles: ['Admin', 'Director', 'PM'] },
    { to: '/ai/recommendations', label: 'AI Insights', icon: Sparkles, roles: ['Admin', 'Director'] },
    { to: '/settings/roles-lcats', label: 'Settings', icon: Settings, roles: ['Admin', 'PM', 'Director'] }
  ];

  const availableNavItems = navItems.filter(
    (item) => !item.roles || (currentUser && item.roles.includes(currentUser.system_role))
  );

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/projects" className="flex items-center gap-3 text-xl font-semibold text-blue-600">
            <CalendarDays className="h-7 w-7" />
            StaffAlloc
          </Link>
          <nav className="flex items-center gap-2">
            {availableNavItems.map(({ to, label, icon: Icon }) => (
              <NavLink key={to} to={to} className={navLinkClasses}>
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="hidden items-center gap-2 sm:flex">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
              {currentUser?.full_name
                .split(' ')
                .map((part) => part[0])
                .join('')
                .slice(0, 2)
                .toUpperCase()}
            </div>
            <div className="text-sm">
              <p className="font-medium text-slate-800">{currentUser?.full_name}</p>
              <p className="text-xs text-slate-500">
                {currentUser?.system_role}{' '}
                <button
                  type="button"
                  onClick={logout}
                  className="ml-3 text-blue-600 underline-offset-2 hover:underline"
                >
                  Sign out
                </button>
              </p>
            </div>
          </div>
        </div>
      </header>
      <main className="mx-auto min-h-[calc(100vh-64px)] max-w-7xl px-6 py-8">
        <Outlet key={location.pathname} />
      </main>
    </div>
  );
}

