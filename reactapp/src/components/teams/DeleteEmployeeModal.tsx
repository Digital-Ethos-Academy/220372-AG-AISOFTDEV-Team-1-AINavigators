import { AlertTriangle, X } from 'lucide-react';
import type { EmployeeListItem } from '../../types/api';

interface DeleteEmployeeModalProps {
  open: boolean;
  employee: EmployeeListItem | null;
  submitting: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export default function DeleteEmployeeModal({
  open,
  employee,
  submitting,
  onConfirm,
  onClose
}: DeleteEmployeeModalProps) {
  if (!open || !employee) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="relative w-full max-w-md rounded-xl bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <h2 className="text-xl font-semibold text-slate-900">Delete Employee</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600 disabled:opacity-50"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="space-y-4 p-6">
          <p className="text-sm text-slate-600">
            Are you sure you want to delete <span className="font-semibold text-slate-900">{employee.full_name}</span>?
          </p>
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm text-amber-800">
              <strong>Warning:</strong> This action cannot be undone. All data associated with this employee,
              including their project assignments and allocations, will be permanently deleted.
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-slate-600">Email:</dt>
                <dd className="font-medium text-slate-900">{employee.email}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-600">Role:</dt>
                <dd className="font-medium text-slate-900">{employee.system_role}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-600">Status:</dt>
                <dd className="font-medium text-slate-900">{employee.is_active ? 'Active' : 'Inactive'}</dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 border-t border-slate-200 p-6">
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={submitting}
            className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Deleting...
              </>
            ) : (
              'Delete Employee'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

