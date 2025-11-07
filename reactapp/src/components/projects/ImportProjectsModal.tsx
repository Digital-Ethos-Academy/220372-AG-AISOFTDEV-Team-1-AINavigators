import { Fragment, useRef, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Upload, FileSpreadsheet, Loader2, X } from 'lucide-react';

interface ImportProjectsModalProps {
  open: boolean;
  submitting: boolean;
  error?: string | null;
  onSubmit: (file: File) => void;
  onClose: () => void;
}

export default function ImportProjectsModal({ open, submitting, error, onSubmit, onClose }: ImportProjectsModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewName, setPreviewName] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewName(file.name);
    } else {
      setSelectedFile(null);
      setPreviewName('');
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) return;
    onSubmit(selectedFile);
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
                  <Dialog.Title className="text-xl font-semibold text-slate-900">
                    Import projects from Excel
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
                  Upload a workbook with <strong>Projects</strong>, <strong>Assignments</strong>, and optional
                  <strong> Allocations</strong> sheets to seed your staffing plan.
                </p>

                {error && (
                  <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                  </div>
                )}

                <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.xls"
                    className="hidden"
                    onChange={handleFileChange}
                  />

                  <div
                    className="flex cursor-pointer flex-col items-center gap-3 rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center text-sm text-slate-600 transition hover:border-blue-300 hover:bg-blue-50"
                    onClick={handleUploadClick}
                  >
                    <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                      <FileSpreadsheet className="h-7 w-7" />
                    </div>
                    {previewName ? (
                      <>
                        <p className="text-sm font-semibold text-slate-800">{previewName}</p>
                        <p className="text-xs text-slate-500">Click to choose a different file.</p>
                      </>
                    ) : (
                      <>
                        <p className="text-sm font-semibold text-slate-800">Select an Excel workbook</p>
                        <p className="text-xs text-slate-500">.xlsx files up to 10MB supported.</p>
                      </>
                    )}
                  </div>

                  <div className="rounded-xl border border-slate-200 bg-white p-4 text-xs text-slate-500">
                    <p className="font-semibold text-slate-700">Template expectations</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5">
                      <li>
                        <strong>Projects</strong> sheet: Name, Code, Client, Start Date, Sprints, Status
                      </li>
                      <li>
                        <strong>Assignments</strong> sheet: Project Code, Employee Email, Role, LCAT, Funded Hours
                      </li>
                      <li>
                        Optional <strong>Allocations</strong> sheet: Project Code, Employee Email, Year, Month, Hours
                      </li>
                    </ul>
                  </div>

                  <div className="flex items-center justify-end gap-3">
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
                      className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:cursor-not-allowed disabled:opacity-70"
                      disabled={submitting || !selectedFile}
                    >
                      {submitting ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Upload className="h-4 w-4" />
                      )}
                      Import projects
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

