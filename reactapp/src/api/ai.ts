import api from './client';
import type {
  BalanceSuggestionsResponse,
  ChatQueryRequest,
  ChatQueryResponse,
  ConflictsResponse,
  ForecastResponse,
  ReindexResponse
} from '../types/api';

export async function chatWithAI(payload: ChatQueryRequest): Promise<ChatQueryResponse> {
  const { data } = await api.post<ChatQueryResponse>('/ai/chat', payload);
  return data;
}

export async function fetchConflicts(managerId?: number): Promise<ConflictsResponse> {
  const { data } = await api.get<ConflictsResponse>('/ai/conflicts', {
    params: managerId ? { manager_id: managerId } : undefined
  });
  return data;
}

export async function fetchForecast(monthsAhead = 3, managerId?: number): Promise<ForecastResponse> {
  const { data } = await api.get<ForecastResponse>('/ai/forecast', { 
    params: { 
      months_ahead: monthsAhead,
      ...(managerId ? { manager_id: managerId } : {})
    } 
  });
  return data;
}

export async function fetchBalanceSuggestions(
  projectId?: number,
  managerId?: number
): Promise<BalanceSuggestionsResponse> {
  const { data } = await api.get<BalanceSuggestionsResponse>('/ai/balance-suggestions', {
    params: { 
      ...(projectId ? { project_id: projectId } : {}),
      ...(managerId ? { manager_id: managerId } : {})
    }
  });
  return data;
}

export async function triggerReindex(): Promise<ReindexResponse> {
  const { data } = await api.post<ReindexResponse>('/ai/reindex');
  return data;
}

