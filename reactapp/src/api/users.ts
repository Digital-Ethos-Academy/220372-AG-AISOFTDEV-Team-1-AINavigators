import api from './client';
import type {
  EmployeeListItem,
  SystemRole,
  User,
  UserAllocationSummaryItem,
  UserCreateInput,
  UserWithAssignments
} from '../types/api';

export interface EmployeeQueryParams {
  managerId: number; // Required for data isolation
  systemRole?: SystemRole;
}

export async function fetchEmployees(params: EmployeeQueryParams): Promise<EmployeeListItem[]> {
  const { managerId, systemRole } = params;
  const { data } = await api.get<EmployeeListItem[]>('/employees', {
    params: {
      manager_id: managerId,
      ...(systemRole ? { system_role: systemRole } : {})
    }
  });
  return data;
}

export async function createEmployee(payload: UserCreateInput): Promise<User> {
  const { data } = await api.post<User>('/employees', payload);
  return data;
}

export async function fetchEmployee(employeeId: number): Promise<UserWithAssignments> {
  const { data } = await api.get<UserWithAssignments>(`/employees/${employeeId}`);
  return data;
}

export async function fetchUserAllocationSummary(
  userId: number
): Promise<UserAllocationSummaryItem[]> {
  const { data } = await api.get<UserAllocationSummaryItem[]>(`/allocations/users/${userId}/summary`);
  return data;
}

export async function deleteEmployee(employeeId: number): Promise<void> {
  await api.delete(`/employees/${employeeId}`);
}

