import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Briefcase, Loader2, Search, Users } from 'lucide-react';

import { createEmployee, fetchEmployees } from '../api/users';
import type { EmployeeListItem, SystemRole, UserCreateInput } from '../types/api';
import { Card, SectionHeader } from '../components/common';
import { useAuth } from '../context/AuthContext';
import AddEmployeeModal from '../components/teams/AddEmployeeModal';

function roleLabel(role: SystemRole) {
  switch (role) {
    case 'Admin':
      return 'Administrator';
    case 'PM':
      return 'Project Manager';
    case 'Employee':
    default:
      return 'Employee';
  }
}

const pillBaseClasses =
  'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold transition';

function StatusPill({ active }: { active: boolean }) {
  return (
    <span
      className={`${pillBaseClasses} ${
        active
          ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
          : 'border-slate-200 bg-slate-100 text-slate-500'
      }`}
    >
      <span className={`h-2 w-2 rounded-full ${active ? 'bg-emerald-500' : 'bg-slate-400'}`} />
      {active ? 'Active' : 'Inactive'}
    </span>
  );
}

function RoleBadge({ role }: { role: SystemRole }) {
  const colors: Record<SystemRole, string> = {
    Admin: 'bg-purple-100 text-purple-700',
    PM: 'bg-amber-100 text-amber-700',
    Employee: 'bg-slate-100 text-slate-600'
  };

  return (
    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-semibold ${colors[role]}`}>
      <Briefcase className="mr-1 h-3.5 w-3.5" />
      {roleLabel(role)}
    </span>
  );
}

function EmployeeCard({ employee }: { employee: EmployeeListItem }) {
  return (
    <div className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-blue-200 hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-lg font-semibold text-slate-900">{employee.full_name}</p>
          <p className="text-sm text-slate-500">{employee.email}</p>
        </div>
        <StatusPill active={employee.is_active} />
      </div>

      <RoleBadge role={employee.system_role} />

      <div className="mt-auto flex items-center justify-between text-sm">
        <span className="text-slate-500">
          Last seen{' '}
          {employee.last_login_at
            ? new Date(employee.last_login_at).toLocaleDateString()
            : 'No recent login'}
        </span>
        <Link
          to={`/teams/${employee.id}`}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-semibold text-blue-600 transition hover:border-blue-300 hover:bg-blue-50"
        >
          View timeline
        </Link>
      </div>
    </div>
  );
}

export default function TeamsPage() {
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<SystemRole | 'All'>('All');
  const [isAddEmployeeOpen, setAddEmployeeOpen] = useState(false);
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: employees = [], isLoading, isError, error } = useQuery({
    queryKey: ['employees', user?.id],
    queryFn: () => {
      if (!user?.id) return Promise.resolve([]);
      return fetchEmployees({
        managerId: user.id
      });
    },
    enabled: !!user?.id,
    staleTime: 60_000
  });

  const createEmployeeMutation = useMutation({
    mutationFn: (payload: UserCreateInput) => createEmployee(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setAddEmployeeOpen(false);
    }
  });

  const uniqueRoles = useMemo<SystemRole[]>(() => {
    const roles = new Set<SystemRole>();
    employees.forEach((employee) => roles.add(employee.system_role));
    return Array.from(roles).sort();
  }, [employees]);

  const filteredEmployees = useMemo(() => {
    const query = search.trim().toLowerCase();
    return employees.filter((employee) => {
      const matchesSearch =
        !query ||
        employee.full_name.toLowerCase().includes(query) ||
        employee.email.toLowerCase().includes(query);
      const matchesRole = roleFilter === 'All' || employee.system_role === roleFilter;
      return matchesSearch && matchesRole;
    });
  }, [employees, roleFilter, search]);

  const activeCount = filteredEmployees.filter((employee) => employee.is_active).length;

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Team Members"
        description="Manage employee profiles, availability, and staffing context."
        action={
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              <Users className="h-3.5 w-3.5" />
              {employees.length} total employees
            </span>
            {user?.system_role === 'PM' && (
              <button
                type="button"
                onClick={() => setAddEmployeeOpen(true)}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
              >
                <Users className="h-4 w-4" />
                Add Employee
              </button>
            )}
          </div>
        }
      />

      <section className="grid gap-4 md:grid-cols-3">
        <Card title="Active Employees" description="Currently available for staffing.">
          <p className="text-3xl font-bold text-slate-900">{activeCount}</p>
          <p className="text-xs text-slate-500">
            {employees.length - activeCount} teammates inactive or onboarding.
          </p>
        </Card>
        <Card title="System Roles" description="Distribution across access levels.">
          <div className="flex flex-wrap gap-2 text-xs font-medium text-slate-600">
            {uniqueRoles.length === 0 && <span>No roles detected.</span>}
            {uniqueRoles.map((role) => (
              <span key={role} className="rounded-full bg-slate-100 px-3 py-1">
                {roleLabel(role)}
              </span>
            ))}
          </div>
        </Card>
        <Card title="Filters" description="Search and segment to find staff quickly.">
          <div className="space-y-3 text-sm text-slate-500">
            <p>Search by name or email.</p>
            <p>Segment by system role to focus on specific cohorts.</p>
            <p>Drill into timelines for cross-project commitments.</p>
          </div>
        </Card>
      </section>

      <Card>
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="relative w-full md:w-72">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search by name or email"
              className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-700 shadow-sm transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 text-sm">
            <button
              type="button"
              onClick={() => setRoleFilter('All')}
              className={`rounded-full px-3 py-1 font-semibold ${
                roleFilter === 'All'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'border border-slate-200 bg-white text-slate-600'
              }`}
            >
              All roles
            </button>
            {uniqueRoles.map((role) => (
              <button
                key={role}
                type="button"
                onClick={() => setRoleFilter(role)}
                className={`rounded-full px-3 py-1 font-semibold ${
                  roleFilter === role
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'border border-slate-200 bg-white text-slate-600'
                }`}
              >
                {roleLabel(role)}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {isLoading && (
        <Card padding="none" className="p-0">
          <div className="flex h-40 items-center justify-center text-sm text-slate-500">
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Loading employees…
          </div>
        </Card>
      )}

      {isError && (
        <Card className="border-red-200 bg-red-50 text-sm text-red-600">
          Failed to load employees: {error instanceof Error ? error.message : 'Unknown error'}
        </Card>
      )}

      {!isLoading && !isError && (
        <>
          {filteredEmployees.length === 0 ? (
            <Card>
              <p className="text-sm text-slate-500">
                No employees match the current filters. Try adjusting your search or role selection.
              </p>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {filteredEmployees.map((employee) => (
                <EmployeeCard key={employee.id} employee={employee} />
              ))}
            </div>
          )}
        </>
      )}

      {user && (
        <AddEmployeeModal
          open={isAddEmployeeOpen}
          submitting={createEmployeeMutation.isPending}
          managerId={user.id}
          error={createEmployeeMutation.error instanceof Error ? createEmployeeMutation.error.message : null}
          onSubmit={(values) => createEmployeeMutation.mutate(values)}
          onClose={() => setAddEmployeeOpen(false)}
        />
      )}
    </div>
  );
}
