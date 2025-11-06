import { Link } from 'react-router-dom';
import { CalendarIcon, ChevronRight, MoreHorizontal } from 'lucide-react';
import type { ProjectListItem } from '../../types/api';

function StatusBadge({ status }: { status: ProjectListItem['status'] }) {
  const colors: Record<ProjectListItem['status'], string> = {
    Active: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    Planning: 'bg-amber-50 text-amber-700 ring-amber-200',
    'On Hold': 'bg-slate-100 text-slate-600 ring-slate-200',
    Closed: 'bg-blue-50 text-blue-700 ring-blue-200'
  } as const;

  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${colors[status]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}

interface ProjectTableProps {
  projects: ProjectListItem[];
}

export default function ProjectTable({ projects }: ProjectTableProps) {
  if (projects.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white py-16 text-center">
        <p className="text-lg font-semibold text-slate-700">No projects yet</p>
        <p className="mt-2 text-sm text-slate-500">Create your first project to begin allocating your team.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Project
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Client
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Start Date
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Sprints
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Status
            </th>
            <th className="relative px-6 py-3">
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {projects.map((project) => (
            <tr key={project.id} className="transition hover:bg-slate-50">
              <td className="px-6 py-4">
                <div className="flex flex-col">
                  <Link to={`/projects/${project.id}`} className="font-medium text-blue-600 hover:underline">
                    {project.name}
                  </Link>
                  <span className="text-xs text-slate-500">{project.code}</span>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-slate-700">{project.client ?? '—'}</td>
              <td className="px-6 py-4 text-sm text-slate-700">
                <span className="inline-flex items-center gap-2">
                  <CalendarIcon className="h-4 w-4 text-slate-400" />
                  {new Date(project.start_date).toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                  })}
                </span>
              </td>
              <td className="px-6 py-4 text-sm font-medium text-slate-700">{project.sprints}</td>
              <td className="px-6 py-4 text-sm">
                <StatusBadge status={project.status} />
              </td>
              <td className="px-6 py-4 text-right text-sm">
                <Link
                  to={`/projects/${project.id}`}
                  className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-600 transition hover:border-blue-200 hover:text-blue-600"
                >
                  View
                  <ChevronRight className="h-4 w-4" />
                </Link>
                <button
                  type="button"
                  className="ml-2 inline-flex items-center rounded-md border border-transparent px-2 py-1 text-slate-400 hover:text-slate-600"
                  aria-label={`More options for ${project.name}`}
                >
                  <MoreHorizontal className="h-5 w-5" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

