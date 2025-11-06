import api from './client';
import type { EmployeeListItem, UserAllocationSummaryItem } from '../types/api';

export async function fetchEmployees(): Promise<EmployeeListItem[]> {
  const { data } = await api.get<EmployeeListItem[]>('/employees');
  return data;
}

export async function fetchUserAllocationSummary(
  userId: number
): Promise<UserAllocationSummaryItem[]> {
  const { data } = await api.get<UserAllocationSummaryItem[]>(`/allocations/users/${userId}/summary`);
  return data;
}

