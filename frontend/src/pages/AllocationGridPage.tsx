import { useState, useCallback } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Blocks, ArrowLeft, Plus, Save, AlertTriangle, LogOut, Loader2, AlertCircle } from 'lucide-react';
import { projectsService } from '../services/projects';
import { allocationsService } from '../services/allocations';
import { useAuth } from '../hooks/useAuth';
import type { Project, ProjectAssignment } from '../types/api.types';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

interface AllocationCell {
  assignmentId: number;
  allocationId?: number;
  monthYear: string;
  hours: number;
  isModified: boolean;
}

interface AssignmentRow {
  assignment: ProjectAssignment;
  cells: Map<string, AllocationCell>;
  totalAllocated: number;
  remainingHours: number;
  isOverBudget: boolean;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Generate array of months for the project duration
 */
function generateMonthColumns(startDate: string, numSprints: number): string[] {
  const start = new Date(startDate);
  const months: string[] = [];
  const totalMonths = Math.ceil((numSprints * 2) / 4); // 2 weeks per sprint, ~4 weeks per month

  for (let i = 0; i < totalMonths; i++) {
    const date = new Date(start);
    date.setMonth(start.getMonth() + i);
    const monthYear = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    months.push(monthYear);
  }

  return months;
}

/**
 * Format month-year for display
 */
function formatMonthYear(monthYear: string): string {
  const [year, month] = monthYear.split('-');
  const date = new Date(parseInt(year), parseInt(month) - 1);
  return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
}

/**
 * Calculate FTE percentage (160 hours = 1.0 FTE)
 */
function calculateFTE(hours: number): number {
  const HOURS_PER_MONTH = 160;
  return (hours / HOURS_PER_MONTH) * 100;
}

/**
 * Get color class based on FTE percentage
 */
function getFTEColorClass(fte: number): string {
  if (fte === 0) return 'bg-white';
  if (fte <= 25) return 'bg-blue-100';
  if (fte <= 50) return 'bg-blue-200';
  if (fte <= 75) return 'bg-blue-300';
  if (fte <= 100) return 'bg-blue-400 text-white';
  return 'bg-red-500 text-white'; // Over 100% FTE
}

/**
 * Build assignment rows from API data
 */
function buildAssignmentRows(
  assignments: ProjectAssignment[],
  monthColumns: string[]
): AssignmentRow[] {
  return assignments.map((assignment) => {
    const cells = new Map<string, AllocationCell>();
    let totalAllocated = 0;

    // Initialize all month cells
    monthColumns.forEach((monthYear) => {
      const [year, month] = monthYear.split('-').map(Number);
      const existingAlloc = assignment.allocations?.find(
        (a) => a.year === year && a.month === month
      );

      const hours = existingAlloc?.allocated_hours || 0;
      totalAllocated += hours;

      cells.set(monthYear, {
        assignmentId: assignment.id,
        allocationId: existingAlloc?.id,
        monthYear,
        hours,
        isModified: false,
      });
    });

    const remainingHours = assignment.funded_hours - totalAllocated;
    const isOverBudget = totalAllocated > assignment.funded_hours;

    return {
      assignment,
      cells,
      totalAllocated,
      remainingHours,
      isOverBudget,
    };
  });
}

// ============================================================================
// CELL COMPONENT
// ============================================================================

interface AllocationCellInputProps {
  cell: AllocationCell;
  onUpdate: (monthYear: string, hours: number) => void;
}

const AllocationCellInput = ({ cell, onUpdate }: AllocationCellInputProps) => {
  const fte = calculateFTE(cell.hours);
  const colorClass = getFTEColorClass(fte);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value === '' ? 0 : parseInt(e.target.value);
    if (!isNaN(value) && value >= 0) {
      onUpdate(cell.monthYear, value);
    }
  };

  return (
    <td className={`border border-gray-300 p-0 relative ${colorClass}`}>
      <div className="flex flex-col items-center justify-center h-full py-2">
        <input
          type="number"
          min="0"
          value={cell.hours || ''}
          onChange={handleChange}
          className={`w-full px-2 text-center text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-transparent ${
            cell.isModified ? 'font-bold' : ''
          }`}
          placeholder="0"
        />
        {cell.hours > 0 && (
          <div className="text-[10px] opacity-70 mt-0.5">
            {Math.round(fte)}%
          </div>
        )}
      </div>
    </td>
  );
};

// ============================================================================
// ROW COMPONENT
// ============================================================================

interface AssignmentRowComponentProps {
  row: AssignmentRow;
  monthColumns: string[];
  onCellUpdate: (assignmentId: number, monthYear: string, hours: number) => void;
}

const AssignmentRowComponent = ({ row, monthColumns, onCellUpdate }: AssignmentRowComponentProps) => {
  const { assignment } = row;
  
  // Handle both nested and flat data structures
  const employeeName = (assignment as any).user?.full_name || assignment.employee_name || 'Unknown';
  const roleName = (assignment as any).role?.name || assignment.role_name || 'N/A';

  return (
    <tr className={row.isOverBudget ? 'bg-red-50' : ''}>
      <td className="border border-gray-300 px-4 py-2 font-medium sticky left-0 bg-white z-10">
        <div className="flex flex-col">
          <span className="text-sm text-gray-900">{employeeName}</span>
          <span className="text-xs text-gray-500">{roleName}</span>
        </div>
      </td>
      <td className="border border-gray-300 px-4 py-2 text-sm text-center bg-gray-50">
        {assignment.funded_hours}h
      </td>
      {monthColumns.map((monthYear) => {
        const cell = row.cells.get(monthYear)!;
        return (
          <AllocationCellInput
            key={monthYear}
            cell={cell}
            onUpdate={(month, hours) => onCellUpdate(assignment.id, month, hours)}
          />
        );
      })}
      <td
        className={`border border-gray-300 px-4 py-2 text-sm text-center font-semibold ${
          row.isOverBudget ? 'text-red-600' : 'text-gray-900'
        }`}
      >
        {row.totalAllocated}h
      </td>
      <td
        className={`border border-gray-300 px-4 py-2 text-sm text-center ${
          row.isOverBudget ? 'text-red-600 font-semibold' : 'text-gray-600'
        }`}
      >
        {row.isOverBudget && <AlertTriangle className="inline h-4 w-4 mr-1" />}
        {row.remainingHours}h
      </td>
    </tr>
  );
};

// ============================================================================
// LAYOUT COMPONENTS
// ============================================================================

const AppHeader = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/dashboard" className="flex items-center gap-2">
              <Blocks className="h-7 w-7 text-blue-600" />
              <h1 className="text-xl font-bold text-blue-600">StaffAlloc</h1>
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link to="/dashboard" className="text-sm font-medium text-gray-500 hover:text-gray-700">
                Dashboard
              </Link>
              <Link to="/projects" className="text-sm font-medium text-blue-600 border-b-2 border-blue-600 pb-1">
                Projects
              </Link>
              <Link to="/employees" className="text-sm font-medium text-gray-500 hover:text-gray-700">
                Employees
              </Link>
              <Link to="/allocations" className="text-sm font-medium text-gray-500 hover:text-gray-700">
                Allocations
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden md:block">
              <p className="text-sm font-medium text-gray-700">{user?.full_name}</p>
              <p className="text-xs text-gray-500">{user?.system_role}</p>
            </div>
            <button
              onClick={logout}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              <LogOut className="h-4 w-4" />
              <span className="hidden md:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

interface ProjectHeaderProps {
  project: Project;
}

const ProjectHeader = ({ project }: ProjectHeaderProps) => (
  <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
    <div className="flex items-center justify-between">
      <div>
        <Link
          to="/projects"
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-2"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Projects
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">{project.code}</h1>
        <p className="text-sm text-gray-600 mt-1">{project.name}</p>
        <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
          <span>Client: {project.client || 'N/A'}</span>
          <span>•</span>
          <span>Sprints: {project.sprints}</span>
          <span>•</span>
          <span>Start: {new Date(project.start_date).toLocaleDateString()}</span>
        </div>
      </div>
      <div className="flex gap-2">
        <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium">
          <Plus className="h-4 w-4" />
          Add Employee
        </button>
      </div>
    </div>
  </div>
);

// ============================================================================
// LOADING & ERROR COMPONENTS
// ============================================================================

const LoadingState = () => (
  <div className="flex items-center justify-center h-64">
    <div className="text-center">
      <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
      <p className="text-gray-600">Loading allocation grid...</p>
    </div>
  </div>
);

const ErrorState = ({ error, onRetry }: { error: string; onRetry: () => void }) => (
  <div className="flex items-center justify-center h-64">
    <div className="text-center">
      <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
      <p className="text-red-600 mb-4">{error}</p>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Try Again
      </button>
    </div>
  </div>
);

// ============================================================================
// MAIN PAGE COMPONENT
// ============================================================================

export default function AllocationGridPage() {
  const { id } = useParams<{ id: string }>();
  const projectId = parseInt(id || '0');
  const [modifiedCells, setModifiedCells] = useState<Map<string, AllocationCell>>(new Map());
  const [isSaving, setIsSaving] = useState(false);

  // Fetch project details
  const {
    data: project,
    isLoading: projectLoading,
    error: projectError,
    refetch: refetchProject,
  } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsService.getProject(projectId),
    enabled: projectId > 0,
  });

  // Fetch project assignments
  const {
    data: assignments,
    isLoading: assignmentsLoading,
    error: assignmentsError,
    refetch: refetchAssignments,
  } = useQuery({
    queryKey: ['project-assignments', projectId],
    queryFn: () => projectsService.getProjectAssignments(projectId),
    enabled: projectId > 0,
  });

  const isLoading = projectLoading || assignmentsLoading;
  const error = projectError || assignmentsError;

  // Generate month columns based on project duration
  const monthColumns = project ? generateMonthColumns(project.start_date, project.sprints) : [];

  // Build assignment rows
  const assignmentRows = assignments ? buildAssignmentRows(assignments, monthColumns) : [];

  // Apply modified cells to rows
  assignmentRows.forEach((row) => {
    modifiedCells.forEach((modifiedCell, key) => {
      const [assignmentId, monthYear] = key.split(':');
      if (parseInt(assignmentId) === row.assignment.id) {
        row.cells.set(monthYear, modifiedCell);
      }
    });

    // Recalculate totals
    row.totalAllocated = Array.from(row.cells.values()).reduce((sum, cell) => sum + cell.hours, 0);
    row.remainingHours = row.assignment.funded_hours - row.totalAllocated;
    row.isOverBudget = row.totalAllocated > row.assignment.funded_hours;
  });

  const handleCellUpdate = useCallback((assignmentId: number, monthYear: string, hours: number) => {
    const key = `${assignmentId}:${monthYear}`;
    setModifiedCells((prev) => {
      const newMap = new Map(prev);
      const existingCell = prev.get(key);
      newMap.set(key, {
        assignmentId,
        allocationId: existingCell?.allocationId,
        monthYear,
        hours,
        isModified: true,
      });
      return newMap;
    });
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Save all modified cells
      const promises = Array.from(modifiedCells.values()).map(async (cell) => {
        if (cell.allocationId) {
          // Update existing allocation
          return allocationsService.updateAllocation(cell.allocationId, {
            allocated_hours: cell.hours,
          });
        } else if (cell.hours > 0) {
          // Create new allocation
          // Parse monthYear string (format: "YYYY-MM") into year and month
          const [year, month] = cell.monthYear.split('-').map(Number);
          return allocationsService.createAllocation({
            project_assignment_id: cell.assignmentId,
            year: year,
            month: month,
            allocated_hours: cell.hours,
          });
        }
      });

      await Promise.all(promises);

      // Refresh data
      await refetchAssignments();
      setModifiedCells(new Map());
    } catch (error) {
      console.error('Failed to save allocations:', error);
      alert('Failed to save allocations. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const hasModifications = modifiedCells.size > 0;
  const hasOverBudget = assignmentRows.some((row) => row.isOverBudget);

  if (isLoading) {
    return (
      <div className="bg-gray-50 min-h-screen">
        <AppHeader />
        <main className="max-w-screen-2xl mx-auto p-6">
          <LoadingState />
        </main>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="bg-gray-50 min-h-screen">
        <AppHeader />
        <main className="max-w-screen-2xl mx-auto p-6">
          <ErrorState
            error={error instanceof Error ? error.message : 'Failed to load project'}
            onRetry={() => {
              refetchProject();
              refetchAssignments();
            }}
          />
        </main>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      <AppHeader />
      <main className="max-w-screen-2xl mx-auto p-6">
        <ProjectHeader project={project} />

        {hasModifications && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-2 text-blue-800">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-medium">You have unsaved changes</span>
            </div>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
            >
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        )}

        {hasOverBudget && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center gap-2 text-red-800">
            <AlertTriangle className="h-5 w-5" />
            <span className="font-medium">Warning: Some employees have allocations exceeding their funded hours</span>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gray-50">
                  <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold text-gray-900 sticky left-0 bg-gray-50 z-20">
                    Employee
                  </th>
                  <th className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold text-gray-900">
                    Funded
                  </th>
                  {monthColumns.map((monthYear) => (
                    <th
                      key={monthYear}
                      className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold text-gray-900 min-w-[100px]"
                    >
                      {formatMonthYear(monthYear)}
                    </th>
                  ))}
                  <th className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold text-gray-900">
                    Total
                  </th>
                  <th className="border border-gray-300 px-4 py-2 text-center text-sm font-semibold text-gray-900">
                    Remaining
                  </th>
                </tr>
              </thead>
              <tbody>
                {assignmentRows.length === 0 ? (
                  <tr>
                    <td colSpan={monthColumns.length + 4} className="border border-gray-300 px-4 py-8 text-center text-gray-500">
                      No employees assigned to this project yet.
                      <br />
                      <button className="mt-2 text-blue-600 hover:underline">Add Employee</button>
                    </td>
                  </tr>
                ) : (
                  assignmentRows.map((row) => (
                    <AssignmentRowComponent
                      key={row.assignment.id}
                      row={row}
                      monthColumns={monthColumns}
                      onCellUpdate={handleCellUpdate}
                    />
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-6 bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Legend</h3>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-100 border border-gray-300"></div>
              <span>0-25% FTE</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-200 border border-gray-300"></div>
              <span>26-50% FTE</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-300 border border-gray-300"></div>
              <span>51-75% FTE</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-400 border border-gray-300"></div>
              <span>76-100% FTE</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-red-500 border border-gray-300"></div>
              <span>&gt;100% FTE</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
