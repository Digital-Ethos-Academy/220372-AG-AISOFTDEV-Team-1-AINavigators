import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, ChevronDown, ChevronUp, ExternalLink, TrendingUp, Users } from 'lucide-react';
import type { ConflictDetail } from '../../types/api';

interface ConflictAlertsProps {
  conflicts: ConflictDetail[];
}

export default function ConflictAlerts({ conflicts }: ConflictAlertsProps) {
  const [expandedEmployees, setExpandedEmployees] = useState<Set<number>>(new Set());

  const toggleEmployee = (userId: number) => {
    setExpandedEmployees((prev) => {
      const next = new Set(prev);
      if (next.has(userId)) {
        next.delete(userId);
      } else {
        next.add(userId);
      }
      return next;
    });
  };
  if (conflicts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Users className="h-12 w-12 text-slate-300 mb-3" />
        <p className="text-sm text-slate-500">
          No over-allocations detected. Keep monitoring as plans evolve.
        </p>
      </div>
    );
  }

  // Group conflicts by employee (consolidate by employee name to handle duplicates)
  const conflictsByEmployee = conflicts.reduce((acc, conflict) => {
    // Use employee name as the primary key to avoid duplicates
    const existing = acc.find(c => c.employee.toLowerCase() === conflict.employee.toLowerCase());
    if (existing) {
      existing.conflicts.push(conflict);
      // Keep the first user_id encountered for this employee
    } else {
      acc.push({
        user_id: conflict.user_id,
        employee: conflict.employee,
        conflicts: [conflict]
      });
    }
    return acc;
  }, [] as { user_id: number; employee: string; conflicts: ConflictDetail[] }[]);

  // Consolidate duplicate months within each employee and sort
  conflictsByEmployee.forEach((employeeGroup) => {
    // Group by month to consolidate duplicates
    const monthMap = new Map<string, ConflictDetail>();
    
    employeeGroup.conflicts.forEach((conflict) => {
      const existing = monthMap.get(conflict.month);
      if (existing) {
        // Merge projects and use max values for hours/fte
        existing.total_hours = Math.max(existing.total_hours, conflict.total_hours);
        existing.fte = Math.max(existing.fte, conflict.fte);
        // Combine projects, avoiding duplicates by project_id
        conflict.projects.forEach((project) => {
          const existingProject = existing.projects.find(
            p => p.project_id === project.project_id && p.project_name === project.project_name
          );
          if (!existingProject) {
            existing.projects.push(project);
          }
        });
      } else {
        // Create a copy to avoid mutating original data
        monthMap.set(conflict.month, {
          ...conflict,
          projects: [...conflict.projects]
        });
      }
    });

    // Convert back to array and sort by date
    employeeGroup.conflicts = Array.from(monthMap.values()).sort((a, b) => {
      // Parse month strings like "Nov 2025", "Feb 2026"
      const parseMonth = (monthStr: string) => {
        const [month, year] = monthStr.split(' ');
        const monthIndex = new Date(Date.parse(month + ' 1, 2000')).getMonth();
        return new Date(parseInt(year), monthIndex);
      };
      return parseMonth(a.month).getTime() - parseMonth(b.month).getTime();
    });
  });

  // Sort employees by maximum FTE (highest severity first)
  conflictsByEmployee.sort((a, b) => {
    const maxFteA = Math.max(...a.conflicts.map(c => c.fte));
    const maxFteB = Math.max(...b.conflicts.map(c => c.fte));
    return maxFteB - maxFteA;
  });

  return (
    <div className="space-y-4">
      {conflictsByEmployee.map(({ user_id, employee, conflicts: employeeConflicts }) => {
        const maxFTE = Math.max(...employeeConflicts.map(c => c.fte));
        const totalHours = employeeConflicts.reduce((sum, c) => sum + c.total_hours, 0);
        
        // Determine severity color
        const getSeverityColor = (fte: number) => {
          if (fte >= 1.5) return 'red';
          if (fte >= 1.3) return 'orange';
          return 'amber';
        };
        
        const severityColor = getSeverityColor(maxFTE);
        const colorClasses = {
          red: {
            bg: 'bg-red-50 border-red-200',
            text: 'text-red-700',
            badge: 'bg-red-100 text-red-700 border-red-300',
            icon: 'text-red-500'
          },
          orange: {
            bg: 'bg-orange-50 border-orange-200',
            text: 'text-orange-700',
            badge: 'bg-orange-100 text-orange-700 border-orange-300',
            icon: 'text-orange-500'
          },
          amber: {
            bg: 'bg-amber-50 border-amber-200',
            text: 'text-amber-700',
            badge: 'bg-amber-100 text-amber-700 border-amber-300',
            icon: 'text-amber-500'
          }
        };
        
        const colors = colorClasses[severityColor];
        const isExpanded = expandedEmployees.has(user_id);

        return (
          <div
            key={user_id}
            className={`rounded-lg border-2 ${colors.bg}`}
          >
            {/* Clickable Header */}
            <button
              onClick={() => toggleEmployee(user_id)}
              className="w-full p-4 flex items-start justify-between hover:opacity-80 transition-opacity text-left"
            >
              <div className="flex items-center gap-3">
                <AlertTriangle className={`h-5 w-5 ${colors.icon}`} />
                <div>
                  <h4 className={`font-semibold ${colors.text}`}>{employee}</h4>
                  <p className="text-xs text-slate-600 mt-0.5">
                    {employeeConflicts.length} conflict{employeeConflicts.length !== 1 ? 's' : ''} • {totalHours}h total
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${colors.badge}`}>
                  <TrendingUp className="h-3.5 w-3.5" />
                  <span className="text-sm font-bold">{(maxFTE * 100).toFixed(0)}% FTE</span>
                </div>
                {isExpanded ? (
                  <ChevronUp className={`h-5 w-5 ${colors.icon}`} />
                ) : (
                  <ChevronDown className={`h-5 w-5 ${colors.icon}`} />
                )}
              </div>
            </button>

            {/* Expandable Details */}
            {isExpanded && (
              <div className="px-4 pb-4">
                <div className="space-y-3">
                  {employeeConflicts.map((conflict, idx) => (
                    <div key={idx} className="bg-white rounded-md p-3 border border-slate-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-semibold text-slate-500 uppercase">
                          {conflict.month}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-600">
                            {conflict.total_hours}h total
                          </span>
                          <span className={`text-xs font-semibold px-2 py-0.5 rounded ${colors.badge}`}>
                            {(conflict.fte * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      {conflict.projects.length > 0 && (
                        <div className="mt-2 space-y-1">
                          <p className="text-xs font-medium text-slate-700 mb-1">
                            Projects ({conflict.projects.length}):
                          </p>
                          <div className="space-y-1">
                            {conflict.projects.map((project, pidx) => (
                              <div
                                key={pidx}
                                className="flex items-center justify-between text-xs bg-slate-50 rounded px-2 py-1.5 border border-slate-100"
                              >
                                <div className="flex items-center gap-2 flex-1 min-w-0">
                                  {project.project_id ? (
                                    <Link
                                      to={`/projects/${project.project_id}`}
                                      className="text-blue-600 hover:text-blue-800 hover:underline font-medium truncate flex items-center gap-1"
                                    >
                                      {project.project_name}
                                      <ExternalLink className="h-3 w-3 flex-shrink-0" />
                                    </Link>
                                  ) : (
                                    <span className="text-slate-700 font-medium truncate">
                                      {project.project_name}
                                    </span>
                                  )}
                                </div>
                                <span className="text-slate-600 font-semibold ml-2 flex-shrink-0">
                                  {project.hours}h
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <div className={`mt-3 pt-3 border-t border-slate-200`}>
                  <p className={`text-xs ${colors.text} font-medium`}>
                    💡 <strong>Recommendation:</strong> Reduce hours on lower-priority projects, redistribute work to available team members, or adjust timelines.
                  </p>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

