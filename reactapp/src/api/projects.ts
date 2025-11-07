import api from './client';
import type {
  MonthlyHourOverride,
  MonthlyHourOverrideInput,
  Project,
  ProjectAssignment,
  ProjectCreateInput,
  ProjectImportResponse,
  ProjectListItem,
  ProjectUpdateInput,
  ProjectViewer,
  ProjectViewerCreateInput,
  ProjectWithDetails
} from '../types/api';
import { fetchAssignmentAllocations } from './assignments';

export interface ProjectQueryParams {
  managerId?: number;
  viewerUserId?: number;
}

export async function fetchProjects(params: ProjectQueryParams = {}): Promise<ProjectListItem[]> {
  const { managerId, viewerUserId } = params;
  const { data } = await api.get<ProjectListItem[]>('/projects', {
    params: {
      ...(managerId ? { manager_id: managerId } : {}),
      ...(viewerUserId ? { viewer_user_id: viewerUserId } : {})
    }
  });
  return data;
}

export async function createProject(payload: ProjectCreateInput): Promise<Project> {
  const { data } = await api.post<Project>('/projects', payload);
  return data;
}

export async function updateProject(
  projectId: number,
  payload: ProjectUpdateInput
): Promise<Project> {
  const { data } = await api.put<Project>(`/projects/${projectId}`, payload);
  return data;
}

export async function importProjectsFromExcel(
  file: File,
  managerId?: number
): Promise<ProjectImportResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (managerId) {
    formData.append('manager_id', String(managerId));
  }

  const { data } = await api.post<ProjectImportResponse>('/projects/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}

export async function fetchProjectDetail(projectId: number): Promise<ProjectWithDetails> {
  const { data } = await api.get<ProjectWithDetails>(`/projects/${projectId}`);

  const assignmentsWithAllocations: ProjectAssignment[] = await Promise.all(
    data.assignments.map(async (assignment) => {
      const allocations = await fetchAssignmentAllocations(assignment.id);
      return { ...assignment, allocations };
    })
  );

  return { ...data, assignments: assignmentsWithAllocations };
}

export async function createMonthlyHourOverride(
  payload: MonthlyHourOverrideInput
): Promise<MonthlyHourOverride> {
  const { data } = await api.post<MonthlyHourOverride>('/projects/overrides', payload);
  return data;
}

export async function updateMonthlyHourOverride(
  overrideId: number,
  overridden_hours: number
): Promise<MonthlyHourOverride> {
  const { data } = await api.put<MonthlyHourOverride>(`/projects/overrides/${overrideId}`, {
    overridden_hours
  });
  return data;
}

export async function deleteMonthlyHourOverride(overrideId: number): Promise<void> {
  await api.delete(`/projects/overrides/${overrideId}`);
}

export async function fetchProjectViewers(projectId: number): Promise<ProjectViewer[]> {
  const { data } = await api.get<ProjectViewer[]>(`/projects/${projectId}/viewers`);
  return data;
}

export async function addProjectViewer(
  projectId: number,
  payload: ProjectViewerCreateInput
): Promise<ProjectViewer> {
  const { data } = await api.post<ProjectViewer>(`/projects/${projectId}/viewers`, {
    ...payload,
    project_id: projectId
  });
  return data;
}

export async function removeProjectViewer(projectId: number, userId: number): Promise<void> {
  await api.delete(`/projects/${projectId}/viewers/${userId}`);
}

