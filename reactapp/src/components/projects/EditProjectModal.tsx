import { Fragment, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Loader2, X } from 'lucide-react';

import type { Project, ProjectUpdateInput, ProjectStatus } from '../../types/api';

const projectStatusOptions: ProjectStatus[] = ['Planning', 'Active', 'On Hold', 'Closed'];

const projectSchema = z.object({
  name: z.string().min(3, 'Project name is required'),
  code: z
    .string()
    .toUpperCase()
    .regex(/^[A-Z0-9-]+$/, 'Use uppercase letters, numbers, and hyphens only'),
  client: z.string().nullable().optional(),
  start_date: z.string().min(1, 'Start date is required'),
  sprints: z
    .number({ invalid_type_error: 'Enter the number of sprints' })
    .int('Sprints must be a whole number')
    .min(1, 'At least one sprint is required')
    .max(104, 'That is a very long project – please review.'),
  status: z.enum(['Planning', 'Active', 'On Hold', 'Closed'])
});

type ProjectFormValues = z.infer<typeof projectSchema>;

interface EditProjectModalProps {
  open: boolean;
  submitting: boolean;
  project: Project | null;
  error?: string | null;
  onSubmit: (values: ProjectUpdateInput) => void;
  onClose: () => void;
}

export default function EditProjectModal({
  open,
  submitting,
  project,
  error,
  onSubmit,
  onClose
}: EditProjectModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<ProjectFormValues>({
    resolver: zodResolver(projectSchema)
  });

  useEffect(() => {
    if (project) {
      reset({
        name: project.name,
        code: project.code,
        client: project.client ?? '',
        start_date: project.start_date.slice(0, 10),
        sprints: project.sprints,
        status: project.status
      });
    }
  }, [project, reset]);

  const submitHandler = (values: ProjectFormValues) => {
    onSubmit({
      ...values,
      client: values.client || undefined
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
                  <Dialog.Title className="text-xl font-semibold text-slate-900">Edit Project</Dialog.Title>
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
                  Update the project basics, timeline, or status. Changes apply immediately across dashboards.
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
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm uppercase tracking-wide focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
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
                    </div>

                    <div>
                      <label htmlFor="status" className="text-sm font-medium text-slate-700">
                        Status *
                      </label>
                      <select
                        id="status"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.status ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        {...register('status')}
                      >
                        {projectStatusOptions.map((statusOption) => (
                          <option key={statusOption} value={statusOption}>
                            {statusOption}
                          </option>
                        ))}
                      </select>
                      {errors.status && <p className="mt-1 text-sm text-red-600">{errors.status.message}</p>}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                      <label htmlFor="start_date" className="text-sm font-medium text-slate-700">
                        Start Date *
                      </label>
                      <input
                        id="start_date"
                        type="date"
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.start_date ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        {...register('start_date')}
                      />
                      {errors.start_date && <p className="mt-1 text-sm text-red-600">{errors.start_date.message}</p>}
                    </div>

                    <div>
                      <label htmlFor="sprints" className="text-sm font-medium text-slate-700">
                        Number of Sprints *
                      </label>
                      <input
                        id="sprints"
                        type="number"
                        min={1}
                        max={104}
                        className={`mt-2 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.sprints ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        placeholder="18"
                        {...register('sprints', { valueAsNumber: true })}
                      />
                      {errors.sprints && <p className="mt-1 text-sm text-red-600">{errors.sprints.message}</p>}
                    </div>
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

