export type ProjectStatus = 'Planning' | 'Active' | 'Closed' | 'On Hold';

export interface UserSummary {
  id: number;
  full_name: string;
  email: string;
}

export interface Role {
  id: number;
  name: string;
  description?: string | null;
}

export interface LCAT {
  id: number;
  name: string;
  description?: string | null;
}

export interface Project {
  id: number;
  name: string;
  code: string;
  client?: string | null;
  start_date: string;
  sprints: number;
  status: ProjectStatus;
  manager_id?: number | null;
  manager?: UserSummary | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectListItem extends Project {}

export interface MonthlyHourOverride {
  id: number;
  project_id: number;
  year: number;
  month: number;
  overridden_hours: number;
}

export interface Allocation {
  id: number;
  project_assignment_id: number;
  year: number;
  month: number;
  allocated_hours: number;
}

export interface ProjectAssignment {
  id: number;
  project_id: number;
  user_id: number;
  role_id: number;
  lcat_id: number;
  funded_hours: number;
  created_at: string;
  updated_at: string;
  project: Project;
  user: UserSummary;
  role: Role;
  lcat: LCAT;
  allocations?: Allocation[];
}

export interface ProjectAssignmentWithAllocations extends ProjectAssignment {
  allocations: Allocation[];
}

export interface ProjectWithDetails extends Project {
  assignments: ProjectAssignment[];
  monthly_hour_overrides: MonthlyHourOverride[];
}

export interface User extends UserSummary {
  system_role: 'Admin' | 'Director' | 'PM' | 'Employee';
  is_active: boolean;
  last_login_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmployeeListItem extends User {}

export interface UserAllocationSummaryItem {
  year: number;
  month: number;
  total_hours: number;
}

export interface ProjectCreateInput {
  name: string;
  code: string;
  client?: string | null;
  start_date: string;
  sprints: number;
}

export interface ProjectAssignmentCreateInput {
  project_id: number;
  user_id: number;
  role_id: number;
  lcat_id: number;
  funded_hours: number;
}

export interface AllocationInput {
  project_assignment_id: number;
  year: number;
  month: number;
  allocated_hours: number;
}

export interface MonthlyHourOverrideInput {
  project_id: number;
  year: number;
  month: number;
  overridden_hours: number;
}

