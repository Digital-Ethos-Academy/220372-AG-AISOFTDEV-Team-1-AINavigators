import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { CalendarDays, LayoutDashboard, Users } from 'lucide-react';

const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
  `inline-flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-150 ${
    isActive
      ? 'bg-blue-50 text-blue-700 border border-blue-200 shadow-sm'
      : 'text-slate-600 hover:bg-slate-100'
  }`;

export default function AppLayout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/projects" className="flex items-center gap-3 text-xl font-semibold text-blue-600">
            <CalendarDays className="h-7 w-7" />
            StaffAlloc
          </Link>
          <nav className="flex items-center gap-2">
            <NavLink to="/dashboard" className={navLinkClasses}>
              <LayoutDashboard className="h-4 w-4" />
              Portfolio Dashboard
            </NavLink>
            <NavLink to="/projects" className={navLinkClasses}>
              <CalendarDays className="h-4 w-4" />
              Projects
            </NavLink>
            <NavLink to="/teams" className={navLinkClasses}>
              <Users className="h-4 w-4" />
              Teams
            </NavLink>
          </nav>
          <div className="hidden items-center gap-2 sm:flex">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
              PP
            </div>
            <div className="text-sm">
              <p className="font-medium text-slate-800">Priya Patel</p>
              <p className="text-xs text-slate-500">Project Manager</p>
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

