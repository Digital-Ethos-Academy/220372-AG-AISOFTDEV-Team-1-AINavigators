import { useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { LogIn } from 'lucide-react';

import { createEmployee } from '../api/users';
import { useAuth } from '../context/AuthContext';
import { Card, SectionHeader } from '../components/common';
import type { SystemRole, UserCreateInput } from '../types/api';

type Mode = 'signin' | 'signup';

const allowedSignupRoles: SystemRole[] = ['PM'];

const exampleManagerAccount = {
  email: 'sarah.martinez@example.com',
  password: 'manager123 (set via API)'
};

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const { login, isLoading } = useAuth();
  const [mode, setMode] = useState<Mode>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [signupRole, setSignupRole] = useState<SystemRole>('PM');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const signUpMutation = useMutation({
    mutationFn: (payload: UserCreateInput) => createEmployee(payload),
    onSuccess: async (user) => {
      await queryClient.invalidateQueries({ queryKey: ['employees'] });
      setSuccessMessage(`Account created for ${user.full_name}. You can now sign in.`);
      setMode('signin');
      setPassword('');
      setConfirmPassword('');
      setEmail(user.email);
    },
    onError: (mutationError: unknown) => {
      if (mutationError instanceof Error) {
        setError(mutationError.message);
      } else {
        setError('Unable to create account. Try again later.');
      }
    }
  });

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      await login({ email, password });
      const redirectTo = (location.state as { from?: Location })?.from?.pathname ?? '/projects';
      navigate(redirectTo, { replace: true });
    } catch (loginError) {
      if (loginError instanceof Error) {
        setError(loginError.message);
      } else {
        setError('Unable to sign in. Try again.');
      }
    }
  };

  const handleSignup = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    const payload: UserCreateInput = {
      email: email.trim(),
      full_name: fullName.trim(),
      password,
      system_role: signupRole,
      is_active: true
    };

    await signUpMutation.mutateAsync(payload);
  };

  const headerDescription = useMemo(() => {
    if (mode === 'signin') {
      return 'Managers can monitor their assigned projects and teams.';
    }
    return 'Request portfolio access for staffing work. New accounts launch with PM permissions.';
  }, [mode]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-16">
      <div className="w-full max-w-3xl space-y-6">
        <SectionHeader
          title={mode === 'signin' ? 'Sign in to StaffAlloc' : 'Create a StaffAlloc Account'}
          description={headerDescription}
          action={
            <button
              type="button"
              onClick={() => {
                setError(null);
                setSuccessMessage(null);
                setMode(mode === 'signin' ? 'signup' : 'signin');
              }}
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-blue-200 hover:text-blue-600"
            >
              {mode === 'signin' ? 'Need an account?' : 'Already have access?'}
            </button>
          }
        />

        {mode === 'signin' ? (
          <Card className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-white">
                <LogIn className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">Example manager account</p>
                <p className="text-xs text-slate-500">
                  Email: <code className="rounded bg-slate-100 px-1 py-0.5 text-xs">{exampleManagerAccount.email}</code>
                  . Password can be set to any value in this prototype.
                </p>
              </div>
            </div>

            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Work email
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                    placeholder="you@company.com"
                  />
                </label>
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Password
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                    placeholder="Enter your password"
                  />
                </label>
                <p className="mt-1 text-xs text-slate-400">
                  Password validation is handled by the API in future releases. For now, enter any value.
                </p>
              </div>

              {error && <p className="text-xs font-semibold text-red-600">{error}</p>}
              {successMessage && <p className="text-xs font-semibold text-emerald-600">{successMessage}</p>}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isLoading ? 'Signing in…' : 'Sign in'}
              </button>
            </form>
          </Card>
        ) : (
          <Card className="space-y-4">
            <form className="space-y-4" onSubmit={handleSignup}>
              <div className="grid gap-3 md:grid-cols-2">
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Full name
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(event) => setFullName(event.target.value)}
                    className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                    placeholder="Priya Patel"
                  />
                </label>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Work email
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                    placeholder="you@company.com"
                  />
                </label>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Password
                  <input
                    type="password"
                    required
                    value={password}
                    minLength={8}
                    onChange={(event) => setPassword(event.target.value)}
                    className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                    placeholder="At least 8 characters"
                  />
                </label>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Confirm password
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    minLength={8}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                    placeholder="Repeat password"
                  />
                </label>
              </div>

              <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Access level
                <select
                  value={signupRole}
                  onChange={(event) => setSignupRole(event.target.value as SystemRole)}
                  className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                >
                  {allowedSignupRoles.map((role) => (
                    <option key={role} value={role}>
                      Project Manager
                    </option>
                  ))}
                </select>
              </label>

              {error && <p className="text-xs font-semibold text-red-600">{error}</p>}
              {signUpMutation.isSuccess && (
                <p className="text-xs font-semibold text-emerald-600">
                  Account created. Return to sign-in to access StaffAlloc.
                </p>
              )}

              <button
                type="submit"
                disabled={signUpMutation.isPending}
                className="w-full rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {signUpMutation.isPending ? 'Creating account…' : 'Create account'}
              </button>
            </form>

            <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
              <p className="font-semibold text-slate-700">Heads up</p>
              <p className="mt-1">
                New accounts are stored directly in the local SQLite database. You can review them via `/employees`. For production,
                replace this flow with the secure authentication service described in the PRD.
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

