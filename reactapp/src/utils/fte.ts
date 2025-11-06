export function calculateFte(allocatedHours: number, standardHours: number): number {
  if (standardHours <= 0) return 0;
  return allocatedHours / standardHours;
}

export function formatFtePercentage(allocatedHours: number, standardHours: number): string {
  const fte = calculateFte(allocatedHours, standardHours);
  return `${Math.round(fte * 100)}%`;
}

export function getHeatmapClass(fte: number): string {
  if (fte === 0) return 'bg-slate-50';
  if (fte > 1) return 'bg-red-100 text-red-700';
  if (fte === 1) return 'bg-yellow-100 text-yellow-700';
  if (fte >= 0.81) return 'bg-green-500/20 text-green-800';
  if (fte >= 0.41) return 'bg-green-400/10 text-green-700';
  if (fte >= 0.01) return 'bg-emerald-50 text-emerald-700';
  return 'bg-slate-50';
}

