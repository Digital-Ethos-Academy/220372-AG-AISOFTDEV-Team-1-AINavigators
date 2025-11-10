import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { AlertTriangle, Loader2, X } from 'lucide-react';

interface DeleteProjectModalProps {
  open: boolean;
  projectName: string;
  submitting: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export default function DeleteProjectModal({
  open,
  projectName,
  submitting,
  onConfirm,
  onClose
}: DeleteProjectModalProps) {
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
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 shadow-xl">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100">
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    </div>
                    <Dialog.Title className="text-lg font-semibold text-slate-900">
                      Delete Project
                    </Dialog.Title>
                  </div>
                  <button
                    type="button"
                    className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                    onClick={onClose}
                    disabled={submitting}
                  >
                    <span className="sr-only">Close</span>
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="mt-4">
                  <p className="text-sm text-slate-600">
                    Are you sure you want to delete <span className="font-semibold text-slate-900">"{projectName}"</span>?
                  </p>
                  <p className="mt-2 text-sm text-slate-600">
                    This will permanently remove the project and all associated assignments and allocations. This action cannot be undone.
                  </p>
                </div>

                <div className="mt-6 flex items-center justify-end gap-3">
                  <button
                    type="button"
                    className="rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                    onClick={onClose}
                    disabled={submitting}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="inline-flex items-center gap-2 rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-400"
                    onClick={onConfirm}
                    disabled={submitting}
                  >
                    {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
                    Delete Project
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}

