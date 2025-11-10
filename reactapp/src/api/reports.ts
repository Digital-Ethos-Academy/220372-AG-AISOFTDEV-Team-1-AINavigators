import api from './client';
import type {
  EmployeeTimeline,
  PortfolioDashboard,
  ProjectDashboard,
  UtilizationByRoleResponse
} from '../types/api';

export async function fetchPortfolioDashboard(managerId: number): Promise<PortfolioDashboard> {
  const { data } = await api.get<PortfolioDashboard>('/reports/portfolio-dashboard', {
    params: { manager_id: managerId }
  });
  return data;
}

export interface ManagerAllocationsParams {
  managerId: number;
  startYear: number;
  startMonth: number;
  endYear: number;
  endMonth: number;
}

export interface EmployeeMonthlyTotal {
  year: number;
  month: number;
  total_hours: number;
  fte_percentage: number;
}

export interface EmployeeAllocationRollup {
  employee_id: number;
  employee_name: string;
  total_funded_hours: number;
  monthly_totals: EmployeeMonthlyTotal[];
}

export interface ManagerAllocationsResponse {
  employees: EmployeeAllocationRollup[];
  date_range: {
    start_year: number;
    start_month: number;
    end_year: number;
    end_month: number;
  };
}

export async function fetchManagerAllocations(params: ManagerAllocationsParams): Promise<ManagerAllocationsResponse> {
  const { managerId, startYear, startMonth, endYear, endMonth } = params;
  const { data } = await api.get<ManagerAllocationsResponse>('/reports/manager-allocations', {
    params: {
      manager_id: managerId,
      start_year: startYear,
      start_month: startMonth,
      end_year: endYear,
      end_month: endMonth
    }
  });
  return data;
}

export async function fetchProjectDashboard(projectId: number): Promise<ProjectDashboard> {
  const { data } = await api.get<ProjectDashboard>(`/reports/project-dashboard/${projectId}`);
  return data;
}

export interface TimelineFilters {
  startYear?: number;
  startMonth?: number;
  endYear?: number;
  endMonth?: number;
}

export async function fetchEmployeeTimeline(
  employeeId: number,
  filters: TimelineFilters = {}
): Promise<EmployeeTimeline> {
  const { data } = await api.get<EmployeeTimeline>(`/reports/employee-timeline/${employeeId}`, {
    params: filters
  });
  return data;
}

export async function fetchUtilizationByRole(
  year: number,
  month: number
): Promise<UtilizationByRoleResponse> {
  const { data } = await api.get<UtilizationByRoleResponse>('/reports/utilization-by-role', {
    params: { year, month }
  });
  return data;
}

export async function exportPortfolioToExcel(managerId: number): Promise<Blob> {
  const { data } = await api.get<Blob>('/reports/export/portfolio', { 
    params: { manager_id: managerId },
    responseType: 'blob' 
  });
  return data;
}

export async function exportProjectToExcel(projectId: number): Promise<Blob> {
  const { data } = await api.get<Blob>(`/reports/export/project/${projectId}`, {
    responseType: 'blob'
  });
  return data;
}

