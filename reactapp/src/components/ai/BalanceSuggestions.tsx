import { useState } from 'react';
import { ArrowRight, ChevronDown, ChevronUp, ExternalLink, Info, Scale, TrendingDown, TrendingUp, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { BalanceSuggestion } from '../../types/api';

interface BalanceSuggestionsProps {
  suggestions: BalanceSuggestion[];
}

export default function BalanceSuggestions({ suggestions }: BalanceSuggestionsProps) {
  const [expandedEmployees, setExpandedEmployees] = useState<Set<string>>(new Set());

  const toggleEmployee = (employee: string) => {
    setExpandedEmployees((prev) => {
      const next = new Set(prev);
      if (next.has(employee)) {
        next.delete(employee);
      } else {
        next.add(employee);
      }
      return next;
    });
  };
  if (suggestions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Scale className="h-12 w-12 text-slate-300 mb-3" />
        <p className="text-sm text-slate-500">
          No balancing opportunities detected. Re-run after new allocations are captured.
        </p>
      </div>
    );
  }

  // Group suggestions by from_employee for better organization
  // Use case-insensitive comparison to consolidate duplicates
  const suggestionsByEmployee = suggestions.reduce((acc, suggestion) => {
    const from = (suggestion.from_employee || 'Unknown').trim();
    // Find existing key with case-insensitive match
    const existingKey = Object.keys(acc).find(
      key => key.toLowerCase() === from.toLowerCase()
    );
    
    if (existingKey) {
      acc[existingKey].push(suggestion);
    } else {
      acc[from] = [suggestion];
    }
    return acc;
  }, {} as Record<string, BalanceSuggestion[]>);

  // Sort employees by total hours to redistribute (highest first)
  const sortedEmployees = Object.entries(suggestionsByEmployee).sort((a, b) => {
    const totalA = a[1].reduce((sum, s) => sum + s.recommended_hours, 0);
    const totalB = b[1].reduce((sum, s) => sum + s.recommended_hours, 0);
    return totalB - totalA;
  });

  return (
    <div className="space-y-4">
      {sortedEmployees.map(([fromEmployee, employeeSuggestions]) => {
        const totalHoursToShift = employeeSuggestions.reduce(
          (sum, s) => sum + s.recommended_hours,
          0
        );
        const isExpanded = expandedEmployees.has(fromEmployee);

        return (
          <div
            key={fromEmployee}
            className="rounded-lg border-2 border-purple-200 bg-purple-50"
          >
            {/* Clickable Header */}
            <button
              onClick={() => toggleEmployee(fromEmployee)}
              className="w-full p-4 flex items-start justify-between hover:opacity-80 transition-opacity text-left"
            >
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-purple-100 border-2 border-purple-300">
                  <Users className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-purple-900">{fromEmployee}</h4>
                  <p className="text-xs text-purple-700 mt-0.5">
                    {employeeSuggestions.length} transfer{employeeSuggestions.length !== 1 ? 's' : ''} • Redistribute {totalHoursToShift}h
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="px-3 py-1 rounded-full bg-purple-100 text-purple-700 border border-purple-300">
                  <span className="text-sm font-bold">{totalHoursToShift}h</span>
                </div>
                {isExpanded ? (
                  <ChevronUp className="h-5 w-5 text-purple-600" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-purple-600" />
                )}
              </div>
            </button>

            {/* Expandable Details */}
            {isExpanded && (
              <div className="px-4 pb-4">
                <div className="space-y-3">
                  {employeeSuggestions.map((suggestion, idx) => {
                    return (
                      <div
                        key={idx}
                        className="bg-white rounded-lg p-4 border-2 border-purple-100 hover:border-purple-300 transition-all"
                      >
                        {/* Header: Employee Transfer */}
                        <div className="flex items-start justify-between gap-4 mb-3">
                          <div className="flex items-center gap-3 flex-1">
                            {/* From Employee */}
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <TrendingDown className="h-4 w-4 text-red-500" />
                                <div>
                                  <p className="font-semibold text-slate-900">
                                    {suggestion.from_employee || 'Unknown'}
                                  </p>
                                  {suggestion.from_employee_current_fte !== undefined && (
                                    <p className="text-xs text-slate-600">
                                      Currently:{' '}
                                      <span className={`font-bold ${
                                        suggestion.from_employee_current_fte > 1.0
                                          ? 'text-red-600'
                                          : 'text-slate-700'
                                      }`}>
                                        {Math.round(suggestion.from_employee_current_fte * 100)}% FTE
                                      </span>
                                      {suggestion.from_employee_current_hours && (
                                        <span className="text-slate-500">
                                          {' '}({suggestion.from_employee_current_hours}h)
                                        </span>
                                      )}
                                    </p>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* Arrow */}
                            <div className="flex flex-col items-center px-2">
                              <ArrowRight className="h-5 w-5 text-purple-500" />
                              <div className="mt-1 px-2 py-0.5 rounded-full bg-purple-100 border border-purple-300">
                                <span className="text-xs font-bold text-purple-700">
                                  {suggestion.recommended_hours}h
                                </span>
                              </div>
                            </div>

                            {/* To Employee */}
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <TrendingUp className="h-4 w-4 text-green-500" />
                                <div>
                                  <p className="font-semibold text-slate-900">
                                    {suggestion.to_employee || 'Unknown'}
                                  </p>
                                  {suggestion.to_employee_current_fte !== undefined && (
                                    <p className="text-xs text-slate-600">
                                      Currently:{' '}
                                      <span className={`font-bold ${
                                        suggestion.to_employee_current_fte < 0.5
                                          ? 'text-blue-600'
                                          : 'text-slate-700'
                                      }`}>
                                        {Math.round(suggestion.to_employee_current_fte * 100)}% FTE
                                      </span>
                                      {suggestion.to_employee_current_hours && (
                                        <span className="text-slate-500">
                                          {' '}({suggestion.to_employee_current_hours}h)
                                        </span>
                                      )}
                                    </p>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>

                        </div>

                        {/* Reasoning */}
                        {suggestion.reasoning && (
                          <div className="mt-3 pt-3 border-t border-slate-100">
                            <div className="flex items-start gap-2">
                              <Info className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                              <p className="text-xs text-slate-700">
                                <span className="font-semibold">Impact:</span> {suggestion.reasoning}
                              </p>
                            </div>
                          </div>
                        )}

                        {/* Project Links for Implementation */}
                        {(suggestion.from_employee_projects && suggestion.from_employee_projects.length > 0) || 
                         (suggestion.to_employee_projects && suggestion.to_employee_projects.length > 0) ? (
                          <div className="mt-3 pt-3 border-t border-slate-200">
                            <p className="text-xs font-semibold text-slate-700 mb-2">
                              📋 Projects to adjust:
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              {/* Reduce hours from these projects */}
                              {suggestion.from_employee_projects && suggestion.from_employee_projects.length > 0 && (
                                <div className="space-y-1">
                                  <p className="text-xs font-medium text-red-700 flex items-center gap-1">
                                    <TrendingDown className="h-3 w-3" />
                                    Reduce hours from:
                                  </p>
                                  <div className="space-y-1">
                                    {suggestion.from_employee_projects.map((project) => (
                                      <Link
                                        key={project.project_id}
                                        to={`/projects/${project.project_id}`}
                                        className="flex items-center gap-1.5 p-2 rounded bg-red-50 hover:bg-red-100 border border-red-200 transition-colors group"
                                      >
                                        <ExternalLink className="h-3 w-3 text-red-600 flex-shrink-0" />
                                        <span className="text-xs text-red-800 font-medium truncate flex-1">
                                          {project.project_name}
                                        </span>
                                        <span className="text-xs text-red-600 opacity-0 group-hover:opacity-100 transition-opacity">
                                          View →
                                        </span>
                                      </Link>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Add hours to these projects */}
                              {suggestion.to_employee_projects && suggestion.to_employee_projects.length > 0 && (
                                <div className="space-y-1">
                                  <p className="text-xs font-medium text-green-700 flex items-center gap-1">
                                    <TrendingUp className="h-3 w-3" />
                                    Add {suggestion.to_employee} to:
                                  </p>
                                  <div className="space-y-1">
                                    {suggestion.to_employee_projects.map((project) => (
                                      <Link
                                        key={project.project_id}
                                        to={`/projects/${project.project_id}`}
                                        className="flex items-center gap-1.5 p-2 rounded bg-green-50 hover:bg-green-100 border border-green-200 transition-colors group"
                                      >
                                        <ExternalLink className="h-3 w-3 text-green-600 flex-shrink-0" />
                                        <span className="text-xs text-green-800 font-medium truncate flex-1">
                                          {project.project_name}
                                        </span>
                                        <span className="text-xs text-green-600 opacity-0 group-hover:opacity-100 transition-opacity">
                                          View →
                                        </span>
                                      </Link>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                            <p className="text-xs text-slate-500 mt-2 italic">
                              💡 Click any project to view allocation grid and make adjustments
                            </p>
                          </div>
                        ) : (
                          <div className="mt-3 pt-3 border-t border-slate-200">
                            <p className="text-xs text-slate-500 italic">
                              ℹ️ No active project allocations found for current month. Consider adding new assignments or adjusting future allocations.
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                <div className="mt-4 pt-3 border-t border-purple-200">
                  <div className="flex items-start gap-2 p-3 bg-purple-50 rounded-lg">
                    <Scale className="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-purple-800">
                      <strong>What are these transfers?</strong> These are AI-recommended hour reallocations from overloaded employees (&gt;100% FTE) to underutilized employees (&lt;50% FTE). Implementing these suggestions helps prevent burnout and improves team morale by distributing workload more evenly across your team.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Summary */}
      <div className="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
        <div className="flex items-start gap-2">
          <Scale className="h-4 w-4 text-slate-500 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-slate-600 space-y-1">
            <p>
              <span className="font-semibold text-slate-800">
                {suggestions.length} rebalancing opportunit{suggestions.length !== 1 ? 'ies' : 'y'}
              </span>{' '}
              identified across{' '}
              <span className="font-semibold">
                {sortedEmployees.length} overloaded employee{sortedEmployees.length !== 1 ? 's' : ''}
              </span>.
            </p>
            <p className="text-slate-500">
              Implementing these suggestions will help distribute workload more evenly and improve team well-being.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

