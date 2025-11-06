import api from './client';
import type {
  MonthlyHourOverride,
  MonthlyHourOverrideInput,
  Project,
  ProjectAssignment,
  ProjectCreateInput,
  ProjectListItem,
  ProjectWithDetails
} from '../types/api';
import { fetchAssignmentAllocations } from './assignments';

export async function fetchProjects(): Promise<ProjectListItem[]> {
  const { data } = await api.get<ProjectListItem[]>('/projects');
  return data;
}

export async function createProject(payload: ProjectCreateInput): Promise<Project> {
  const { data } = await api.post<Project>('/projects', payload);
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

