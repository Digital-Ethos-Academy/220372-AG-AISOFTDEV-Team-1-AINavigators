import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren
} from 'react';

import { login as apiLogin } from '../api/auth';
import type { EmployeeListItem, SystemRole } from '../types/api';

interface AuthState {
  user: EmployeeListItem | null;
  token: string | null;
  isLoading: boolean;
  login: (params: { email: string; password: string }) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: SystemRole[]) => boolean;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

const STORAGE_KEY = 'staffalloc-auth';

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<EmployeeListItem | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as { user: EmployeeListItem; token: string | null };
        setUser(parsed.user ?? null);
        setToken(parsed.token ?? null);
      }
    } catch (error) {
      console.warn('Failed to restore auth session', error);
      localStorage.removeItem(STORAGE_KEY);
    } finally {
      setLoading(false);
    }
  }, []);

  const persist = useCallback((nextUser: EmployeeListItem | null, nextToken: string | null) => {
    if (!nextUser) {
      localStorage.removeItem(STORAGE_KEY);
      return;
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ user: nextUser, token: nextToken }));
  }, []);

  const login = useCallback(
    async ({ email, password }: { email: string; password: string }) => {
      setLoading(true);
      try {
        const response = await apiLogin({ email, password });
        setUser(response.user);
        setToken(null);
        persist(response.user, null);
      } finally {
        setLoading(false);
      }
    },
    [persist]
  );

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    persist(null, null);
  }, [persist]);

  const hasRole = useCallback(
    (...roles: SystemRole[]) => {
      if (!user) return false;
      if (roles.length === 0) return true;
      return roles.includes(user.system_role);
    },
    [user]
  );

  const value = useMemo(
    () => ({
      user,
      token,
      isLoading,
      login,
      logout,
      hasRole
    }),
    [user, token, isLoading, login, logout, hasRole]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

