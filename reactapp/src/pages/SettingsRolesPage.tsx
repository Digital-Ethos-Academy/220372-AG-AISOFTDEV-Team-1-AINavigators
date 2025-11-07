import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { CopyPlus, Pencil, Plus, Shield, Trash2 } from 'lucide-react';

import {
  createLCAT,
  createRole,
  deleteLCAT,
  deleteRole,
  fetchLCATs,
  fetchRoles,
  updateLCAT,
  updateRole
} from '../api/admin';
import type { LCAT, LCATInput, Role, RoleInput } from '../types/api';
import { Card, SectionHeader } from '../components/common';
import { useAuth } from '../context/AuthContext';
import BulkImportModal from '../components/projects/BulkImportModal';

interface RoleFormState {
  id: number | null;
  name: string;
  description: string;
}

interface LCATFormState {
  id: number | null;
  name: string;
  description: string;
}

const emptyRoleForm: RoleFormState = { id: null, name: '', description: '' };
const emptyLCATForm: LCATFormState = { id: null, name: '', description: '' };

function RoleForm({
  form,
  setForm,
  isSubmitting,
  onSubmit,
  onCancel
}: {
  form: RoleFormState;
  setForm: (value: RoleFormState) => void;
  isSubmitting: boolean;
  onSubmit: (form: RoleFormState) => Promise<void>;
  onCancel: () => void;
}) {
  return (
    <form
      className="space-y-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
      onSubmit={async (event) => {
        event.preventDefault();
        await onSubmit(form);
      }}
    >
      <div>
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Role name</label>
        <input
          required
          type="text"
          value={form.name}
          onChange={(event) => setForm({ ...form, name: event.target.value })}
          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          placeholder="e.g. Software Engineer"
        />
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Description</label>
        <textarea
          value={form.description}
          onChange={(event) => setForm({ ...form, description: event.target.value })}
          rows={2}
          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          placeholder="Optional summary to guide PMs."
        />
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {form.id ? (
            <>
              <Pencil className="h-4 w-4" />
              Update role
            </>
          ) : (
            <>
              <Plus className="h-4 w-4" />
              Create role
            </>
          )}
        </button>
        {form.id && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-700"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

function LCATForm({
  form,
  setForm,
  isSubmitting,
  onSubmit,
  onCancel
}: {
  form: LCATFormState;
  setForm: (value: LCATFormState) => void;
  isSubmitting: boolean;
  onSubmit: (form: LCATFormState) => Promise<void>;
  onCancel: () => void;
}) {
  return (
    <form
      className="space-y-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
      onSubmit={async (event) => {
        event.preventDefault();
        await onSubmit(form);
      }}
    >
      <div>
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">LCAT name</label>
        <input
          required
          type="text"
          value={form.name}
          onChange={(event) => setForm({ ...form, name: event.target.value })}
          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          placeholder="e.g. Level 2"
        />
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Description</label>
        <textarea
          value={form.description}
          onChange={(event) => setForm({ ...form, description: event.target.value })}
          rows={2}
          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          placeholder="Optional context for labor category."
        />
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {form.id ? (
            <>
              <Pencil className="h-4 w-4" />
              Update LCAT
            </>
          ) : (
            <>
              <Plus className="h-4 w-4" />
              Create LCAT
            </>
          )}
        </button>
        {form.id && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-700"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default function SettingsRolesPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const ownerId = user?.system_role === 'PM' ? user.id : undefined;

  const rolesQuery = useQuery({
    queryKey: ['roles', ownerId ?? 'all'],
    queryFn: () => fetchRoles({ ownerId, includeGlobal: true }),
    staleTime: 60_000,
    enabled: Boolean(user)
  });
  const lcatsQuery = useQuery({
    queryKey: ['lcats', ownerId ?? 'all'],
    queryFn: () => fetchLCATs({ ownerId, includeGlobal: true }),
    staleTime: 60_000,
    enabled: Boolean(user)
  });

  const [roleForm, setRoleForm] = useState<RoleFormState>(emptyRoleForm);
  const [lcatForm, setLcatForm] = useState<LCATFormState>(emptyLCATForm);
  const [isRoleBulkOpen, setRoleBulkOpen] = useState(false);
  const [isLcatBulkOpen, setLcatBulkOpen] = useState(false);
  const [roleBulkError, setRoleBulkError] = useState<string | null>(null);
  const [lcatBulkError, setLcatBulkError] = useState<string | null>(null);
  const [bulkSubmitting, setBulkSubmitting] = useState(false);

  const createRoleMutation = useMutation({
    mutationFn: (payload: RoleInput) => createRole(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setRoleForm(emptyRoleForm);
    }
  });

  const updateRoleMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: RoleInput }) => updateRole(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setRoleForm(emptyRoleForm);
    }
  });

  const deleteRoleMutation = useMutation({
    mutationFn: (roleId: number) => deleteRole(roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      if (roleForm.id) {
        setRoleForm(emptyRoleForm);
      }
    }
  });

  const createLCATMutation = useMutation({
    mutationFn: (payload: LCATInput) => createLCAT(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lcats'] });
      setLcatForm(emptyLCATForm);
    }
  });

  const updateLCATMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: LCATInput }) => updateLCAT(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lcats'] });
      setLcatForm(emptyLCATForm);
    }
  });

  const deleteLCATMutation = useMutation({
    mutationFn: (lcatId: number) => deleteLCAT(lcatId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lcats'] });
      if (lcatForm.id) {
        setLcatForm(emptyLCATForm);
      }
    }
  });

  const isCreatingRole = createRoleMutation.isPending || updateRoleMutation.isPending;
  const isCreatingLCAT = createLCATMutation.isPending || updateLCATMutation.isPending;

  const handleRoleSubmit = async (formState: RoleFormState) => {
    const payload: RoleInput = {
      name: formState.name.trim(),
      description: formState.description.trim() || undefined,
      owner_id: ownerId
    };

    if (!payload.name) return;

    if (formState.id) {
      await updateRoleMutation.mutateAsync({ id: formState.id, payload });
    } else {
      await createRoleMutation.mutateAsync(payload);
    }
  };

  const handleLCATSubmit = async (formState: LCATFormState) => {
    const payload: LCATInput = {
      name: formState.name.trim(),
      description: formState.description.trim() || undefined,
      owner_id: ownerId
    };

    if (!payload.name) return;

    if (formState.id) {
      await updateLCATMutation.mutateAsync({ id: formState.id, payload });
    } else {
      await createLCATMutation.mutateAsync(payload);
    }
  };

  const roleUsageCount = useMemo(() => rolesQuery.data?.length ?? 0, [rolesQuery.data]);
  const lcatUsageCount = useMemo(() => lcatsQuery.data?.length ?? 0, [lcatsQuery.data]);

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Roles & LCATs"
        description="Define job roles and labor categories for your projects. Use the forms below to add items individually, or click 'Bulk add' to paste many at once."
      />

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <Card
            title="Project Roles"
            description="Define the standard titles PMs select when assigning teammates to projects."
          >
            <RoleForm
              form={roleForm}
              setForm={setRoleForm}
              onSubmit={handleRoleSubmit}
              isSubmitting={isCreatingRole}
              onCancel={() => setRoleForm(emptyRoleForm)}
            />
          </Card>

          <Card
            title="Existing Roles"
            description={`${roleUsageCount} roles available to project teams`}
            action={
              <button
                type="button"
                onClick={() => {
                  setRoleBulkOpen(true);
                  setRoleBulkError(null);
                }}
                className="inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-blue-200 hover:text-blue-600"
              >
                <CopyPlus className="h-3.5 w-3.5" /> Bulk add
              </button>
            }
          >
            {rolesQuery.isLoading ? (
              <p className="text-sm text-slate-500">Loading roles…</p>
            ) : rolesQuery.isError ? (
              <p className="text-sm text-red-600">Failed to load roles.</p>
            ) : rolesQuery.data && rolesQuery.data.length > 0 ? (
              <ul className="space-y-2 text-sm">
                {rolesQuery.data.map((role: Role) => (
                  <li
                    key={role.id}
                    className="flex flex-col gap-2 rounded-lg border border-slate-200 bg-slate-50 p-3 md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <p className="font-semibold text-slate-800">{role.name}</p>
                      {role.description && <p className="text-xs text-slate-500">{role.description}</p>}
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <button
                        type="button"
                        onClick={() =>
                          setRoleForm({
                            id: role.id,
                            name: role.name,
                            description: role.description ?? ''
                          })
                        }
                        className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-2 py-1 text-xs font-semibold text-slate-600 transition hover:border-blue-200 hover:text-blue-600"
                      >
                        <Pencil className="h-3.5 w-3.5" />
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => deleteRoleMutation.mutate(role.id)}
                        disabled={deleteRoleMutation.isPending}
                        className="inline-flex items-center gap-1 rounded-md border border-red-100 px-2 py-1 text-xs font-semibold text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-70"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">No roles created yet. Add your first role above.</p>
            )}
          </Card>
        </div>

        <div className="space-y-4">
          <Card
            title="Labor Categories (LCATs)"
            description="Ensure funded hours align to the right labor category levels."
          >
            <LCATForm
              form={lcatForm}
              setForm={setLcatForm}
              onSubmit={handleLCATSubmit}
              isSubmitting={isCreatingLCAT}
              onCancel={() => setLcatForm(emptyLCATForm)}
            />
          </Card>

          <Card
            title="Existing LCATs"
            description={`${lcatUsageCount} labor categories configured`}
            action={
              <button
                type="button"
                onClick={() => {
                  setLcatBulkOpen(true);
                  setLcatBulkError(null);
                }}
                className="inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-emerald-200 hover:text-emerald-600"
              >
                <CopyPlus className="h-3.5 w-3.5" /> Bulk add
              </button>
            }
          >
            {lcatsQuery.isLoading ? (
              <p className="text-sm text-slate-500">Loading labor categories…</p>
            ) : lcatsQuery.isError ? (
              <p className="text-sm text-red-600">Failed to load labor categories.</p>
            ) : lcatsQuery.data && lcatsQuery.data.length > 0 ? (
              <ul className="space-y-2 text-sm">
                {lcatsQuery.data.map((lcat: LCAT) => (
                  <li
                    key={lcat.id}
                    className="flex flex-col gap-2 rounded-lg border border-slate-200 bg-slate-50 p-3 md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <p className="font-semibold text-slate-800">{lcat.name}</p>
                      {lcat.description && <p className="text-xs text-slate-500">{lcat.description}</p>}
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <button
                        type="button"
                        onClick={() =>
                          setLcatForm({
                            id: lcat.id,
                            name: lcat.name,
                            description: lcat.description ?? ''
                          })
                        }
                        className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-2 py-1 text-xs font-semibold text-slate-600 transition hover:border-emerald-200 hover:text-emerald-600"
                      >
                        <Pencil className="h-3.5 w-3.5" />
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => deleteLCATMutation.mutate(lcat.id)}
                        disabled={deleteLCATMutation.isPending}
                        className="inline-flex items-center gap-1 rounded-md border border-red-100 px-2 py-1 text-xs font-semibold text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-70"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">No labor categories defined yet. Start by creating one above.</p>
            )}
          </Card>
        </div>
      </section>

      <BulkImportModal
        open={isRoleBulkOpen}
        title="Bulk add roles"
        description="Paste one role name per line. Optional descriptions can follow a pipe, e.g. 'Data Scientist | Machine learning expertise'."
        placeholder={`Software Engineer | Core platform work\nUX Designer\nQA Analyst`}
        submitting={bulkSubmitting}
        error={roleBulkError}
        onSubmit={async (lines) => {
          setBulkSubmitting(true);
          setRoleBulkError(null);
          try {
            for (const line of lines) {
              const [namePart, descriptionPart] = line.split('|').map((part) => part.trim());
              if (!namePart) continue;
              await createRoleMutation.mutateAsync({
                name: namePart,
                description: descriptionPart || undefined,
                owner_id: ownerId
              });
            }
            setRoleBulkOpen(false);
          } catch (bulkError) {
            setRoleBulkError(bulkError instanceof Error ? bulkError.message : 'Failed to import roles.');
          } finally {
            setBulkSubmitting(false);
          }
        }}
        onClose={() => {
          setRoleBulkOpen(false);
          setRoleBulkError(null);
          setBulkSubmitting(false);
        }}
      />

      <BulkImportModal
        open={isLcatBulkOpen}
        title="Bulk add LCATs"
        description="Paste one labor category per line. Add optional descriptions after a pipe."
        placeholder={`Level 1 | Entry-level support\nSenior Consultant`}
        submitting={bulkSubmitting}
        error={lcatBulkError}
        onSubmit={async (lines) => {
          setBulkSubmitting(true);
          setLcatBulkError(null);
          try {
            for (const line of lines) {
              const [namePart, descriptionPart] = line.split('|').map((part) => part.trim());
              if (!namePart) continue;
              await createLCATMutation.mutateAsync({
                name: namePart,
                description: descriptionPart || undefined,
                owner_id: ownerId
              });
            }
            setLcatBulkOpen(false);
          } catch (bulkError) {
            setLcatBulkError(bulkError instanceof Error ? bulkError.message : 'Failed to import LCATs.');
          } finally {
            setBulkSubmitting(false);
          }
        }}
        onClose={() => {
          setLcatBulkOpen(false);
          setLcatBulkError(null);
          setBulkSubmitting(false);
        }}
      />
    </div>
  );
}

