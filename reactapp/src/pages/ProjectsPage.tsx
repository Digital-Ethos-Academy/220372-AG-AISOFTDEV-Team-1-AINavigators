import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Search } from 'lucide-react';

import { createProject, fetchProjects, importProjectsFromExcel } from '../api/projects';
import ImportProjectsModal from '../components/projects/ImportProjectsModal';
import CreateProjectModal from '../components/projects/CreateProjectModal';
import ProjectTable from '../components/projects/ProjectTable';
import { useAuth } from '../context/AuthContext';
import type { ProjectCreateInput } from '../types/api';

export default function ProjectsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [isModalOpen, setModalOpen] = useState(false);
  const [isImportOpen, setImportOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [importError, setImportError] = useState<string | null>(null);
  const [importSummary, setImportSummary] = useState<{ created: number; skipped: number } | null>(null);
  const [isImporting, setImporting] = useState(false);

  const { data: projects = [], isLoading, isError, error } = useQuery({
    queryKey: ['projects', user?.id],
    queryFn: () => {
      if (!user?.id) return Promise.resolve([]);
      return fetchProjects({ managerId: user.id });
    },
    enabled: !!user?.id
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

  const visibleProjects = filteredProjects;

  const createErrorMessage = createError instanceof Error ? createError.message : null;

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
          <p className="mt-1 text-sm text-slate-500">
            Manage project staffing plans, allocations, and health in one place.
            {user?.system_role === 'PM' && ' Showing projects assigned to you.'}
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
        <button
          type="button"
          onClick={() => {
            setImportError(null);
            setImportSummary(null);
            setImportOpen(true);
          }}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:text-blue-600"
        >
          Import from Excel
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

      {!isLoading && !isError && (
        <>
          {user?.system_role === 'PM' && visibleProjects.length === 0 ? (
            <div className="rounded-lg border border-dashed border-slate-300 bg-white py-16 text-center text-sm text-slate-500">
              You are not assigned to any projects yet. Ask your administrator to add you as the project manager.
            </div>
          ) : (
            <ProjectTable projects={visibleProjects} />
          )}
        </>
      )}

      <CreateProjectModal
        open={isModalOpen}
        submitting={isCreating}
        error={createErrorMessage}
        onSubmit={(values) =>
          handleCreateProject({
            ...values,
            manager_id: user?.system_role === 'PM' ? user.id : values.manager_id
          })
        }
        onClose={() => setModalOpen(false)}
      />

      <ImportProjectsModal
        open={isImportOpen}
        submitting={isImporting}
        error={importError}
        onSubmit={async (file) => {
          try {
            setImportError(null);
            setImportSummary(null);
            setImporting(true);
            const response = await importProjectsFromExcel(file, user?.system_role === 'PM' ? user.id : undefined);
            setImportSummary({ created: response.created_projects.length, skipped: response.skipped_codes.length });
            setImportOpen(false);
            await queryClient.invalidateQueries({ queryKey: ['projects'] });
          } catch (uploadError) {
            if (uploadError instanceof Error) {
              setImportError(uploadError.message);
            } else {
              setImportError('Unable to import projects. Please try again.');
            }
          }
          finally {
            setImporting(false);
          }
        }}
        onClose={() => {
          setImportOpen(false);
          setImportError(null);
          setImporting(false);
        }}
      />

      {importSummary && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          Imported {importSummary.created} project{importSummary.created === 1 ? '' : 's'}. {importSummary.skipped > 0 && (
            <span>Skipped {importSummary.skipped} existing code{importSummary.skipped === 1 ? '' : 's'}.</span>
          )}
        </div>
      )}
    </div>
  );
}

