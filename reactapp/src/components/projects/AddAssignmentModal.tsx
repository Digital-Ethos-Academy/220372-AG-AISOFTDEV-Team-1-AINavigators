import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Loader2, UserPlus, X } from 'lucide-react';

import type { EmployeeListItem, LCAT, ProjectAssignmentCreateInput, Role } from '../../types/api';

const assignmentSchema = z.object({
  user_id: z.number({ invalid_type_error: 'Select an employee' }).int(),
  role_id: z.number({ invalid_type_error: 'Select a role' }).int(),
  lcat_id: z.number({ invalid_type_error: 'Select an LCAT' }).int(),
  funded_hours: z
    .number({ invalid_type_error: 'Enter funded hours' })
    .int('Funded hours should be a whole number')
    .min(0, 'Funded hours must be non-negative')
});

type AssignmentFormValues = z.infer<typeof assignmentSchema>;

interface AddAssignmentModalProps {
  open: boolean;
  submitting: boolean;
  projectId: number;
  employees: EmployeeListItem[];
  roles: Role[];
  lcats: LCAT[];
  onClose: () => void;
  onSubmit: (payload: ProjectAssignmentCreateInput) => void;
  error?: string | null;
}

export default function AddAssignmentModal({
  open,
  submitting,
  projectId,
  employees,
  roles,
  lcats,
  onClose,
  onSubmit,
  error
}: AddAssignmentModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<AssignmentFormValues>({
    resolver: zodResolver(assignmentSchema)
  });

  const submitHandler = (values: AssignmentFormValues) => {
    onSubmit({
      project_id: projectId,
      ...values
    });
    reset();
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
              <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 shadow-xl">
                <div className="flex items-center justify-between">
                  <Dialog.Title className="text-lg font-semibold text-slate-900">
                    Add Team Member to Project
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
                  Select an employee, assign their Role and LCAT, and set their funded hours for this project.
                </p>

                {error && (
                  <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                  </div>
                )}

                <form className="mt-6 space-y-5" onSubmit={handleSubmit(submitHandler)}>
                  <div>
                    <label htmlFor="user_id" className="text-sm font-medium text-slate-700">
                      Employee *
                    </label>
                    <select
                      id="user_id"
                      className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                        errors.user_id ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                      }`}
                      defaultValue=""
                      {...register('user_id', { valueAsNumber: true })}
                    >
                      <option value="" disabled>
                        Choose an employee
                      </option>
                      {employees.map((employee) => (
                        <option key={employee.id} value={employee.id}>
                          {employee.full_name} · {employee.email}
                        </option>
                      ))}
                    </select>
                    {errors.user_id && <p className="mt-1 text-sm text-red-600">{errors.user_id.message}</p>}
                  </div>

                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                      <label htmlFor="role_id" className="text-sm font-medium text-slate-700">
                        Role *
                      </label>
                      <select
                        id="role_id"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.role_id ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        defaultValue=""
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
                      <label htmlFor="lcat_id" className="text-sm font-medium text-slate-700">
                        LCAT *
                      </label>
                      <select
                        id="lcat_id"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.lcat_id ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        defaultValue=""
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

                  <div className="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500">
                    <p className="flex items-center gap-2 font-medium text-slate-600">
                      <UserPlus className="h-4 w-4" />
                      Helpful tips
                    </p>
                    <ul className="mt-2 list-disc space-y-1 pl-5">
                      <li>Funded hours represent the budget cap for this project.</li>
                      <li>We’ll alert you if allocations exceed the funded total or 100% FTE.</li>
                    </ul>
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
                      Add Assignment
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

