import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Calendar, X } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const dateRangeSchema = z
  .object({
    startYear: z
      .number({ invalid_type_error: 'Enter a valid year' })
      .int('Year must be a whole number')
      .min(2020, 'Year must be 2020 or later')
      .max(2050, 'Year must be 2050 or earlier'),
    startMonth: z
      .number({ invalid_type_error: 'Enter a valid month' })
      .int('Month must be a whole number')
      .min(1, 'Month must be between 1 and 12')
      .max(12, 'Month must be between 1 and 12'),
    endYear: z
      .number({ invalid_type_error: 'Enter a valid year' })
      .int('Year must be a whole number')
      .min(2020, 'Year must be 2020 or later')
      .max(2050, 'Year must be 2050 or earlier'),
    endMonth: z
      .number({ invalid_type_error: 'Enter a valid month' })
      .int('Month must be a whole number')
      .min(1, 'Month must be between 1 and 12')
      .max(12, 'Month must be between 1 and 12')
  })
  .superRefine((data, ctx) => {
    // Validate that end date is after start date
    const startIndex = data.startYear * 12 + data.startMonth;
    const endIndex = data.endYear * 12 + data.endMonth;
    
    if (endIndex < startIndex) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['endMonth'],
        message: 'End date must be after start date'
      });
    }
  });

type DateRangeFormValues = z.infer<typeof dateRangeSchema>;

interface DateRangeModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: DateRangeFormValues) => void;
  defaultValues: DateRangeFormValues;
}

const MONTHS = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' }
];

export default function DateRangeModal({ open, onClose, onSubmit, defaultValues }: DateRangeModalProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<DateRangeFormValues>({
    resolver: zodResolver(dateRangeSchema),
    defaultValues
  });

  const handleFormSubmit = (data: DateRangeFormValues) => {
    onSubmit(data);
    onClose();
  };

  return (
    <Transition appear show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/30" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 shadow-xl transition-all">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-blue-600" />
                    <Dialog.Title className="text-lg font-semibold text-slate-900">
                      Select Date Range
                    </Dialog.Title>
                  </div>
                  <button
                    type="button"
                    onClick={onClose}
                    className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
                  {/* Start Date */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Start Date
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <select
                          {...register('startMonth', { valueAsNumber: true })}
                          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                        >
                          {MONTHS.map((month) => (
                            <option key={month.value} value={month.value}>
                              {month.label}
                            </option>
                          ))}
                        </select>
                        {errors.startMonth && (
                          <p className="mt-1 text-xs text-red-600">{errors.startMonth.message}</p>
                        )}
                      </div>
                      <div>
                        <input
                          type="number"
                          {...register('startYear', { valueAsNumber: true })}
                          placeholder="Year"
                          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                        />
                        {errors.startYear && (
                          <p className="mt-1 text-xs text-red-600">{errors.startYear.message}</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* End Date */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      End Date
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <select
                          {...register('endMonth', { valueAsNumber: true })}
                          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                        >
                          {MONTHS.map((month) => (
                            <option key={month.value} value={month.value}>
                              {month.label}
                            </option>
                          ))}
                        </select>
                        {errors.endMonth && (
                          <p className="mt-1 text-xs text-red-600">{errors.endMonth.message}</p>
                        )}
                      </div>
                      <div>
                        <input
                          type="number"
                          {...register('endYear', { valueAsNumber: true })}
                          placeholder="Year"
                          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                        />
                        {errors.endYear && (
                          <p className="mt-1 text-xs text-red-600">{errors.endYear.message}</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3 pt-2">
                    <button
                      type="button"
                      onClick={onClose}
                      className="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition"
                    >
                      Apply
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

