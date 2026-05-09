import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { FiX, FiUploadCloud, FiDownload, FiTrash2, FiEye, FiTrash } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { uploadResumes, getUserResumes, getResume, deleteResume, clearData } from '../services/api.js';

const ResumesDrawer = ({ isOpen, onClose }) => {
  const { theme } = useTheme();
  const uploadInputRef = useRef(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [clearLoading, setClearLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [processingNotice, setProcessingNotice] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [confirmDialog, setConfirmDialog] = useState(null);
  const [alert, setAlert] = useState(null);

  const drawerClassName = theme === 'dark'
    ? 'fixed right-0 top-0 z-[9998] h-full w-full max-w-md bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 border-l border-white/10 text-slate-100 shadow-2xl backdrop-blur-xl'
    : 'fixed right-0 top-0 z-[9998] h-full w-full max-w-md bg-gradient-to-b from-white via-slate-50 to-white border-l border-slate-200 text-slate-900 shadow-2xl backdrop-blur-xl';

  const panelCardClassName = theme === 'dark'
    ? 'rounded-2xl border border-white/10 bg-slate-900/70'
    : 'rounded-2xl border border-slate-200 bg-white';

  const refreshResumes = async () => {
    try {
      const data = await getUserResumes();
      setResumes(data.resumes || []);
    } catch (error) {
      console.error('Failed to fetch resumes:', error);
      setResumes([]);
    }
  };

  useEffect(() => {
    if (isOpen) {
      refreshResumes();
    }
  }, [isOpen]);

  const handleUploadClick = () => {
    uploadInputRef.current?.click();
  };

  const handleUploadChange = async (event) => {
    const input = event.target;
    const files = Array.from(input.files || []);
    if (files.length === 0) return;

    setUploadLoading(true);
    setUploadStatus('');
    setProcessingNotice({
      type: 'info',
      text: `Uploading ${files.length} resume(s). Please wait while processing completes.`,
    });

    try {
      const data = await uploadResumes(files);
      setUploadStatus(data.message || 'Processing complete.');
      setProcessingNotice({
        type: 'success',
        text: `Successfully processed ${files.length} resume(s) and ready to use!`,
      });
      setAlert({
        title: 'Upload Successful',
        message: `${files.length} resume${files.length > 1 ? 's' : ''} processed and ready to use!`,
      });
      await refreshResumes();
    } catch (error) {
      console.error('Resume upload error:', error);
      setUploadStatus(error.message || 'Upload failed.');
      setProcessingNotice({
        type: 'error',
        text: error.message || 'Resume upload failed. Please try again.',
      });
    } finally {
      setUploadLoading(false);
      input.value = '';
      setTimeout(() => setUploadStatus(''), 5000);
      setTimeout(() => setProcessingNotice(null), 6000);
    }
  };

  const handleDownload = async (fileName) => {
    try {
      const blob = await getResume(fileName);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handlePreview = async (fileName) => {
    try {
      const blob = await getResume(fileName);
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => window.URL.revokeObjectURL(url), 10000);
    } catch (error) {
      console.error('Preview failed:', error);
    }
  };

  const openConfirmDialog = (title, message, onConfirm) => {
    setConfirmDialog({ title, message, onConfirm });
  };

  const closeConfirmDialog = () => setConfirmDialog(null);

  const closeAlert = () => setAlert(null);

  const handleDelete = (fileName) => {
    openConfirmDialog(
      'Delete Resume',
      `Delete ${fileName}? This cannot be undone.`,
      async () => {
        await deleteResume(fileName);
        await refreshResumes();
      }
    );
  };

  const handleClearAll = () => {
    openConfirmDialog(
      'Clear All Data',
      'Clear ALL resumes and chat history? This cannot be undone.',
      async () => {
        setClearLoading(true);
        setUploadStatus('Deleting all resumes and chat data...');
        setProcessingNotice({
          type: 'info',
          text: 'Deleting all resumes. Please wait while the data is being removed.',
        });

        try {
          await clearData();
          setUploadStatus('All data has been deleted successfully!');
          setProcessingNotice({
            type: 'success',
            text: 'All resumes and chat history have been deleted.',
          });
          await refreshResumes();
          setTimeout(() => setUploadStatus(''), 5000);
          setTimeout(() => setProcessingNotice(null), 6000);
        } catch (error) {
          console.error('Clear all data failed:', error);
          setUploadStatus(error.message || 'Failed to delete all data.');
          setProcessingNotice({
            type: 'error',
            text: error.message || 'Failed to delete all data. Please try again.',
          });
          setTimeout(() => setUploadStatus(''), 5000);
          setTimeout(() => setProcessingNotice(null), 6000);
        } finally {
          setClearLoading(false);
        }
      }
    );
  };

  const handleConfirmAction = async () => {
    if (!confirmDialog?.onConfirm) return;
    const action = confirmDialog.onConfirm;
    closeConfirmDialog();
    await action();
  };

  return (
    <>
      {alert && createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 px-4">
          <div className={`w-full max-w-sm rounded-2xl border p-6 shadow-2xl ${theme === 'dark' ? 'bg-slate-950 border-emerald-500/40 text-slate-100' : 'bg-white border-emerald-200 text-slate-900'}`}>
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-full bg-emerald-100 dark:bg-emerald-900/30">
                <svg className="h-6 w-6 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-emerald-600 dark:text-emerald-400">{alert.title}</h3>
              </div>
            </div>
            <p className={`mt-3 text-sm leading-6 ${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>{alert.message}</p>
            <div className="mt-6 flex justify-end">
              <button
                onClick={closeAlert}
                className="px-4 py-2 rounded-xl text-sm font-medium bg-gradient-to-r from-emerald-500 to-teal-500 text-white hover:shadow-lg hover:shadow-emerald-500/30 transition-all"
              >
                Done
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}

      {isOpen && createPortal(
        <div className="fixed inset-0 z-[9997]">
          <button
            type="button"
            aria-label="Close resumes drawer"
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          />
      <aside className={`${drawerClassName} flex flex-col`}>
        <div className={`flex items-center justify-between px-5 py-4 border-b ${theme === 'dark' ? 'border-white/10' : 'border-slate-200'}`}>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <span className="text-white font-bold text-sm">HM</span>
            </div>
            <div>
              <p className={`text-xs uppercase tracking-[0.24em] ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Resume workspace</p>
              <h2 className={`text-2xl font-bold bg-gradient-to-r text-transparent bg-clip-text ${theme === 'dark' ? 'from-emerald-400 to-teal-300' : 'from-emerald-600 to-teal-500'}`}>Resumes</h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className={`p-2 rounded-full transition-colors ${theme === 'dark' ? 'hover:bg-white/10 text-slate-300' : 'hover:bg-slate-100 text-slate-700'}`}
          >
            <FiX size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar px-5 py-4 space-y-4">
          <div className={`${panelCardClassName} p-4`}> 
            <button
              onClick={handleUploadClick}
              className="flex items-center justify-center gap-3 w-full px-4 py-3 rounded-lg font-semibold bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg hover:shadow-emerald-500/30 transition-all duration-300 hover:-translate-y-0.5 active:scale-95"
              disabled={uploadLoading}
            >
              <FiUploadCloud size={20} /> {uploadLoading ? 'Uploading...' : 'Upload Resumes'}
            </button>
            <input
              ref={uploadInputRef}
              type="file"
              multiple
              accept=".pdf,.doc,.docx"
              onChange={handleUploadChange}
              className="hidden"
            />
            <p className={`mt-3 text-xs ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
              Add files here without crowding the chat sidebar.
            </p>
            {uploadLoading && (
              <div className={`mt-3 flex items-center gap-2 text-sm ${theme === 'dark' ? 'text-emerald-300' : 'text-emerald-700'}`}>
                <span className="inline-block h-4 w-4 rounded-full border-2 border-current border-r-transparent animate-spin" />
                Uploading and processing resumes...
              </div>
            )}
            {uploadStatus && <p className={`mt-3 text-sm ${theme === 'dark' ? 'text-emerald-400' : 'text-emerald-700'}`}>{uploadStatus}</p>}
            {processingNotice && (
              <div
                className={`mt-3 rounded-xl border px-3 py-2 text-sm ${processingNotice.type === 'error'
                  ? (theme === 'dark' ? 'border-red-500/40 bg-red-500/10 text-red-300' : 'border-red-200 bg-red-50 text-red-700')
                  : processingNotice.type === 'success'
                    ? (theme === 'dark' ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-emerald-200 bg-emerald-50 text-emerald-700')
                    : (theme === 'dark' ? 'border-sky-500/40 bg-sky-500/10 text-sky-300' : 'border-sky-200 bg-sky-50 text-sky-700')}`}
              >
                {processingNotice.text}
              </div>
            )}
          </div>

          <div className={`${panelCardClassName} p-4`}>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold uppercase tracking-[0.18em]">Uploaded files</h3>
              <span className={`text-xs px-2 py-1 rounded-full ${theme === 'dark' ? 'bg-white/10 text-slate-300' : 'bg-slate-200 text-slate-600'}`}>
                {resumes.length}
              </span>
            </div>

            {resumes.length === 0 ? (
              <p className={`text-sm ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>No resumes uploaded yet.</p>
            ) : (
              <ul className="space-y-2 max-h-[45vh] overflow-auto custom-scrollbar pr-1">
                {resumes.map((resume) => {
                  const name = typeof resume === 'string' ? resume : (resume.name || resume.id || JSON.stringify(resume));
                  const key = typeof resume === 'object' && resume.id ? resume.id : name;

                  return (
                    <li key={key} className={`rounded-2xl border p-3 ${theme === 'dark' ? 'border-white/10 bg-slate-950/50' : 'border-slate-200/80 bg-white'}`}>
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium">{name}</p>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <button onClick={() => handlePreview(name)} title="Preview" className={theme === 'dark' ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700'}>
                            <FiEye />
                          </button>
                          <button onClick={() => handleDownload(name)} title="Download" className={theme === 'dark' ? 'text-emerald-400 hover:text-emerald-300' : 'text-emerald-600 hover:text-emerald-700'}>
                            <FiDownload />
                          </button>
                          <button onClick={() => handleDelete(name)} title="Delete" className={theme === 'dark' ? 'text-red-400 hover:text-red-300' : 'text-red-500 hover:text-red-700'}>
                            <FiTrash2 />
                          </button>
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <button
            onClick={handleClearAll}
            disabled={clearLoading}
            className={`flex items-center justify-center gap-3 w-full px-4 py-3.5 rounded-lg font-semibold border transition-all duration-300 hover:-translate-y-0.5 active:scale-95 ${theme === 'dark' ? 'bg-gradient-to-r from-red-500/10 to-red-600/10 text-red-300 border-red-500/20 hover:bg-red-500/20' : 'bg-gradient-to-r from-red-50 to-red-100 text-red-700 border-red-200 hover:bg-red-100'}`}
          >
            <FiTrash size={20} /> {clearLoading ? 'Deleting...' : 'Clear All Data'}
          </button>
        </div>

        {confirmDialog && (
          <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 px-4">
            <div className={`w-full max-w-sm rounded-2xl border p-5 shadow-2xl ${theme === 'dark' ? 'bg-slate-950 border-white/10 text-slate-100' : 'bg-white border-slate-200 text-slate-900'}`}>
              <h3 className="text-lg font-semibold">{confirmDialog.title}</h3>
              <p className={`mt-2 text-sm leading-6 ${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>{confirmDialog.message}</p>
              <div className="mt-5 flex justify-end gap-3">
                <button
                  onClick={closeConfirmDialog}
                  className={`px-4 py-2 rounded-xl text-sm font-medium border ${theme === 'dark' ? 'border-white/10 text-slate-200 hover:bg-white/10' : 'border-slate-200 text-slate-700 hover:bg-slate-50'}`}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmAction}
                  className="px-4 py-2 rounded-xl text-sm font-medium bg-red-600 text-white hover:bg-red-700"
                >
                  Confirm
                </button>
              </div>
            </div>
          </div>
        )}
      </aside>
    </div>,
    document.body
  )}
    </>
  );
};

export default ResumesDrawer;