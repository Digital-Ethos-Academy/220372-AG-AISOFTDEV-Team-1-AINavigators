import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  createMonthlyHourOverride,
  deleteMonthlyHourOverride,
  fetchProjectDetail,
  updateMonthlyHourOverride
} from '../api/projects';
import type { MonthlyHourOverrideInput, ProjectWithDetails } from '../types/api';

const PROJECT_QUERY_KEY = 'project';

export function useProjectDetail(projectId: number) {
  return useQuery<ProjectWithDetails, Error>({
    queryKey: [PROJECT_QUERY_KEY, projectId],
    queryFn: () => fetchProjectDetail(projectId),
    staleTime: 60_000
  });
}

export function useMonthlyOverrideMutations(projectId: number) {
  const queryClient = useQueryClient();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: [PROJECT_QUERY_KEY, projectId] });

  const create = useMutation({
    mutationFn: (payload: MonthlyHourOverrideInput) => createMonthlyHourOverride(payload),
    onSuccess: invalidate
  });

  const update = useMutation({
    mutationFn: ({ overrideId, overridden_hours }: { overrideId: number; overridden_hours: number }) =>
      updateMonthlyHourOverride(overrideId, overridden_hours),
    onSuccess: invalidate
  });

  const remove = useMutation({
    mutationFn: (overrideId: number) => deleteMonthlyHourOverride(overrideId),
    onSuccess: invalidate
  });

  return { create, update, remove };
}

