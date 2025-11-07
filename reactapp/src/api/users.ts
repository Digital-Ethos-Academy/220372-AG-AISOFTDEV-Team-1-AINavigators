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
  managerId?: number;
  systemRole?: SystemRole;
  includeGlobal?: boolean;
}

export async function fetchEmployees(params: EmployeeQueryParams = {}): Promise<EmployeeListItem[]> {
  const { managerId, systemRole, includeGlobal } = params;
  const { data } = await api.get<EmployeeListItem[]>('/employees', {
    params: {
      ...(managerId ? { manager_id: managerId } : {}),
      ...(systemRole ? { system_role: systemRole } : {}),
      ...(includeGlobal ? { include_global: includeGlobal } : {})
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

