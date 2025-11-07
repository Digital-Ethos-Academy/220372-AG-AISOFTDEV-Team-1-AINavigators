import api from './client';
import type {
  BalanceSuggestionsResponse,
  ChatQueryRequest,
  ChatQueryResponse,
  ConflictsResponse,
  ForecastResponse,
  ReindexResponse,
  StaffingRecommendationRequestPayload,
  StaffingRecommendationResponse
} from '../types/api';

export async function chatWithAI(payload: ChatQueryRequest): Promise<ChatQueryResponse> {
  const { data } = await api.post<ChatQueryResponse>('/ai/chat', payload);
  return data;
}

export async function recommendStaff(
  payload: StaffingRecommendationRequestPayload
): Promise<StaffingRecommendationResponse> {
  const body: StaffingRecommendationRequestPayload = {
    project_id: payload.project_id,
    year: payload.year,
    month: payload.month,
    required_hours: payload.required_hours
  };

  if (payload.role_id) {
    body.role_id = payload.role_id;
  }
  if (payload.lcat_id) {
    body.lcat_id = payload.lcat_id;
  }

  const { data } = await api.post<StaffingRecommendationResponse>('/ai/recommend-staff', body);
  return data;
}

export async function fetchConflicts(): Promise<ConflictsResponse> {
  const { data } = await api.get<ConflictsResponse>('/ai/conflicts');
  return data;
}

export async function fetchForecast(monthsAhead = 3): Promise<ForecastResponse> {
  const { data } = await api.get<ForecastResponse>('/ai/forecast', { params: { months_ahead: monthsAhead } });
  return data;
}

export async function fetchBalanceSuggestions(
  projectId?: number
): Promise<BalanceSuggestionsResponse> {
  const { data } = await api.get<BalanceSuggestionsResponse>('/ai/balance-suggestions', {
    params: projectId ? { project_id: projectId } : undefined
  });
  return data;
}

export async function triggerReindex(): Promise<ReindexResponse> {
  const { data } = await api.post<ReindexResponse>('/ai/reindex');
  return data;
}

