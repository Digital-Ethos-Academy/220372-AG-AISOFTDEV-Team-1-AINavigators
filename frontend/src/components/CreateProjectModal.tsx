import { Fragment, useRef, useState, useEffect, forwardRef } from 'react';
import type { InputHTMLAttributes, ButtonHTMLAttributes } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { useForm } from 'react-hook-form';
import type { SubmitHandler, FieldError } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Calendar, Loader2 } from 'lucide-react';
import { projectsService } from '../services/projects';
import type { Project } from '../types/api.types';

// ============================================================================
// TYPES & SCHEMA
// ============================================================================

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newProject: Project) => void;
}

// Zod validation schema matching backend API
const projectSchema = z.object({
  code: z
    .string()
    .min(1, 'Project Code is required')
    .regex(/^[A-Z0-9-]+$/, 'Only uppercase letters, numbers, and hyphens allowed'),
  name: z
    .string()
    .min(1, 'Project Name is required'),
  client: z
    .string()
    .min(1, 'Client Name is required'),
  start_date: z
    .string()
    .min(1, 'Start date is required')
    .refine((date) => {
      if (!date) return false;
      const inputDate = new Date(date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return inputDate >= today;
    }, {
      message: 'Start date cannot be in the past',
    }),
  sprints: z.coerce
    .number({
      required_error: "Number of sprints is required",
      invalid_type_error: "Must be a number",
    })
    .int('Must be a whole number')
    .min(1, 'Must be at least 1 sprint')
    .max(52, 'Cannot exceed 52 sprints'),
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface FormFieldProps {
  name: keyof ProjectFormData;
  label: string;
  error?: FieldError;
  helperText?: string;
  children: React.ReactNode;
}

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  isInvalid?: boolean;
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  isLoading?: boolean;
  loadingText?: string;
}

// ============================================================================
// REUSABLE UI & FORM COMPONENTS
// ============================================================================

const Button = ({
  children,
  variant = 'secondary',
  isLoading = false,
  loadingText,
  ...props
}: ButtonProps) => {
  const baseClasses = 'inline-flex justify-center items-center rounded-md px-4 py-2 text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'border-transparent bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-400',
    secondary: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50',
  };

  return (
    <button
      {...props}
      disabled={isLoading || props.disabled}
      className={`${baseClasses} ${variantClasses[variant]}`}
    >
      {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {isLoading ? loadingText || children : children}
    </button>
  );
};

const ModalHeader = ({ title, onClose }: { title: string; onClose: () => void }) => (
  <div className="flex items-start justify-between">
    <Dialog.Title as="h3" className="text-xl font-semibold leading-6 text-gray-900">
      {title}
    </Dialog.Title>
    <button
      type="button"
      onClick={onClose}
      className="rounded-md text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      <span className="sr-only">Close</span>
      <X className="h-6 w-6" aria-hidden="true" />
    </button>
  </div>
);

const ModalFooter = ({
  onCancel,
  isSubmitting,
}: {
  onCancel: () => void;
  isSubmitting: boolean;
}) => (
  <div className="mt-8 flex justify-end space-x-4">
    <Button type="button" variant="secondary" onClick={onCancel} disabled={isSubmitting}>
      Cancel
    </Button>
    <Button type="submit" variant="primary" isLoading={isSubmitting} loadingText="Creating...">
      Create Project
    </Button>
  </div>
);

const FormField = ({ name, label, error, helperText, children }: FormFieldProps) => (
  <div>
    <label htmlFor={name} className="block text-sm font-medium text-gray-700">
      {label} <span className="text-red-500">*</span>
    </label>
    <div className="mt-1 relative">
      {children}
    </div>
    {error ? (
      <p className="mt-1 text-sm text-red-600">{error.message}</p>
    ) : helperText ? (
      <p className="mt-1 text-sm text-gray-500">{helperText}</p>
    ) : null}
  </div>
);

const baseInputClasses = 'block w-full rounded-md border-0 py-2.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6';
const invalidInputClasses = 'ring-red-500 focus:ring-red-600';
const validInputClasses = 'ring-gray-300 focus:ring-blue-600';

const TextInput = forwardRef<HTMLInputElement, InputProps>(
  ({ isInvalid, ...props }, ref) => (
    <input
      type="text"
      ref={ref}
      {...props}
      className={`${baseInputClasses} ${isInvalid ? invalidInputClasses : validInputClasses}`}
      aria-invalid={isInvalid ? "true" : "false"}
    />
  )
);
TextInput.displayName = 'TextInput';

const NumberInput = forwardRef<HTMLInputElement, InputProps>(
  ({ isInvalid, ...props }, ref) => (
    <input
      type="number"
      ref={ref}
      {...props}
      className={`${baseInputClasses} ${isInvalid ? invalidInputClasses : validInputClasses}`}
      aria-invalid={isInvalid ? "true" : "false"}
    />
  )
);
NumberInput.displayName = 'NumberInput';

const DateInput = forwardRef<HTMLInputElement, InputProps>(
  ({ isInvalid, ...props }, ref) => (
    <div className="relative">
      <input
        type="date"
        ref={ref}
        {...props}
        className={`${baseInputClasses} ${isInvalid ? invalidInputClasses : validInputClasses} pr-10`}
        aria-invalid={isInvalid ? "true" : "false"}
      />
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
        <Calendar className="h-5 w-5 text-gray-400" aria-hidden="true" />
      </div>
    </div>
  )
);
DateInput.displayName = 'DateInput';

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function CreateProjectModal({ isOpen, onClose, onSuccess }: CreateProjectModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    mode: 'onSubmit',
    reValidateMode: 'onSubmit',
    criteriaMode: 'firstError',
    shouldFocusError: true,
    defaultValues: {
      code: '',
      name: '',
      client: '',
      start_date: '',
      sprints: 0,
    },
  });

  const [apiError, setApiError] = useState<string | null>(null);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      // Reset form after closing (with delay for animation)
      setTimeout(() => {
        reset();
        setApiError(null);
      }, 300);
    }
  }, [isOpen, reset]);

  const onSubmit: SubmitHandler<ProjectFormData> = async (data) => {
    setApiError(null);
    try {
      // Call API service to create project
      const newProject = await projectsService.createProject(data);
      onSuccess(newProject);
      onClose();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create the project.';
      setApiError(errorMessage);
    }
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/30" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-lg bg-white p-8 text-left align-middle shadow-xl transition-all">
                <ModalHeader title="Create New Project" onClose={onClose} />

                <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-6">
                  <FormField name="code" label="Project Code" error={errors.code} helperText="Unique identifier for this project">
                    <TextInput
                      id="code"
                      placeholder="e.g., PROJ-2025-001"
                      {...register('code')}
                      isInvalid={!!errors.code}
                    />
                  </FormField>

                  <FormField name="name" label="Project Name" error={errors.name}>
                    <TextInput
                      id="name"
                      placeholder="e.g., Customer Portal Redesign"
                      {...register('name')}
                      isInvalid={!!errors.name}
                    />
                  </FormField>

                  <FormField name="client" label="Client Name" error={errors.client}>
                    <TextInput
                      id="client"
                      placeholder="e.g., Acme Corporation"
                      {...register('client')}
                      isInvalid={!!errors.client}
                    />
                  </FormField>

                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <FormField name="start_date" label="Start Date" error={errors.start_date}>
                      <DateInput
                        id="start_date"
                        {...register('start_date')}
                        isInvalid={!!errors.start_date}
                      />
                    </FormField>

                    <FormField name="sprints" label="Number of Sprints" error={errors.sprints} helperText="Each sprint is 2 weeks.">
                      <NumberInput
                        id="sprints"
                        placeholder="e.g., 18"
                        {...register('sprints', { valueAsNumber: true })}
                        isInvalid={!!errors.sprints}
                      />
                    </FormField>
                  </div>

                  {apiError && (
                    <div className="rounded-md bg-red-50 p-4">
                      <p className="text-sm font-medium text-red-800">{apiError}</p>
                    </div>
                  )}

                  <ModalFooter onCancel={onClose} isSubmitting={isSubmitting} />
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
