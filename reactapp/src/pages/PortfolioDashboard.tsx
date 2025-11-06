import { useQuery } from '@tanstack/react-query';
import { BarChart3, FileSpreadsheet, Users } from 'lucide-react';

import { fetchProjects } from '../api/projects';

export default function PortfolioDashboard() {
  const { data: projects = [] } = useQuery({ queryKey: ['projects'], queryFn: fetchProjects });

  const totalSprints = projects.reduce((sum, project) => sum + project.sprints, 0);

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">Portfolio Dashboard (Coming in V1.1)</h1>
        <p className="mt-2 text-sm text-slate-500">
          This prototype surfaces a few key metrics while we focus engineering effort on the V1.0 MVP experience.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <Users className="h-5 w-5 text-blue-500" />
            <h2 className="text-sm font-semibold text-slate-600">Active Projects</h2>
          </div>
          <p className="mt-3 text-3xl font-bold text-slate-900">{projects.length}</p>
          <p className="mt-1 text-xs text-slate-500">Aligned with US011 (portfolio roll-up)</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <BarChart3 className="h-5 w-5 text-emerald-500" />
            <h2 className="text-sm font-semibold text-slate-600">Total Planned Sprints</h2>
          </div>
          <p className="mt-3 text-3xl font-bold text-slate-900">{totalSprints}</p>
          <p className="mt-1 text-xs text-slate-500">Tracks multi-project cadence</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <FileSpreadsheet className="h-5 w-5 text-amber-500" />
            <h2 className="text-sm font-semibold text-slate-600">Excel Export</h2>
          </div>
          <p className="mt-3 text-sm text-slate-600">
            Export to Excel (US016) will land once the dashboards are fully in place. Until then, continue sharing via this UI.
          </p>
        </div>
      </section>
    </div>
  );
}

