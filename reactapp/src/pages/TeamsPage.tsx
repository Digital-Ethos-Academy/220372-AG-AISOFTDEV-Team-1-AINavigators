import { Users } from 'lucide-react';

export default function TeamsPage() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-blue-600">
        <Users className="h-6 w-6" />
      </div>
      <h1 className="mt-4 text-2xl font-semibold text-slate-900">Team View arriving soon</h1>
      <p className="mt-2 text-sm text-slate-500">
        The dedicated employee utilization view (US012) ships with the V1.2 "Optimizer's Toolkit" milestone. For now, manage staffing directly inside each project.
      </p>
    </div>
  );
}

