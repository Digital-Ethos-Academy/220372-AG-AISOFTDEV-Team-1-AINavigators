import { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';

import type {
  Allocation,
  MonthlyHourOverride,
  ProjectAssignment,
  ProjectWithDetails
} from '../../types/api';
import { getHeatmapClass } from '../../utils/fte';
import { buildMonthlyTimeline, buildSprintTimeline, getMonthlyWorkHours } from '../../utils/time';

type ViewMode = 'month' | 'sprint';

interface AllocationGridProps {
  project: ProjectWithDetails;
  viewMode: ViewMode;
  onChangeHours: (params: {
    assignmentId: number;
    userId: number;
    allocationId?: number;
    year: number;
    month: number;
    hours: number;
  }) => Promise<void>;
  userTotals: Record<string, number>;
  onRequestOverride: (params: {
    year: number;
    month: number;
    currentHours: number;
    baselineHours: number;
    override?: MonthlyHourOverride;
  }) => void;
}

interface CellKey {
  assignmentId: number;
  year: number;
  month: number;
}

const cellKey = ({ assignmentId, year, month }: CellKey) => `${assignmentId}-${year}-${month}`;

const formatHours = (value: number) => `${value.toFixed(0)} hrs`;

function AssignmentSummary({ assignment, values }: { assignment: ProjectAssignment; values: Record<string, number> }) {
  const monthlyKeys = Object.keys(values).filter((key) => key.startsWith(`${assignment.id}-`));
  const totalAllocated = monthlyKeys.reduce((sum, key) => sum + (values[key] ?? 0), 0);
  const remaining = assignment.funded_hours - totalAllocated;
  const isOverBudget = remaining < 0;

  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm">
      <div className="flex flex-col">
        <span className="font-medium text-slate-700">{assignment.user.full_name}</span>
        <span className="text-xs text-slate-500">
          {assignment.role.name} · {assignment.lcat.name}
        </span>
      </div>
      <div className="flex items-center gap-4 text-xs">
        <div className="flex flex-col text-right">
          <span className="text-slate-500">Funded</span>
          <span className="font-semibold text-slate-700">{assignment.funded_hours} hrs</span>
        </div>
        <div className="flex flex-col text-right">
          <span className="text-slate-500">Allocated</span>
          <span className="font-semibold text-slate-700">{totalAllocated} hrs</span>
        </div>
        <div className="flex flex-col text-right">
          <span className="text-slate-500">Remaining</span>
          <span className={`font-semibold ${isOverBudget ? 'text-red-600' : 'text-emerald-600'}`}>
            {remaining} hrs
          </span>
        </div>
      </div>
    </div>
  );
}

function computeInitialValues(assignments: ProjectAssignment[]): Record<string, number> {
  const initial: Record<string, number> = {};
  assignments.forEach((assignment) => {
    assignment.allocations?.forEach((allocation) => {
      const key = cellKey({ assignmentId: assignment.id, year: allocation.year, month: allocation.month });
      initial[key] = allocation.allocated_hours;
    });
  });
  return initial;
}

function findAllocation(
  assignment: ProjectAssignment,
  year: number,
  month: number
): Allocation | undefined {
  return assignment.allocations?.find((alloc) => alloc.year === year && alloc.month === month);
}

function getUserTotal(userTotals: Record<string, number>, userId: number, year: number, month: number) {
  return userTotals[`${userId}-${year}-${month}`];
}

export default function AllocationGrid({ project, viewMode, onChangeHours, userTotals, onRequestOverride }: AllocationGridProps) {
  const [cellValues, setCellValues] = useState<Record<string, number>>(() => computeInitialValues(project.assignments));
  const [draftValues, setDraftValues] = useState<Record<string, string>>({});
  const [pendingCells, setPendingCells] = useState<Record<string, boolean>>({});

  useEffect(() => {
    setCellValues(computeInitialValues(project.assignments));
    setDraftValues({});
  }, [project.id, project.assignments]);

  const months = useMemo(() => buildMonthlyTimeline(project), [project]);
  const sprintTimeline = useMemo(() => buildSprintTimeline(project), [project]);

  const overrides = useMemo(() => {
    const map = new Map<string, MonthlyHourOverride>();
    project.monthly_hour_overrides.forEach((override) => {
      map.set(`${override.year}-${override.month}`, override);
    });
    return map;
  }, [project.monthly_hour_overrides]);

  const monthlyHoursMap = useMemo(() => {
    const map = new Map<string, number>();
    months.forEach(({ year, month }) => {
      map.set(`${year}-${month}`, getMonthlyWorkHours(year, month, project.monthly_hour_overrides));
    });
    return map;
  }, [months, project.monthly_hour_overrides]);

  const handleInputChange = (key: string, value: string) => {
    setDraftValues((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async ({ assignment, year, month }: { assignment: ProjectAssignment; year: number; month: number }) => {
    const key = cellKey({ assignmentId: assignment.id, year, month });
    const rawDraft = draftValues[key];
    const hours = rawDraft === undefined ? cellValues[key] ?? 0 : Number(rawDraft || 0);
    const allocation = findAllocation(assignment, year, month);

    if (Number.isNaN(hours) || hours < 0) {
      return;
    }

    setPendingCells((prev) => ({ ...prev, [key]: true }));

    try {
      await onChangeHours({
        assignmentId: assignment.id,
        userId: assignment.user_id,
        allocationId: allocation?.id,
        year,
        month,
        hours
      });
      setCellValues((prev) => ({ ...prev, [key]: hours }));
      setDraftValues((prev) => {
        const updated = { ...prev };
        delete updated[key];
        return updated;
      });
    } finally {
      setPendingCells((prev) => ({ ...prev, [key]: false }));
    }
  };

  const renderMonthlyView = () => (
    <div className="overflow-x-auto">
      <table className="min-w-full border-collapse text-sm">
        <thead>
          <tr className="bg-slate-50">
            <th className="sticky left-0 z-10 w-64 border border-slate-200 bg-slate-50 px-4 py-3 text-left font-semibold text-slate-600">
              Team Member
            </th>
            {months.map(({ label, year, month }) => {
              const override = overrides.get(`${year}-${month}`);
              const workHours = monthlyHoursMap.get(`${year}-${month}`) ?? 160;
              const baselineHours = getMonthlyWorkHours(year, month, []);
              return (
                <th key={`${year}-${month}`} className="border border-slate-200 px-4 py-3 text-left font-semibold text-slate-600">
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <div>{label}</div>
                      <div className="text-xs text-slate-500">{workHours} hrs</div>
                    </div>
                    <button
                      type="button"
                      className="text-xs font-medium text-blue-600 hover:underline"
                      onClick={() =>
                        onRequestOverride({
                          year,
                          month,
                            currentHours: workHours,
                            baselineHours,
                          override
                        })
                      }
                    >
                      {override ? 'Edit override' : 'Override'}
                    </button>
                  </div>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {project.assignments.map((assignment) => (
            <tr key={assignment.id} className="bg-white">
              <td className="sticky left-0 z-10 border border-slate-200 bg-white px-4 py-4 align-top">
                <AssignmentSummary assignment={assignment} values={cellValues} />
              </td>
              {months.map(({ year, month }) => {
                const key = cellKey({ assignmentId: assignment.id, year, month });
                const workHours = monthlyHoursMap.get(`${year}-${month}`) ?? 160;
                const value = draftValues[key] ?? String(cellValues[key] ?? 0);
                const numericValue = Number(value) || 0;
                const fte = workHours ? numericValue / workHours : 0;
                const totalUserHours = getUserTotal(userTotals, assignment.user_id, year, month) ?? numericValue;
                const totalFte = workHours ? totalUserHours / workHours : 0;
                const isOverAllocation = totalFte > 1;

                return (
                  <td key={key} className="border border-slate-200 px-3 py-2 align-top">
                    <div className={`rounded-md px-3 py-3 ${getHeatmapClass(fte)}`}>
                      <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                        <span>{formatHours(numericValue)}</span>
                        <span>{Math.round(fte * 100)}% FTE</span>
                      </div>
                      <div className="mt-2 flex items-center gap-2">
                        <input
                          type="number"
                          min={0}
                          className="w-full rounded-md border border-slate-200 bg-white px-2 py-1 text-sm text-slate-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
                          value={draftValues[key] ?? String(cellValues[key] ?? 0)}
                          onChange={(event) => handleInputChange(key, event.target.value)}
                          onBlur={() => handleSave({ assignment, year, month })}
                          onKeyDown={(event) => {
                            if (event.key === 'Enter') {
                              event.currentTarget.blur();
                            }
                          }}
                        />
                        {pendingCells[key] && <Loader2 className="h-4 w-4 animate-spin text-slate-500" />}
                      </div>
                      {isOverAllocation && (
                        <div className="mt-2 flex items-center gap-1 text-xs font-medium text-red-600">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          {Math.round(totalFte * 100)}% FTE across all projects
                        </div>
                      )}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderSprintView = () => {
    const sprintsByMonthCounts = sprintTimeline.reduce<Record<string, number>>((acc, sprint) => {
      const key = `${sprint.year}-${sprint.month}`;
      acc[key] = (acc[key] ?? 0) + 1;
      return acc;
    }, {});

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse text-sm">
          <thead>
            <tr className="bg-slate-50">
              <th className="sticky left-0 z-10 w-64 border border-slate-200 bg-slate-50 px-4 py-3 text-left font-semibold text-slate-600">
                Team Member
              </th>
              {sprintTimeline.map((sprint) => (
                <th key={sprint.index} className="border border-slate-200 px-4 py-3 text-left font-semibold text-slate-600">
                  <div>{sprint.label}</div>
                  <div className="text-xs text-slate-500">{sprint.start.format('MMM D')} – {sprint.end.format('MMM D')}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {project.assignments.map((assignment) => (
              <tr key={assignment.id} className="bg-white">
                <td className="sticky left-0 z-10 border border-slate-200 bg-white px-4 py-4 align-top">
                  <AssignmentSummary assignment={assignment} values={cellValues} />
                </td>
                {sprintTimeline.map((sprint) => {
                  const key = `${assignment.id}-${sprint.index}`;
                  const monthKey = `${sprint.year}-${sprint.month}`;
                  const monthlyHours = cellValues[`${assignment.id}-${sprint.year}-${sprint.month}`] ?? 0;
                  const sprintCount = sprintsByMonthCounts[monthKey] ?? 2;
                  const sprintHours = monthlyHours / sprintCount;
                  const workHours = getMonthlyWorkHours(sprint.year, sprint.month, project.monthly_hour_overrides) / sprintCount;
                  const fte = workHours ? sprintHours / workHours : 0;

                  return (
                    <td key={key} className="border border-slate-200 px-3 py-2 align-top">
                      <div className={`rounded-md px-3 py-3 ${getHeatmapClass(fte)}`}>
                        <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                          <span>{formatHours(sprintHours)}</span>
                          <span>{Math.round(fte * 100)}% FTE</span>
                        </div>
                        <p className="mt-2 text-xs text-slate-500">Sprint hours are derived from the monthly plan. Edit in monthly view.</p>
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return viewMode === 'month' ? renderMonthlyView() : renderSprintView();
}

