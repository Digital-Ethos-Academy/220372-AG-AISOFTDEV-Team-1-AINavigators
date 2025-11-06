import api from './client';
import type { LCAT, Role } from '../types/api';

export async function fetchRoles(): Promise<Role[]> {
  const { data } = await api.get<Role[]>('/admin/roles/');
  return data;
}

export async function fetchLCATs(): Promise<LCAT[]> {
  const { data } = await api.get<LCAT[]>('/admin/lcats/');
  return data;
}

