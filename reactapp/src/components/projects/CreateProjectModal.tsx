import { Fragment, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { CalendarDays, Loader2, X } from 'lucide-react';

import type { ProjectCreateInput } from '../../types/api';

const projectSchema = z.object({
  name: z.string().min(3, 'Project name is required'),
  code: z
    .string()
    .toUpperCase()
    .regex(/^[A-Z0-9-]+$/, 'Use uppercase letters, numbers, and hyphens only'),
  client: z.string().min(2, 'Client name must be at least 2 characters').nullable().optional(),
  start_date: z.string().min(1, 'Start date is required'),
  sprints: z
    .number({ invalid_type_error: 'Enter the number of sprints' })
    .int('Sprints must be a whole number')
    .min(1, 'At least one sprint is required')
    .max(52, 'Too many sprints for an MVP project')
});

type ProjectFormValues = z.infer<typeof projectSchema>;

interface CreateProjectModalProps {
  open: boolean;
  submitting: boolean;
  error?: string | null;
  onSubmit: (values: ProjectCreateInput) => void;
  onClose: () => void;
}

export default function CreateProjectModal({ open, submitting, error, onSubmit, onClose }: CreateProjectModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<ProjectFormValues>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      start_date: new Date().toISOString().split('T')[0],
      sprints: 12
    }
  });

  useEffect(() => {
    if (!open) {
      reset();
    }
  }, [open, reset]);

  const submitHandler = (values: ProjectFormValues) => {
    onSubmit({
      ...values,
      client: values.client ?? undefined
    });
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
                  <Dialog.Title className="text-xl font-semibold text-slate-900">Create New Project</Dialog.Title>
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
                  Capture the project basics so Priya can ditch her spreadsheet. Fields marked with * are required.
                </p>

                {error && (
                  <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                  </div>
                )}

                <form className="mt-6 space-y-5" onSubmit={handleSubmit(submitHandler)}>
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                      <label htmlFor="name" className="text-sm font-medium text-slate-700">
                        Project Name *
                      </label>
                      <input
                        id="name"
                        type="text"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.name ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        placeholder="Customer Portal Redesign"
                        {...register('name')}
                      />
                      {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>}
                    </div>

                    <div>
                      <label htmlFor="code" className="text-sm font-medium text-slate-700">
                        Project Code *
                      </label>
                      <input
                        id="code"
                        type="text"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 uppercase tracking-wide ${
                          errors.code ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        placeholder="PROJ-2025-001"
                        {...register('code')}
                      />
                      {errors.code && <p className="mt-1 text-sm text-red-600">{errors.code.message}</p>}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                      <label htmlFor="client" className="text-sm font-medium text-slate-700">
                        Client
                      </label>
                      <input
                        id="client"
                        type="text"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.client ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        placeholder="Acme Corporation"
                        {...register('client')}
                      />
                      {errors.client && <p className="mt-1 text-sm text-red-600">{errors.client.message}</p>}
                    </div>

                    <div>
                      <label htmlFor="start_date" className="text-sm font-medium text-slate-700">
                        Start Date *
                      </label>
                      <div className="relative mt-2">
                        <input
                          id="start_date"
                          type="date"
                          className={`w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                            errors.start_date ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                          }`}
                          {...register('start_date')}
                        />
                        <CalendarDays className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                      </div>
                      {errors.start_date && <p className="mt-1 text-sm text-red-600">{errors.start_date.message}</p>}
                    </div>
                  </div>

                  <div>
                    <label htmlFor="sprints" className="text-sm font-medium text-slate-700">
                      Number of Sprints *
                    </label>
                    <input
                      id="sprints"
                      type="number"
                      min={1}
                      max={52}
                      className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                        errors.sprints ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                      }`}
                      placeholder="18"
                      {...register('sprints', { valueAsNumber: true })}
                    />
                    {errors.sprints && <p className="mt-1 text-sm text-red-600">{errors.sprints.message}</p>}
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
                      Create Project
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

