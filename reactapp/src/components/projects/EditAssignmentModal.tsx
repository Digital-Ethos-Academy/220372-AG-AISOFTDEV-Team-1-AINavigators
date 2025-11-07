import { Fragment, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Loader2, X } from 'lucide-react';

import type { LCAT, ProjectAssignment, ProjectAssignmentUpdateInput, Role } from '../../types/api';

const assignmentSchema = z.object({
  role_id: z.number({ invalid_type_error: 'Select a role' }).int(),
  lcat_id: z.number({ invalid_type_error: 'Select an LCAT' }).int(),
  funded_hours: z
    .number({ invalid_type_error: 'Enter funded hours' })
    .int('Funded hours should be a whole number')
    .min(0, 'Funded hours must be non-negative')
});

type AssignmentFormValues = z.infer<typeof assignmentSchema>;

interface EditAssignmentModalProps {
  open: boolean;
  submitting: boolean;
  assignment: ProjectAssignment | null;
  roles: Role[];
  lcats: LCAT[];
  error?: string | null;
  onSubmit: (payload: ProjectAssignmentUpdateInput) => void;
  onClose: () => void;
}

export default function EditAssignmentModal({
  open,
  submitting,
  assignment,
  roles,
  lcats,
  error,
  onSubmit,
  onClose
}: EditAssignmentModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<AssignmentFormValues>({
    resolver: zodResolver(assignmentSchema)
  });

  useEffect(() => {
    if (assignment) {
      reset({
        role_id: assignment.role_id,
        lcat_id: assignment.lcat_id,
        funded_hours: assignment.funded_hours
      });
    }
  }, [assignment, reset]);

  const submitHandler = (values: AssignmentFormValues) => {
    onSubmit(values);
  };

  return (
    <Transition show={open} as={Fragment}>
      <Dialog onClose={onClose} className="relative z-50">
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-slate-900/60" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="w-full max-w-xl transform overflow-hidden rounded-2xl bg-white p-6 shadow-xl">
                <div className="flex items-start justify-between">
                  <Dialog.Title className="text-lg font-semibold text-slate-900">
                    Edit Assignment
                  </Dialog.Title>
                  <button
                    type="button"
                    className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                    onClick={onClose}
                  >
                    <span className="sr-only">Close</span>
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <p className="mt-1 text-sm text-slate-500">
                  Update this teammate&apos;s role, labor category, or funded hours for the project.
                </p>

                {error && (
                  <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                  </div>
                )}

                <form className="mt-6 space-y-5" onSubmit={handleSubmit(submitHandler)}>
                  <div>
                    <label htmlFor="role" className="text-sm font-medium text-slate-700">
                      Role *
                    </label>
                    <select
                      id="role"
                      className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                        errors.role_id ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                      }`}
                      {...register('role_id', { valueAsNumber: true })}
                    >
                      <option value="" disabled>
                        Select role
                      </option>
                      {roles.map((role) => (
                        <option key={role.id} value={role.id}>
                          {role.name}
                        </option>
                      ))}
                    </select>
                    {errors.role_id && <p className="mt-1 text-sm text-red-600">{errors.role_id.message}</p>}
                  </div>

                  <div>
                    <label htmlFor="lcat" className="text-sm font-medium text-slate-700">
                      LCAT *
                    </label>
                    <select
                      id="lcat"
                      className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                        errors.lcat_id ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                      }`}
                      {...register('lcat_id', { valueAsNumber: true })}
                    >
                      <option value="" disabled>
                        Select LCAT
                      </option>
                      {lcats.map((lcat) => (
                        <option key={lcat.id} value={lcat.id}>
                          {lcat.name}
                        </option>
                      ))}
                    </select>
                    {errors.lcat_id && <p className="mt-1 text-sm text-red-600">{errors.lcat_id.message}</p>}
                  </div>

                  <div>
                    <label htmlFor="funded_hours" className="text-sm font-medium text-slate-700">
                      Funded Hours *
                    </label>
                    <input
                      id="funded_hours"
                      type="number"
                      min={0}
                      className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                        errors.funded_hours ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                      }`}
                      placeholder="1000"
                      {...register('funded_hours', { valueAsNumber: true })}
                    />
                    {errors.funded_hours && (
                      <p className="mt-1 text-sm text-red-600">{errors.funded_hours.message}</p>
                    )}
                  </div>

                  <div className="flex items-center justify-end gap-3 pt-4">
                    <button
                      type="button"
                      className="rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                      onClick={onClose}
                      disabled={submitting}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
                      disabled={submitting}
                    >
                      {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
                      Save changes
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}

