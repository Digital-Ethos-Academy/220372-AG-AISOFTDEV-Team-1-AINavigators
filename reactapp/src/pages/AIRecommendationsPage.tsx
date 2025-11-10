import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Loader2, RefreshCw, Sparkles, TriangleAlert } from 'lucide-react';

import { fetchBalanceSuggestions, fetchConflicts, fetchForecast } from '../api/ai';
import type {
  BalanceSuggestionsResponse,
  ForecastResponse
} from '../types/api';
import { Card, KpiTile, SectionHeader } from '../components/common';
import { ConflictAlerts, ForecastInsights, BalanceSuggestions } from '../components/ai';
import { useAuth } from '../context/AuthContext';

export default function AIRecommendationsPage() {
  const { user } = useAuth();
  const [selectedFilter, setSelectedFilter] = useState<'All' | 'Conflicts' | 'Forecast' | 'Balance'>(
    'All'
  );
  const [forecastMonths, setForecastMonths] = useState<number>(3);

  const conflictsQuery = useQuery({
    queryKey: ['ai-conflicts', user?.id],
    queryFn: () => fetchConflicts(user?.id),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  // Always fetch 12 months of forecast data, then slice based on selected view
  const forecastQuery = useQuery({
    queryKey: ['ai-forecast', user?.id],
    queryFn: () => fetchForecast(12, user?.id),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  const balanceQuery = useQuery({
    queryKey: ['ai-balance', user?.id],
    queryFn: () => fetchBalanceSuggestions(undefined, user?.id),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  const conflicts = conflictsQuery.data;
  const forecastFull = forecastQuery.data as ForecastResponse | undefined;
  const balance = balanceQuery.data as BalanceSuggestionsResponse | undefined;

  // Track if any query is currently refreshing
  const isRefreshing = conflictsQuery.isFetching || forecastQuery.isFetching || balanceQuery.isFetching;

  // Slice forecast predictions based on selected period (no recalculation needed!)
  const forecast = forecastFull ? {
    ...forecastFull,
    forecast_period_months: forecastMonths,
    predictions: forecastFull.predictions.slice(0, forecastMonths)
  } : undefined;

  const filteredSections = useMemo(() => {
    const sections: { key: string; title: string; type: typeof selectedFilter }[] = [
      { key: 'conflicts', title: 'Conflict Alerts', type: 'Conflicts' },
      { key: 'forecast', title: 'Forecast', type: 'Forecast' },
      { key: 'balance', title: 'Workload Balance', type: 'Balance' }
    ];

    return selectedFilter === 'All'
      ? sections
      : sections.filter((section) => section.type === selectedFilter);
  }, [selectedFilter]);

  return (
    <div className="space-y-6">
      <SectionHeader
        title="AI Recommendations & Alerts"
        description="Leverage AI insights to unblock staffing decisions, resolve conflicts, and stay ahead of resourcing risks."
        action={
          <button
            type="button"
            onClick={() => {
              conflictsQuery.refetch();
              forecastQuery.refetch();
              balanceQuery.refetch();
            }}
            disabled={isRefreshing}
            className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold transition-all ${
              isRefreshing
                ? 'border-slate-300 bg-slate-100 text-slate-400 cursor-not-allowed'
                : 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100'
            }`}
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Refreshing...' : 'Refresh insights'}
          </button>
        }
      />

      <section className="grid gap-4 md:grid-cols-3">
        <KpiTile
          label="Conflicts Detected"
          value={conflicts?.conflicts?.length ?? 0}
          subLabel="Employees over 100% FTE"
          icon={<TriangleAlert className="h-5 w-5 text-amber-500" />}
        />
        <KpiTile
          label="Forecast Horizon"
          value={`${forecast?.forecast_period_months ?? 0} months`}
          subLabel="Projection window"
          icon={<Sparkles className="h-5 w-5 text-purple-500" />}
        />
        <KpiTile
          label="Workload Suggestions"
          value={balance?.suggestions?.length ?? 0}
          subLabel="AI proposals to smooth utilization"
          icon={<RefreshCw className="h-5 w-5 text-emerald-500" />}
        />
      </section>

      <Card>
        <div className="flex flex-wrap items-center gap-2 text-sm">
          {['All', 'Conflicts', 'Forecast', 'Balance'].map((filter) => (
            <button
              key={filter}
              type="button"
              onClick={() => setSelectedFilter(filter as typeof selectedFilter)}
              className={`rounded-full px-3 py-1 font-semibold ${
                selectedFilter === filter
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'border border-slate-200 bg-white text-slate-600'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
      </Card>

      {filteredSections.map((section) => {
        switch (section.key) {
          case 'conflicts':
            return (
              <Card
                key={section.key}
                title="Conflict Alerts"
                description="Identify over-allocations and proposed resolutions."
              >
                {conflictsQuery.isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
                  </div>
                ) : conflicts?.conflicts ? (
                  <ConflictAlerts conflicts={conflicts.conflicts} />
                ) : null}
              </Card>
            );

          case 'forecast':
            return (
              <Card
                key={section.key}
                title="Forecast Insights"
                description="Projection of staffing surpluses and shortages based on planned projects."
              >
                <div className="mb-4 flex items-center justify-between">
                  <label className="flex items-center gap-2 text-sm text-slate-600">
                    <span className="font-medium">Forecast Period:</span>
                    <select
                      value={forecastMonths}
                      onChange={(e) => setForecastMonths(Number(e.target.value))}
                      className="rounded-lg border border-slate-300 bg-white px-3 py-1 text-sm font-semibold text-slate-700 hover:border-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    >
                      <option value={3}>3 months</option>
                      <option value={6}>6 months</option>
                      <option value={9}>9 months</option>
                      <option value={12}>12 months</option>
                    </select>
                  </label>
                </div>
                {forecastQuery.isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
                  </div>
                ) : forecast?.predictions ? (
                  <ForecastInsights predictions={forecast.predictions} />
                ) : null}
              </Card>
            );

          case 'balance':
            return (
              <Card
                key={section.key}
                title="Workload Balancing Suggestions"
                description="Recommendations to redistribute work and prevent burnout."
              >
                {balanceQuery.isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
                  </div>
                ) : balance?.suggestions ? (
                  <BalanceSuggestions suggestions={balance.suggestions} />
                ) : null}
              </Card>
            );

          default:
            return null;
        }
      })}
    </div>
  );
}

