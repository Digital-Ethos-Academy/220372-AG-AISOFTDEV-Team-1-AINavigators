import { Fragment, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Calendar, Loader2, Sparkles, X } from 'lucide-react';

import type { AssignmentDistributionInput, ProjectAssignment } from '../../types/api';

const monthSchema = z
  .number({ invalid_type_error: 'Enter a month (1-12)' })
  .int('Enter a whole number')
  .min(1, 'Minimum month is 1')
  .max(12, 'Maximum month is 12');

const yearSchema = z
  .number({ invalid_type_error: 'Enter a year' })
  .int('Enter a whole number')
  .min(2020, 'Year must be 2020 or later')
  .max(2050, 'Year must be before 2051');

const distributeSchema = z
  .object({
    start_year: yearSchema,
    start_month: monthSchema,
    end_year: yearSchema,
    end_month: monthSchema,
    total_hours: z
      .number({ invalid_type_error: 'Enter total hours or leave blank' })
      .int('Enter a whole number')
      .min(0, 'Hours must be non-negative')
      .optional()
      .or(z.literal('')),
    strategy: z.literal('even').optional()
  })
  .superRefine((value, ctx) => {
    const startIndex = value.start_year * 12 + value.start_month;
    const endIndex = value.end_year * 12 + value.end_month;
    if (endIndex < startIndex) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['end_month'],
        message: 'End month must be after the start month'
      });
    }
  });

type DistributeFormValues = z.infer<typeof distributeSchema>;

interface DistributeAssignmentModalProps {
  open: boolean;
  submitting: boolean;
  assignment: ProjectAssignment | null;
  defaultStart: { year: number; month: number };
  defaultEnd: { year: number; month: number };
  error?: string | null;
  onSubmit: (payload: AssignmentDistributionInput) => void;
  onClose: () => void;
}

export default function DistributeAssignmentModal({
  open,
  submitting,
  assignment,
  defaultStart,
  defaultEnd,
  error,
  onSubmit,
  onClose
}: DistributeAssignmentModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors }
  } = useForm<DistributeFormValues>({
    resolver: zodResolver(distributeSchema),
    defaultValues: {
      start_year: defaultStart.year,
      start_month: defaultStart.month,
      end_year: defaultEnd.year,
      end_month: defaultEnd.month,
      strategy: 'even'
    }
  });

  useEffect(() => {
    reset({
      start_year: defaultStart.year,
      start_month: defaultStart.month,
      end_year: defaultEnd.year,
      end_month: defaultEnd.month,
      total_hours: '',
      strategy: 'even'
    });
  }, [defaultEnd, defaultStart, reset]);

  const submitHandler = (values: DistributeFormValues) => {
    const payload: AssignmentDistributionInput = {
      start_year: values.start_year,
      start_month: values.start_month,
      end_year: values.end_year,
      end_month: values.end_month,
      strategy: 'even'
    };
    if (typeof values.total_hours === 'number') {
      payload.total_hours = values.total_hours;
    }
    onSubmit(payload);
  };

  const rangePreview = (() => {
    const startMonth = watch('start_month');
    const startYear = watch('start_year');
    const endMonth = watch('end_month');
    const endYear = watch('end_year');
    return `${String(startMonth).padStart(2, '0')}/${startYear} – ${String(endMonth).padStart(2, '0')}/${endYear}`;
  })();

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
                  <Dialog.Title className="text-lg font-semibold text-slate-900">
                    Auto-distribute hours
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
                  Spread this assignment&apos;s hours evenly across a month range. Useful when you
                  know the timeframe but don&apos;t want to type each cell.
                </p>

                {assignment && (
                  <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                    <div className="flex items-center gap-2 font-semibold text-slate-800">
                      <Sparkles className="h-4 w-4 text-blue-500" />
                      {assignment.user.full_name} · {assignment.role.name}
                    </div>
                    <p className="mt-1 text-xs text-slate-500">
                      Funded {assignment.funded_hours} hrs • Current range {rangePreview}
                    </p>
                  </div>
                )}

                {error && (
                  <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                  </div>
                )}

                <form className="mt-6 space-y-5" onSubmit={handleSubmit(submitHandler)}>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <fieldset className="space-y-2">
                      <legend className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Start (month / year)
                      </legend>
                      <div className="flex gap-3">
                        <input
                          type="number"
                          min={1}
                          max={12}
                          className={`w-20 rounded-md border px-2 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 ${
                            errors.start_month ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                          }`}
                          {...register('start_month', { valueAsNumber: true })}
                        />
                        <input
                          type="number"
                          min={2020}
                          max={2050}
                          className={`w-28 rounded-md border px-2 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 ${
                            errors.start_year ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                          }`}
                          {...register('start_year', { valueAsNumber: true })}
                        />
                      </div>
                      {(errors.start_month || errors.start_year) && (
                        <p className="text-xs text-red-600">
                          {errors.start_month?.message || errors.start_year?.message}
                        </p>
                      )}
                    </fieldset>

                    <fieldset className="space-y-2">
                      <legend className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        End (month / year)
                      </legend>
                      <div className="flex gap-3">
                        <input
                          type="number"
                          min={1}
                          max={12}
                          className={`w-20 rounded-md border px-2 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 ${
                            errors.end_month ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                          }`}
                          {...register('end_month', { valueAsNumber: true })}
                        />
                        <input
                          type="number"
                          min={2020}
                          max={2050}
                          className={`w-28 rounded-md border px-2 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 ${
                            errors.end_year ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                          }`}
                          {...register('end_year', { valueAsNumber: true })}
                        />
                      </div>
                      {(errors.end_month || errors.end_year) && (
                        <p className="text-xs text-red-600">
                          {errors.end_month?.message || errors.end_year?.message}
                        </p>
                      )}
                    </fieldset>
                  </div>

                  <div>
                    <label htmlFor="total_hours" className="text-sm font-medium text-slate-700">
                      Total hours to distribute (optional)
                    </label>
                    <input
                      id="total_hours"
                      type="number"
                      min={0}
                      placeholder="Auto-calc remaining"
                      className={`mt-2 w-full rounded-md border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 ${
                        errors.total_hours ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                      }`}
                      {...register('total_hours', {
                        setValueAs: (value) => (value === '' ? '' : Number(value))
                      })}
                    />
                    {errors.total_hours && <p className="mt-1 text-sm text-red-600">{errors.total_hours.message}</p>}
                    <p className="mt-1 text-xs text-slate-500">
                      Leave blank to use the remaining funded hours.
                    </p>
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
                      className="inline-flex items-center gap-2 rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-400"
                      disabled={submitting}
                    >
                      {submitting ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <Sparkles className="h-4 w-4" /> Distribute hours
                        </>
                      )}
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

