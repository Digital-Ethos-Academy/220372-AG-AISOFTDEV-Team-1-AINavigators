import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Search } from 'lucide-react';

import { createProject, fetchProjects } from '../api/projects';
import CreateProjectModal from '../components/projects/CreateProjectModal';
import ProjectTable from '../components/projects/ProjectTable';
import type { ProjectCreateInput } from '../types/api';

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const [isModalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState('');

  const { data: projects = [], isLoading, isError, error } = useQuery({
    queryKey: ['projects'],
    queryFn: fetchProjects
  });

  const {
    mutate: handleCreateProject,
    isPending: isCreating,
    error: createError
  } = useMutation({
    mutationFn: (payload: ProjectCreateInput) => createProject(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setModalOpen(false);
    }
  });

  const filteredProjects = projects.filter((project) => {
    if (!search.trim()) return true;
    const query = search.toLowerCase();
    return (
      project.name.toLowerCase().includes(query) ||
      project.code.toLowerCase().includes(query) ||
      (project.client ?? '').toLowerCase().includes(query)
    );
  });

  const createErrorMessage = createError instanceof Error ? createError.message : null;

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
          <p className="mt-1 text-sm text-slate-500">
            Manage project staffing plans, allocations, and health in one place.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <Plus className="h-4 w-4" />
          Create Project
        </button>
      </header>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="relative w-full md:w-80">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by name, code, or client"
            className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-700 shadow-sm transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </div>
        <div className="text-sm text-slate-500">
          Showing <span className="font-semibold text-slate-700">{filteredProjects.length}</span> of{' '}
          <span className="font-semibold text-slate-700">{projects.length}</span> projects
        </div>
      </div>

      {isLoading && (
        <div className="rounded-lg border border-slate-200 bg-white p-12 text-center text-sm text-slate-500">
          Loading projects...
        </div>
      )}

      {isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-600">
          Failed to load projects: {error?.message}
        </div>
      )}

      {!isLoading && !isError && <ProjectTable projects={filteredProjects} />}

      <CreateProjectModal
        open={isModalOpen}
        submitting={isCreating}
        error={createErrorMessage}
        onSubmit={handleCreateProject}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}

