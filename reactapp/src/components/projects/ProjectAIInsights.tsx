import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Info, Loader2, Sparkles, TriangleAlert } from 'lucide-react';

import {
  fetchBalanceSuggestions,
  fetchConflicts,
  fetchForecast,
  recommendStaff
} from '../../api/ai';
import type {
  BalanceSuggestionsResponse,
  BalanceSuggestion,
  ConflictDetail,
  ConflictsResponse,
  ForecastPrediction,
  ForecastResponse,
  LCAT,
  Role,
  StaffingRecommendationResponse
} from '../../types/api';
import { Card } from '../common';

interface ProjectAIInsightsProps {
  projectId: number;
  roles: Role[];
  lcats: LCAT[];
}

export default function ProjectAIInsights({ projectId, roles, lcats }: ProjectAIInsightsProps) {
  const [recommendation, setRecommendation] = useState<StaffingRecommendationResponse | null>(null);
  const [conflicts, setConflicts] = useState<ConflictsResponse | null>(null);
  const [balance, setBalance] = useState<BalanceSuggestionsResponse | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [staffingError, setStaffingError] = useState<string | null>(null);

  const recommendMutation = useMutation({
    mutationFn: (params: { roleId?: number; lcatId?: number; year: number; month: number; requiredHours: number }) =>
      recommendStaff({
        project_id: projectId,
        role_id: params.roleId,
        lcat_id: params.lcatId,
        year: params.year,
        month: params.month,
        required_hours: params.requiredHours
      }),
    onSuccess: (response) => {
      setRecommendation(response);
      setStaffingError(null);
    }
  });

  const conflictsMutation = useMutation({
    mutationFn: fetchConflicts,
    onSuccess: (response) => setConflicts(response)
  });

  const balanceMutation = useMutation({
    mutationFn: () => fetchBalanceSuggestions(projectId),
    onSuccess: (response) => setBalance(response)
  });

  const forecastMutation = useMutation({
    mutationFn: () => fetchForecast(3),
    onSuccess: (response) => setForecast(response)
  });

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card
        title="Fill open staffing needs"
        description="Let the AI suggest team members based on availability and skills."
      >
        <form
          className="space-y-3 text-sm"
          onSubmit={(event) => {
            event.preventDefault();
            const formData = new FormData(event.currentTarget);
            const roleIdValue = (formData.get('roleId') as string) || '';
            const lcatIdValue = (formData.get('lcatId') as string) || '';
            const year = Number(formData.get('year'));
            const month = Number(formData.get('month'));
            const requiredHours = Number(formData.get('requiredHours'));
            const roleId = roleIdValue ? Number(roleIdValue) : undefined;
            const lcatId = lcatIdValue ? Number(lcatIdValue) : undefined;

            setStaffingError(null);

            if (!roleId && !lcatId) {
              setStaffingError('Select at least a role or an LCAT to guide the recommendation.');
              return;
            }

            if (year && month && requiredHours) {
              recommendMutation.mutate({ roleId, lcatId, year, month, requiredHours });
            }
          }}
        >
          <div className="grid grid-cols-2 gap-3">
            <label className="flex flex-col text-xs font-semibold uppercase tracking-wide text-slate-500">
              Role
              <select
                name="roleId"
                className="mt-1 rounded border border-slate-200 px-2 py-1 text-sm text-slate-700"
                defaultValue=""
              >
                <option value="">Any role</option>
                {roles.map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col text-xs font-semibold uppercase tracking-wide text-slate-500">
              Labor category
              <select
                name="lcatId"
                className="mt-1 rounded border border-slate-200 px-2 py-1 text-sm text-slate-700"
                defaultValue=""
              >
                <option value="">Any LCAT</option>
                {lcats.map((lcat) => (
                  <option key={lcat.id} value={lcat.id}>
                    {lcat.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col text-xs font-semibold uppercase tracking-wide text-slate-500">
              Required hours
              <input
                name="requiredHours"
                type="number"
                min={1}
                className="mt-1 rounded border border-slate-200 px-2 py-1 text-sm text-slate-700"
                placeholder="160"
              />
            </label>
            <label className="flex flex-col text-xs font-semibold uppercase tracking-wide text-slate-500">
              Year
              <input
                name="year"
                type="number"
                min={2024}
                className="mt-1 rounded border border-slate-200 px-2 py-1 text-sm text-slate-700"
                placeholder={String(new Date().getFullYear())}
              />
            </label>
            <label className="flex flex-col text-xs font-semibold uppercase tracking-wide text-slate-500">
              Month
              <input
                name="month"
                type="number"
                min={1}
                max={12}
                className="mt-1 rounded border border-slate-200 px-2 py-1 text-sm text-slate-700"
                placeholder="9"
              />
            </label>
          </div>
          <button
            type="submit"
            disabled={recommendMutation.isPending}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {recommendMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            Suggest staffing
          </button>
        </form>
        {staffingError && (
          <div className="mt-3 flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
            <Info className="h-4 w-4" />
            {staffingError}
          </div>
        )}
        {recommendation && (
          <div className="mt-3 space-y-2 rounded-lg border border-blue-200 bg-blue-50 p-3 text-xs text-blue-700">
            <p className="font-semibold">AI Recommendations</p>
            {recommendation.candidates.length === 0 ? (
              <p>No available candidates for this window.</p>
            ) : (
              <ul className="space-y-2">
                {recommendation.candidates.map((candidate) => (
                  <li
                    key={candidate.user_id}
                    className="rounded-md border border-blue-200 bg-white px-3 py-2 text-slate-700"
                  >
                    <p className="font-semibold text-blue-700">{candidate.full_name}</p>
                    <p className="text-xs text-slate-500">
                      Current FTE {Math.round(candidate.current_fte * 100)}% · Allocated {candidate.allocated_hours}h · Available {candidate.available_hours}h
                    </p>
                  </li>
                ))}
              </ul>
            )}
            <p className="text-[11px] font-medium opacity-80">{recommendation.reasoning}</p>
          </div>
        )}
      </Card>

      <Card title="Conflict & Balance" description="Identify overloads and redistribute work with a single click.">
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <button
            type="button"
            onClick={() => conflictsMutation.mutate()}
            className="inline-flex items-center gap-1 rounded border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-700 transition hover:border-amber-300"
          >
            <TriangleAlert className="h-4 w-4" />
            Detect conflicts
          </button>
          <button
            type="button"
            onClick={() => balanceMutation.mutate()}
            className="inline-flex items-center gap-1 rounded border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 transition hover:border-emerald-300"
          >
            <Sparkles className="h-4 w-4" />
            Balance workload
          </button>
          <button
            type="button"
            onClick={() => forecastMutation.mutate()}
            className="inline-flex items-center gap-1 rounded border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 transition hover:border-blue-300"
          >
            <Sparkles className="h-4 w-4" />
            Forecast needs
          </button>
        </div>

        <div className="mt-3 space-y-3 text-xs text-slate-600">
          {conflictsMutation.isPending && <p>Checking for conflicts…</p>}
          {conflicts && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3">
              <p className="text-[11px] font-semibold text-amber-700">{conflicts.message}</p>
              {conflicts.conflicts.length > 0 && (
                <ul className="mt-2 space-y-2">
                  {conflicts.conflicts.map((conflict: ConflictDetail) => (
                    <li key={`${conflict.user_id}-${conflict.month}`} className="rounded-md border border-amber-200 bg-white px-3 py-2">
                      <p className="font-semibold text-amber-700">
                        {conflict.employee} · {conflict.month} · {(conflict.fte * 100).toFixed(1)}% FTE
                      </p>
                      <ul className="mt-1 space-y-1 text-[11px] text-slate-600">
                        {conflict.projects.map((project, index) => (
                          <li key={`${project.project_id ?? index}-${project.project_name}`}>
                            {project.project_name}: {project.hours}h
                          </li>
                        ))}
                      </ul>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
          {balanceMutation.isPending && <p>Generating balancing suggestions…</p>}
          {balance && (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
              <p className="text-[11px] font-semibold text-emerald-700">{balance.message}</p>
              {balance.suggestions.length > 0 && (
                <ul className="mt-2 space-y-2">
                  {balance.suggestions.map((suggestion: BalanceSuggestion, index) => (
                    <li key={`${suggestion.action}-${index}`} className="rounded-md border border-emerald-200 bg-white px-3 py-2">
                      <p className="text-[11px] text-slate-600">
                        Shift {suggestion.recommended_hours}h from {suggestion.from_employee ?? '—'} to {suggestion.to_employee ?? '—'} ({suggestion.action})
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
          {forecastMutation.isPending && <p>Calculating forecast…</p>}
          {forecast && (
            <div className="rounded-lg border border-blue-200 bg-blue-50 p-3">
              <p className="text-[11px] font-semibold text-blue-700">{forecast.message}</p>
              {forecast.predictions.length > 0 && (
                <ul className="mt-2 grid gap-2 text-[11px] text-slate-600">
                  {forecast.predictions.map((prediction: ForecastPrediction) => (
                    <li key={prediction.month} className="rounded-md border border-blue-200 bg-white px-3 py-2">
                      <p className="font-semibold text-blue-700">{prediction.month}</p>
                      <p>Capacity: {prediction.projected_capacity_hours}h · Allocated: {prediction.projected_allocated_hours}h</p>
                      <p>
                        Surplus: {prediction.surplus_hours}h · Status: <span className="uppercase">{prediction.risk}</span>
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}

