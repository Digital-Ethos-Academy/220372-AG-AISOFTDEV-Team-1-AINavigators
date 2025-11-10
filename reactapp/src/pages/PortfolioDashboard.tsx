import { useMutation, useQuery } from '@tanstack/react-query';
import {
  AlertOctagon,
  ArrowDownToLine,
  BarChart3,
  Loader2,
  PieChart,
  Users
} from 'lucide-react';

import { exportPortfolioToExcel, fetchPortfolioDashboard } from '../api/reports';
import { Card, KpiTile, SectionHeader } from '../components/common';
import { saveBlobAsFile } from '../utils/download';
import { useAuth } from '../context/AuthContext';
import ManagerAllocationGrid from '../components/dashboard/ManagerAllocationGrid';

export default function PortfolioDashboard() {
  const { user } = useAuth();
  
  const portfolioQuery = useQuery({
    queryKey: ['portfolio-dashboard', user?.id],
    queryFn: () => {
      if (!user?.id) return Promise.reject(new Error('User not authenticated'));
      return fetchPortfolioDashboard(user.id);
    },
    enabled: !!user?.id,
    staleTime: 60_000
  });

  const exportMutation = useMutation({
    mutationFn: () => {
      if (!user?.id) return Promise.reject(new Error('User not authenticated'));
      return exportPortfolioToExcel(user.id);
    },
    onSuccess: (blob) => {
      const timestamp = new Date().toISOString().slice(0, 10);
      saveBlobAsFile(blob, `staffalloc-portfolio-${timestamp}.xlsx`);
    }
  });

  const overAllocated = portfolioQuery.data?.over_allocated_employees ?? [];
  const benchEmployees = portfolioQuery.data?.bench_employees ?? [];
  const utilizationPct = portfolioQuery.data?.overall_utilization_pct ?? 0;

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Dashboard"
        description="Staffing Overview"
        action={
          <button
            type="button"
            onClick={() => exportMutation.mutate()}
            disabled={exportMutation.isPending}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:text-blue-600 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {exportMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ArrowDownToLine className="h-4 w-4" />
            )}
            Export to Excel
          </button>
        }
      />

      {portfolioQuery.isLoading && (
        <Card padding="none" className="p-0">
          <div className="flex h-64 items-center justify-center text-sm text-slate-500">
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Loading portfolio metrics…
          </div>
        </Card>
      )}

      {portfolioQuery.isError && (
        <Card className="border-red-200 bg-red-50">
          <div className="flex items-center gap-3 text-sm text-red-600">
            <AlertOctagon className="h-5 w-5" />
            <span>Failed to load portfolio dashboard: {portfolioQuery.error instanceof Error ? portfolioQuery.error.message : 'Unknown error'}</span>
          </div>
        </Card>
      )}

      {portfolioQuery.data && !portfolioQuery.isError && (
        <>
          <section className="grid gap-4 md:grid-cols-3">
            <KpiTile
              label="Active Projects"
              value={portfolioQuery.data.total_projects}
              subLabel="Across portfolio"
              icon={<Users className="h-5 w-5 text-blue-500" />}
            />
            <KpiTile
              label="Total Headcount"
              value={portfolioQuery.data.total_employees}
              subLabel="Tracked employees"
              icon={<BarChart3 className="h-5 w-5 text-emerald-500" />}
            />
            <KpiTile
              label="Utilization"
              value={`${utilizationPct.toFixed(1)}%`}
              subLabel="Overall FTE"
              icon={<PieChart className="h-5 w-5 text-purple-500" />}
              trend={{
                direction: utilizationPct >= 80 ? 'up' : 'flat',
                label:
                  utilizationPct >= 80
                    ? 'Healthy portfolio utilization'
                    : 'Below target – investigate bench capacity',
                tone: utilizationPct >= 80 ? 'positive' : 'neutral'
              }}
            />
          </section>

          <section className="mt-6">
            {user?.id && <ManagerAllocationGrid managerId={user.id} />}
          </section>

          <section className="grid gap-6 lg:grid-cols-2">
            <Card
              title="Over-allocated"
              description="Employees above 100% FTE across all projects."
            >
              {overAllocated.length === 0 ? (
                <p className="text-sm text-slate-500">No over-allocations detected.</p>
              ) : (
                <ul className="space-y-3 text-sm text-slate-600">
                  {overAllocated.map((employee) => (
                    <li key={employee.user_id} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                      <div className="flex items-center justify-between">
                        <p className="font-semibold text-slate-800">{employee.full_name}</p>
                        <span className="text-xs font-semibold text-red-600">
                          {employee.fte_percentage.toFixed(1)}% FTE
                        </span>
                      </div>
                      {employee.projects && employee.projects.length > 0 && (
                        <ul className="mt-2 space-y-1 text-xs text-slate-500">
                          {employee.projects.map((project) => (
                            <li key={project.project_id}>
                              {project.project_name} · {project.allocated_hours} hrs
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card
              title="Bench Spotlight"
              description="Under 25% FTE availability to redeploy."
            >
              {benchEmployees.length === 0 ? (
                <p className="text-sm text-slate-500">No bench capacity currently detected.</p>
              ) : (
                <ul className="space-y-2 text-sm text-slate-600">
                  {benchEmployees.map((employee) => (
                    <li key={employee.user_id} className="flex items-center justify-between rounded-lg border border-slate-200 p-2">
                      <span>{employee.full_name}</span>
                      <span className="text-xs font-semibold text-emerald-600">
                        {employee.fte_percentage.toFixed(1)}% FTE
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </section>
        </>
      )}
    </div>
  );
}
