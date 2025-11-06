import { Fragment, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Calendar, Trash2, X } from 'lucide-react';

interface OverrideFormValues {
  overridden_hours: number;
}

const overrideSchema = z.object({
  overridden_hours: z
    .number({ invalid_type_error: 'Enter the monthly hour total' })
    .int('Enter a whole number of hours')
    .min(40, 'Hours must be at least 40')
    .max(320, 'Hours must be less than 320')
});

interface MonthlyHoursOverrideModalProps {
  open: boolean;
  year: number;
  month: number;
  initialHours: number;
  baselineHours: number;
  submitting: boolean;
  deleting: boolean;
  overrideId?: number;
  onClose: () => void;
  onSubmit: (hours: number) => void;
  onDelete?: () => void;
}

export default function MonthlyHoursOverrideModal({
  open,
  year,
  month,
  initialHours,
  baselineHours,
  submitting,
  deleting,
  overrideId,
  onClose,
  onSubmit,
  onDelete
}: MonthlyHoursOverrideModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors }
  } = useForm<OverrideFormValues>({
    resolver: zodResolver(overrideSchema),
    defaultValues: {
      overridden_hours: initialHours
    }
  });

  useEffect(() => {
    if (open) {
      setValue('overridden_hours', initialHours, { shouldValidate: true });
    } else {
      reset();
    }
  }, [open, initialHours, reset, setValue]);

  const label = new Date(year, month - 1, 1).toLocaleDateString(undefined, {
    month: 'long',
    year: 'numeric'
  });

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
              <Dialog.Panel className="w-full max-w-lg transform overflow-hidden rounded-2xl bg-white p-6 shadow-xl">
                <div className="flex items-center justify-between">
                  <Dialog.Title className="text-lg font-semibold text-slate-900">
                    Override monthly hours
                  </Dialog.Title>
                  <button
                    type="button"
                    className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                    onClick={onClose}
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <p className="mt-1 text-sm text-slate-500">
                  Adjust the denominator used for FTE calculations in {label}. The default is based on business days.
                </p>

                <form
                  className="mt-6 space-y-5"
                  onSubmit={handleSubmit((values) => onSubmit(values.overridden_hours))}
                >
                  <div>
                    <label htmlFor="overridden_hours" className="text-sm font-medium text-slate-700">
                      Working hours for {label}
                    </label>
                    <div className="mt-2 flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                        <Calendar className="h-5 w-5" />
                      </div>
                      <input
                        id="overridden_hours"
                        type="number"
                        min={40}
                        className={`w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 ${
                          errors.overridden_hours ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-slate-200'
                        }`}
                        {...register('overridden_hours', { valueAsNumber: true })}
                      />
                    </div>
                    {errors.overridden_hours && (
                      <p className="mt-1 text-sm text-red-600">{errors.overridden_hours.message}</p>
                    )}
                  </div>

                  <div className="flex items-center justify-between rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500">
                    <div>
                      <p className="font-medium text-slate-600">Business-day baseline</p>
                      <p>{baselineHours} hours</p>
                    </div>
                    {overrideId && onDelete && (
                      <button
                        type="button"
                        onClick={onDelete}
                        className="inline-flex items-center gap-2 rounded-md border border-red-200 px-3 py-1.5 text-sm font-semibold text-red-600 transition hover:bg-red-50"
                        disabled={deleting}
                      >
                        <Trash2 className="h-4 w-4" />
                        Remove
                      </button>
                    )}
                  </div>

                  <div className="flex items-center justify-end gap-3 pt-4">
                    <button
                      type="button"
                      className="rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                      onClick={onClose}
                      disabled={submitting || deleting}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
                      disabled={submitting || deleting}
                    >
                      Save Override
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

