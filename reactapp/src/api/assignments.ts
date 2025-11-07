import api from './client';
import type {
  Allocation,
  AllocationInput,
  AssignmentDistributionInput,
  ProjectAssignment,
  ProjectAssignmentCreateInput,
  ProjectAssignmentUpdateInput,
  ProjectAssignmentWithAllocations
} from '../types/api';

export async function createAssignment(
  payload: ProjectAssignmentCreateInput
): Promise<ProjectAssignment> {
  const { data } = await api.post<ProjectAssignment>('/allocations/assignments', payload);
  return data;
}

export async function deleteAssignment(assignmentId: number): Promise<void> {
  await api.delete(`/allocations/assignments/${assignmentId}`);
}

export async function updateAssignment(
  assignmentId: number,
  payload: ProjectAssignmentUpdateInput
): Promise<ProjectAssignment> {
  const { data } = await api.put<ProjectAssignment>(`/allocations/assignments/${assignmentId}`, payload);
  return data;
}

export async function fetchAssignmentAllocations(assignmentId: number): Promise<Allocation[]> {
  const { data } = await api.get<ProjectAssignmentWithAllocations>(
    `/allocations/assignments/${assignmentId}`
  );
  return data.allocations ?? [];
}

export async function createAllocation(payload: AllocationInput): Promise<Allocation> {
  const { data } = await api.post<Allocation>('/allocations', payload);
  return data;
}

export async function updateAllocation(
  allocationId: number,
  allocated_hours: number
): Promise<Allocation> {
  const { data } = await api.put<Allocation>(`/allocations/${allocationId}`, {
    allocated_hours
  });
  return data;
}

export async function deleteAllocation(allocationId: number): Promise<void> {
  await api.delete(`/allocations/${allocationId}`);
}

export async function distributeAssignmentAllocations(
  assignmentId: number,
  payload: AssignmentDistributionInput
): Promise<Allocation[]> {
  const { data } = await api.post<Allocation[]>(
    `/allocations/assignments/${assignmentId}/distribute`,
    payload
  );
  return data;
}

