import { AlertCircle, Calendar, CheckCircle, TrendingDown, TrendingUp } from 'lucide-react';
import type { ForecastPrediction } from '../../types/api';

interface ForecastInsightsProps {
  predictions: ForecastPrediction[];
}

export default function ForecastInsights({ predictions }: ForecastInsightsProps) {
  if (predictions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Calendar className="h-12 w-12 text-slate-300 mb-3" />
        <p className="text-sm text-slate-500">
          Forecasting data unavailable. Ensure upcoming pipeline entries are synced.
        </p>
      </div>
    );
  }

  const getRiskConfig = (risk: string) => {
    switch (risk) {
      case 'shortage':
        return {
          icon: <AlertCircle className="h-4 w-4" />,
          label: 'Over-Allocated',
          color: 'bg-red-50 border-red-200 text-red-700',
          badgeColor: 'bg-red-100 text-red-700 border-red-300',
          iconColor: 'text-red-500'
        };
      case 'underutilized':
        return {
          icon: <TrendingDown className="h-4 w-4" />,
          label: 'Under-Utilized',
          color: 'bg-blue-50 border-blue-200 text-blue-700',
          badgeColor: 'bg-blue-100 text-blue-700 border-blue-300',
          iconColor: 'text-blue-500'
        };
      default:
        return {
          icon: <CheckCircle className="h-4 w-4" />,
          label: 'Balanced',
          color: 'bg-emerald-50 border-emerald-200 text-emerald-700',
          badgeColor: 'bg-emerald-100 text-emerald-700 border-emerald-300',
          iconColor: 'text-emerald-500'
        };
    }
  };

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto pb-2 -mx-4 px-4">
        <div className={`flex gap-3 ${predictions.length <= 3 ? '' : 'min-w-max'}`}>
          {predictions.map((prediction, idx) => {
            const riskConfig = getRiskConfig(prediction.risk);
            const utilizationPercent = prediction.projected_capacity_hours > 0
              ? (prediction.projected_allocated_hours / prediction.projected_capacity_hours) * 100
              : 0;

            return (
              <div
                key={idx}
                className={`rounded-lg border-2 p-4 ${riskConfig.color} ${predictions.length <= 3 ? 'flex-1 min-w-[240px]' : 'w-80 flex-shrink-0'}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Calendar className={`h-4 w-4 ${riskConfig.iconColor}`} />
                    <span className="font-semibold text-sm">{prediction.month}</span>
                  </div>
                  <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-semibold ${riskConfig.badgeColor}`}>
                    {riskConfig.icon}
                    {riskConfig.label}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-baseline">
                    <span className="text-xs text-slate-600">Capacity:</span>
                    <span className="text-sm font-bold text-slate-800">
                      {prediction.projected_capacity_hours.toLocaleString()}h
                    </span>
                  </div>
                  <div className="flex justify-between items-baseline">
                    <span className="text-xs text-slate-600">Allocated:</span>
                    <span className="text-sm font-bold text-slate-800">
                      {prediction.projected_allocated_hours.toLocaleString()}h
                    </span>
                  </div>
                  <div className="flex justify-between items-baseline pt-2 border-t border-slate-200">
                    <span className="text-xs font-medium text-slate-700">
                      {prediction.surplus_hours >= 0 ? 'Available:' : 'Over by:'}
                    </span>
                    <span className={`text-sm font-bold ${prediction.surplus_hours >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {Math.abs(prediction.surplus_hours).toLocaleString()}h
                    </span>
                  </div>
                </div>

                {/* Utilization Bar */}
                <div className="mt-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-slate-600">Utilization</span>
                    <span className="text-xs font-semibold text-slate-700">
                      {utilizationPercent.toFixed(0)}%
                    </span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        prediction.risk === 'shortage'
                          ? 'bg-red-500'
                          : prediction.risk === 'underutilized'
                          ? 'bg-blue-400'
                          : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(utilizationPercent, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-xs text-slate-600 mb-1">Total Capacity</div>
            <div className="text-lg font-bold text-slate-800">
              {predictions.reduce((sum, p) => sum + p.projected_capacity_hours, 0).toLocaleString()}h
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-600 mb-1">Total Allocated</div>
            <div className="text-lg font-bold text-slate-800">
              {predictions.reduce((sum, p) => sum + p.projected_allocated_hours, 0).toLocaleString()}h
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-600 mb-1">Net Balance</div>
            <div className={`text-lg font-bold ${
              predictions.reduce((sum, p) => sum + p.surplus_hours, 0) >= 0
                ? 'text-emerald-600'
                : 'text-red-600'
            }`}>
              {predictions.reduce((sum, p) => sum + p.surplus_hours, 0).toLocaleString()}h
            </div>
          </div>
        </div>
      </div>

      {/* Risk Summary */}
      <div className="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
        <div className="flex items-start gap-2">
          <TrendingUp className="h-4 w-4 text-slate-500 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-slate-600 space-y-2">
            {predictions.filter(p => p.risk === 'shortage').length > 0 && (
              <div>
                <p className="font-semibold text-red-700 mb-1">
                  ⚠️ {predictions.filter(p => p.risk === 'shortage').length} month(s) over-allocated by {Math.abs(predictions.filter(p => p.risk === 'shortage').reduce((sum, p) => sum + p.surplus_hours, 0)).toLocaleString()}h total
                </p>
                <p className="text-slate-700">
                  <strong>Actions to resolve:</strong>
                </p>
                <ul className="list-disc list-inside ml-2 space-y-0.5 text-slate-600">
                  <li>Reduce hours on lower-priority projects</li>
                  <li>Extend project timelines to spread work over more months</li>
                  <li>Defer non-critical projects to future months</li>
                  <li>If sustained: Consider hiring additional staff</li>
                </ul>
              </div>
            )}
            {predictions.filter(p => p.risk === 'underutilized').length > 0 && (
              <div>
                <p className="font-semibold text-blue-700 mb-1">
                  📊 {predictions.filter(p => p.risk === 'underutilized').length} month(s) under-utilized with {predictions.filter(p => p.risk === 'underutilized').reduce((sum, p) => sum + p.surplus_hours, 0).toLocaleString()}h available
                </p>
                <p className="text-slate-700">
                  <strong>Opportunities:</strong>
                </p>
                <ul className="list-disc list-inside ml-2 space-y-0.5 text-slate-600">
                  <li>Pursue new project opportunities</li>
                  <li>Accelerate existing project timelines</li>
                  <li>Invest in training and professional development</li>
                  <li>Plan for knowledge transfer or documentation</li>
                </ul>
              </div>
            )}
            {predictions.every(p => p.risk === 'balanced') && (
              <p>
                <span className="font-semibold text-emerald-700">✓ All months balanced.</span>{' '}
                Capacity planning is well-aligned with projected demand. Continue monitoring as plans evolve.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

