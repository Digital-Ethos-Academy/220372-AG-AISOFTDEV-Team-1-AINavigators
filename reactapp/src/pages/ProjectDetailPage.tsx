import { useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Navigate, useParams } from 'react-router-dom';
import { AlertTriangle, ArrowDownToLine, CalendarDays, LayoutGrid, Loader2, PencilLine, UsersRound } from 'lucide-react';

import { createAllocation, createAssignment, deleteAssignment, distributeAssignmentAllocations, updateAllocation, updateAssignment } from '../api/assignments';
import { fetchLCATs, fetchRoles } from '../api/admin';
import { exportProjectToExcel } from '../api/reports';
import { updateProject } from '../api/projects';
import { useMonthlyOverrideMutations, useProjectDetail } from '../hooks/useProjectDetail';
import AllocationGrid from '../components/projects/AllocationGrid';
import AddAssignmentModal from '../components/projects/AddAssignmentModal';
import EditAssignmentModal from '../components/projects/EditAssignmentModal';
import DistributeAssignmentModal from '../components/projects/DistributeAssignmentModal';
import EditProjectModal from '../components/projects/EditProjectModal';
import MonthlyHoursOverrideModal from '../components/projects/MonthlyHoursOverrideModal';
import { fetchEmployees, fetchUserAllocationSummary } from '../api/users';
import type {
  AssignmentDistributionInput,
  MonthlyHourOverride,
  ProjectAssignment,
  ProjectAssignmentCreateInput,
  ProjectUpdateInput
} from '../types/api';
import ProjectHealthPanel from '../components/projects/ProjectHealthPanel';
import ProjectAIInsights from '../components/projects/ProjectAIInsights';
import { SectionHeader } from '../components/common';
import { saveBlobAsFile } from '../utils/download';
import { useAuth } from '../context/AuthContext';

type ViewMode = 'month' | 'sprint';

interface OverrideModalState {
  open: boolean;
  year: number;
  month: number;
  initialHours: number;
  baselineHours: number;
  override?: MonthlyHourOverride;
}

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = Number(params.projectId);

  if (Number.isNaN(projectId)) {
    return <Navigate to="/projects" replace />;
  }

  const { user } = useAuth();

  const queryClient = useQueryClient();
  const { data: project, isLoading, isError, error } = useProjectDetail(projectId);
  const rolesQuery = useQuery({
    queryKey: ['roles', user?.id ?? 'all'],
    queryFn: () =>
      fetchRoles({ ownerId: user?.system_role === 'PM' ? user.id : undefined, includeGlobal: true })
  });
  const lcatsQuery = useQuery({
    queryKey: ['lcats', user?.id ?? 'all'],
    queryFn: () =>
      fetchLCATs({ ownerId: user?.system_role === 'PM' ? user.id : undefined, includeGlobal: true })
  });
  const employeesQuery = useQuery({
    queryKey: ['employees', user?.id ?? 'all'],
    queryFn: () =>
      fetchEmployees({
        managerId: user?.system_role === 'PM' ? user.id : undefined,
        includeGlobal: true
      })
  });

  const { create: createOverrideMutation, update: updateOverrideMutation, remove: deleteOverrideMutation } =
    useMonthlyOverrideMutations(projectId);

  const [viewMode, setViewMode] = useState<ViewMode>('month');
  const [isAddAssignmentOpen, setAddAssignmentOpen] = useState(false);
  const [isEditProjectOpen, setEditProjectOpen] = useState(false);
  const [overrideModal, setOverrideModal] = useState<OverrideModalState | null>(null);
  const [editingAssignment, setEditingAssignment] = useState<ProjectAssignment | null>(null);
  const [distributingAssignment, setDistributingAssignment] = useState<ProjectAssignment | null>(null);
  const [userTotals, setUserTotals] = useState<Record<string, number>>({});
  const [loadingSummaries, setLoadingSummaries] = useState(false);
  const [projectModalError, setProjectModalError] = useState<string | null>(null);
  const [assignmentModalError, setAssignmentModalError] = useState<string | null>(null);
  const [distributionModalError, setDistributionModalError] = useState<string | null>(null);

  const addAssignmentMutation = useMutation({
    mutationFn: (payload: ProjectAssignmentCreateInput) => createAssignment(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
    }
  });

  const createAllocationMutation = useMutation({
    mutationFn: createAllocation,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['project', projectId] })
  });

  const updateAllocationMutation = useMutation({
    mutationFn: ({ allocationId, hours }: { allocationId: number; hours: number }) =>
      updateAllocation(allocationId, hours),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['project', projectId] })
  });

  const exportMutation = useMutation({
    mutationFn: () => exportProjectToExcel(projectId),
    onSuccess: (blob) => {
      const label = project?.code ?? `project-${projectId}`;
      const timestamp = new Date().toISOString().slice(0, 10);
      saveBlobAsFile(blob, `staffalloc-${label}-${timestamp}.xlsx`);
    }
  });

  const updateProjectMutation = useMutation({
    mutationFn: (payload: ProjectUpdateInput) => updateProject(projectId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      setEditProjectOpen(false);
      setProjectModalError(null);
    },
    onError: (mutationError: unknown) => {
      setProjectModalError(mutationError instanceof Error ? mutationError.message : 'Unable to update project.');
    }
  });

  const updateAssignmentMutation = useMutation({
    mutationFn: ({ assignmentId, payload }: { assignmentId: number; payload: ProjectAssignmentUpdateInput }) =>
      updateAssignment(assignmentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      setEditingAssignment(null);
      setAssignmentModalError(null);
    },
    onError: (mutationError: unknown) => {
      setAssignmentModalError(mutationError instanceof Error ? mutationError.message : 'Unable to update assignment.');
    }
  });

  const distributeMutation = useMutation({
    mutationFn: ({ assignmentId, payload }: { assignmentId: number; payload: AssignmentDistributionInput }) =>
      distributeAssignmentAllocations(assignmentId, payload),
    onSuccess: (_allocations, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      setDistributionModalError(null);
      if (variables && distributingAssignment) {
        refreshUserTotals(distributingAssignment.user_id);
      }
      setDistributingAssignment(null);
    },
    onError: (mutationError: unknown) => {
      setDistributionModalError(
        mutationError instanceof Error ? mutationError.message : 'Unable to distribute hours. Try again.'
      );
    }
  });

  const removeAssignmentMutation = useMutation({
    mutationFn: (assignmentId: number) => deleteAssignment(assignmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
    }
  });

  useEffect(() => {
    if (!project) return;

    let cancelled = false;
    const loadSummaries = async () => {
      setLoadingSummaries(true);
      try {
        const uniqueUserIds = Array.from(new Set(project.assignments.map((assignment) => assignment.user_id)));
        const results = await Promise.all(
          uniqueUserIds.map(async (userId) => {
            const summary = await fetchUserAllocationSummary(userId);
            return { userId, summary };
          })
        );

        if (cancelled) return;

        const totals: Record<string, number> = {};
        results.forEach(({ userId, summary }) => {
          summary.forEach((item) => {
            totals[`${userId}-${item.year}-${item.month}`] = item.total_hours;
          });
        });
        setUserTotals(totals);
      } catch (loadError) {
        console.error('Failed to load allocation summaries', loadError);
      } finally {
        if (!cancelled) {
          setLoadingSummaries(false);
        }
      }
    };

    loadSummaries();

    return () => {
      cancelled = true;
    };
  }, [project]);

  const refreshUserTotals = async (userId: number) => {
    try {
      const summary = await fetchUserAllocationSummary(userId);
      setUserTotals((prev) => {
        const next = { ...prev };
        Object.keys(next).forEach((key) => {
          if (key.startsWith(`${userId}-`)) {
            delete next[key];
          }
        });
        summary.forEach((item) => {
          next[`${userId}-${item.year}-${item.month}`] = item.total_hours;
        });
        return next;
      });
    } catch (summaryError) {
      console.error('Failed to refresh allocation summary', summaryError);
    }
  };

  const handleAssignmentSubmit = async (payload: ProjectAssignmentCreateInput) => {
    await addAssignmentMutation.mutateAsync(payload);
    setAddAssignmentOpen(false);
    try {
      const summary = await fetchUserAllocationSummary(payload.user_id);
      setUserTotals((prev) => {
        const next = { ...prev };
        Object.keys(next).forEach((key) => {
          if (key.startsWith(`${payload.user_id}-`)) {
            delete next[key];
          }
        });
        summary.forEach((item) => {
          next[`${payload.user_id}-${item.year}-${item.month}`] = item.total_hours;
        });
        return next;
      });
    } catch (summaryError) {
      console.error('Failed to refresh allocation summary', summaryError);
    }
  };

  const handleChangeHours = async ({
    assignmentId,
    userId,
    allocationId,
    year,
    month,
    hours
  }: {
    assignmentId: number;
    userId: number;
    allocationId?: number;
    year: number;
    month: number;
    hours: number;
  }) => {
    if (allocationId) {
      await updateAllocationMutation.mutateAsync({ allocationId, hours });
    } else if (hours > 0) {
      await createAllocationMutation.mutateAsync({
        project_assignment_id: assignmentId,
        year,
        month,
        allocated_hours: hours
      });
    }

    try {
      await refreshUserTotals(userId);
    } catch (summaryError) {
      console.error('Failed to refresh allocation summary', summaryError);
    }
  };

  const handleOverrideSubmit = async (hours: number) => {
    if (!project || !overrideModal) return;
    const { year, month, override } = overrideModal;
    if (override) {
      await updateOverrideMutation.mutateAsync({ overrideId: override.id, overridden_hours: hours });
    } else {
      await createOverrideMutation.mutateAsync({ project_id: project.id, year, month, overridden_hours: hours });
    }
    setOverrideModal(null);
  };

  const handleOverrideDelete = async () => {
    if (!overrideModal?.override) return;
    await deleteOverrideMutation.mutateAsync(overrideModal.override.id);
    setOverrideModal(null);
  };

  const handleRequestOverride = ({
    year,
    month,
    currentHours,
    baselineHours,
    override
  }: {
    year: number;
    month: number;
    currentHours: number;
    baselineHours: number;
    override?: MonthlyHourOverride;
  }) => {
    setOverrideModal({
      open: true,
      year,
      month,
      initialHours: currentHours,
      baselineHours,
      override
    });
  };

  const handleProjectUpdate = async (values: ProjectUpdateInput) => {
    setProjectModalError(null);
    await updateProjectMutation.mutateAsync(values);
  };

  const handleAssignmentUpdate = async (values: ProjectAssignmentUpdateInput) => {
    if (!editingAssignment) return;
    setAssignmentModalError(null);
    await updateAssignmentMutation.mutateAsync({ assignmentId: editingAssignment.id, payload: values });
    await refreshUserTotals(editingAssignment.user_id);
  };

  const handleDistributeSubmit = async (values: AssignmentDistributionInput) => {
    if (!distributingAssignment) return;
    setDistributionModalError(null);
    await distributeMutation.mutateAsync({ assignmentId: distributingAssignment.id, payload: values });
  };

  const handleRemoveAssignment = async (assignment: ProjectAssignment) => {
    if (!window.confirm(`Remove ${assignment.user.full_name} from this project? This will delete all their allocations.`)) {
      return;
    }
    await removeAssignmentMutation.mutateAsync(assignment.id);
  };

  const timelineDefaults = useMemo(() => {
    if (!project) {
      const today = new Date();
      return {
        start: { year: today.getFullYear(), month: today.getMonth() + 1 },
        end: { year: today.getFullYear(), month: today.getMonth() + 1 }
      };
    }

    let earliest = new Date(project.start_date);
    let latest = new Date(project.start_date);

    project.assignments.forEach((assignment) => {
      assignment.allocations?.forEach((allocation) => {
        const current = new Date(allocation.year, allocation.month - 1, 1);
        if (current < earliest) earliest = current;
        if (current > latest) latest = current;
      });
    });

    const estimatedEnd = new Date(project.start_date);
    estimatedEnd.setDate(estimatedEnd.getDate() + project.sprints * 14);
    if (latest < estimatedEnd) {
      latest = estimatedEnd;
    }

    return {
      start: { year: earliest.getFullYear(), month: earliest.getMonth() + 1 },
      end: { year: latest.getFullYear(), month: latest.getMonth() + 1 }
    };
  }, [project]);

  const fundedVsAllocated = useMemo(() => {
    if (!project) return { funded: 0, allocated: 0 };
    let funded = 0;
    let allocated = 0;
    project.assignments.forEach((assignment) => {
      funded += assignment.funded_hours;
      assignment.allocations?.forEach((allocation) => {
        allocated += allocation.allocated_hours;
      });
    });
    return { funded, allocated };
  }, [project]);

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center rounded-xl border border-slate-200 bg-white text-sm text-slate-500">
        Loading project...
      </div>
    );
  }

  if (isError || !project) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-600">
        Failed to load project: {error?.message ?? 'Unknown error'}
      </div>
    );
  }

  if (user?.system_role === 'PM' && project.manager_id !== user.id) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-amber-700">
        You do not have access to this project. Ask the portfolio admin to assign you as the project manager.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="inline-flex items-center gap-3 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              <CalendarDays className="h-4 w-4" />
              {project.code} · {project.status}
            </div>
            <h1 className="mt-3 text-3xl font-bold text-slate-900">{project.name}</h1>
            <p className="mt-2 text-sm text-slate-500">
              {project.client ? `${project.client} · ` : ''}Starts {new Date(project.start_date).toLocaleDateString()}
            </p>
          </div>
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
              <UsersRound className="h-5 w-5 text-slate-500" />
              <div>
                <p className="text-xs text-slate-500">Assignments</p>
                <p className="font-semibold text-slate-700">{project.assignments.length}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
              <LayoutGrid className="h-5 w-5 text-slate-500" />
              <div>
                <p className="text-xs text-slate-500">Funded vs Allocated</p>
                <p className="font-semibold text-slate-700">
                  {fundedVsAllocated.allocated} / {fundedVsAllocated.funded} hrs
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              <div>
                <p className="text-xs text-slate-500">Overrides</p>
                <p className="font-semibold text-slate-700">{project.monthly_hour_overrides.length}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => setEditProjectOpen(true)}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:text-blue-600"
            >
              <PencilLine className="h-4 w-4" /> Edit Project
            </button>
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
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
              onClick={() => setAddAssignmentOpen(true)}
            >
              Add Team Member
            </button>
          </div>
        </div>

        {exportMutation.isError && (
          <p className="mt-3 text-xs font-semibold text-red-600">
            Unable to export project data. Please try again shortly.
          </p>
        )}
      </header>

      <section className="space-y-4">
        <SectionHeader
          title="Project Health"
          description="Track funded budget, allocated hours, and burn-down progress."
        />
        <ProjectHealthPanel projectId={project.id} />
      </section>

      <section className="space-y-4">
        <SectionHeader
          title="AI Assist"
          description="Use AI to recommend staffing, detect conflicts, and balance workloads for this project."
        />
        <ProjectAIInsights
          projectId={project.id}
          roles={rolesQuery.data ?? []}
          lcats={lcatsQuery.data ?? []}
        />
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-800">Allocation Grid</h2>
          <div className="flex items-center gap-4">
            {loadingSummaries && (
              <span className="inline-flex items-center gap-2 text-xs text-slate-500">
                <Loader2 className="h-3.5 w-3.5 animate-spin" /> Checking cross-project allocations...
              </span>
            )}
            <div className="flex gap-2 rounded-lg border border-slate-200 bg-slate-50 p-1 text-sm">
              <button
                type="button"
                className={`rounded-md px-3 py-1.5 font-semibold transition ${
                  viewMode === 'month' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600'
                }`}
                onClick={() => setViewMode('month')}
              >
                Monthly View
              </button>
              <button
                type="button"
                className={`rounded-md px-3 py-1.5 font-semibold transition ${
                  viewMode === 'sprint' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600'
                }`}
                onClick={() => setViewMode('sprint')}
              >
                Sprint View
              </button>
            </div>
          </div>
        </div>
        <AllocationGrid
          project={project}
          viewMode={viewMode}
          onChangeHours={handleChangeHours}
          onRequestOverride={handleRequestOverride}
          userTotals={userTotals}
          onEditAssignment={(assignment) => {
            setAssignmentModalError(null);
            setEditingAssignment(assignment);
          }}
          onDistributeHours={(assignment) => {
            setDistributionModalError(null);
            setDistributingAssignment(assignment);
          }}
          onRemoveAssignment={handleRemoveAssignment}
        />
      </section>

      <AddAssignmentModal
        open={isAddAssignmentOpen}
        submitting={addAssignmentMutation.isPending}
        projectId={project.id}
        employees={employeesQuery.data ?? []}
        roles={rolesQuery.data ?? []}
        lcats={lcatsQuery.data ?? []}
        onClose={() => setAddAssignmentOpen(false)}
        onSubmit={handleAssignmentSubmit}
        error={addAssignmentMutation.error instanceof Error ? addAssignmentMutation.error.message : null}
      />

      <EditProjectModal
        open={isEditProjectOpen}
        submitting={updateProjectMutation.isPending}
        project={project}
        error={projectModalError}
        onSubmit={handleProjectUpdate}
        onClose={() => {
          setEditProjectOpen(false);
          setProjectModalError(null);
        }}
      />

      <EditAssignmentModal
        open={editingAssignment !== null}
        submitting={updateAssignmentMutation.isPending}
        assignment={editingAssignment}
        roles={rolesQuery.data ?? []}
        lcats={lcatsQuery.data ?? []}
        error={assignmentModalError}
        onSubmit={handleAssignmentUpdate}
        onClose={() => {
          setEditingAssignment(null);
          setAssignmentModalError(null);
        }}
      />

      <DistributeAssignmentModal
        open={distributingAssignment !== null}
        submitting={distributeMutation.isPending}
        assignment={distributingAssignment}
        defaultStart={timelineDefaults.start}
        defaultEnd={timelineDefaults.end}
        error={distributionModalError}
        onSubmit={handleDistributeSubmit}
        onClose={() => {
          setDistributingAssignment(null);
          setDistributionModalError(null);
        }}
      />

      {overrideModal && (
        <MonthlyHoursOverrideModal
          open={overrideModal.open}
          year={overrideModal.year}
          month={overrideModal.month}
          initialHours={overrideModal.initialHours}
          baselineHours={overrideModal.baselineHours}
          overrideId={overrideModal.override?.id}
          submitting={createOverrideMutation.isPending || updateOverrideMutation.isPending}
          deleting={deleteOverrideMutation.isPending}
          onClose={() => setOverrideModal(null)}
          onSubmit={handleOverrideSubmit}
          onDelete={overrideModal.override ? handleOverrideDelete : undefined}
        />
      )}
    </div>
  );
}

