import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Loader2, X } from 'lucide-react';

import type { SystemRole, UserCreateInput } from '../../types/api';

const employeeSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  full_name: z.string().min(2, 'Full name is required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  system_role: z.enum(['Employee', 'PM', 'Admin']),
  is_active: z.boolean()
});

type EmployeeFormValues = z.infer<typeof employeeSchema>;

interface AddEmployeeModalProps {
  open: boolean;
  submitting: boolean;
  managerId: number;
  error?: string | null;
  onSubmit: (values: UserCreateInput) => void;
  onClose: () => void;
}

export default function AddEmployeeModal({
  open,
  submitting,
  managerId,
  error,
  onSubmit,
  onClose
}: AddEmployeeModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<EmployeeFormValues>({
    resolver: zodResolver(employeeSchema),
    defaultValues: {
      system_role: 'Employee',
      is_active: true
    }
  });

  const submitHandler = (values: EmployeeFormValues) => {
    onSubmit({
      ...values,
      manager_id: managerId
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
                <div className="flex items-start justify-between">
                  <Dialog.Title className="text-xl font-semibold text-slate-900">Add Employee</Dialog.Title>
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
                  Create a new employee account. They will be assigned to you as their manager.
                </p>

                {error && (
                  <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                  </div>
                )}

                <form className="mt-6 space-y-5" onSubmit={handleSubmit(submitHandler)}>
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                      <label htmlFor="full_name" className="text-sm font-medium text-slate-700">
                        Full Name *
                      </label>
                      <input
                        id="full_name"
                        type="text"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.full_name ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        placeholder="John Smith"
                        {...register('full_name')}
                      />
                      {errors.full_name && <p className="mt-1 text-sm text-red-600">{errors.full_name.message}</p>}
                    </div>

                    <div>
                      <label htmlFor="email" className="text-sm font-medium text-slate-700">
                        Email Address *
                      </label>
                      <input
                        id="email"
                        type="email"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.email ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        placeholder="john.smith@company.com"
                        {...register('email')}
                      />
                      {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                      <label htmlFor="password" className="text-sm font-medium text-slate-700">
                        Initial Password *
                      </label>
                      <input
                        id="password"
                        type="password"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.password ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        placeholder="Min 8 characters"
                        {...register('password')}
                      />
                      {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}
                    </div>

                    <div>
                      <label htmlFor="system_role" className="text-sm font-medium text-slate-700">
                        System Role *
                      </label>
                      <select
                        id="system_role"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.system_role ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        {...register('system_role')}
                      >
                        <option value="Employee">Employee (Team Member)</option>
                        <option value="PM">PM (Project Manager)</option>
                        <option value="Admin">Admin (Full Access)</option>
                      </select>
                      {errors.system_role && <p className="mt-1 text-sm text-red-600">{errors.system_role.message}</p>}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <input
                      id="is_active"
                      type="checkbox"
                      className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-200"
                      {...register('is_active')}
                    />
                    <label htmlFor="is_active" className="text-sm font-medium text-slate-700">
                      Account is active
                    </label>
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
                      Create employee
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

