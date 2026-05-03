// frontend/src/components/Sidebar.jsx (UPDATED for MORE Professionalism and Colors)
import React, { useRef, useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { FiPlus, FiMessageSquare, FiUploadCloud, FiSun, FiMoon, FiDownload, FiTrash2, FiEye, FiTrash } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { uploadResumes, getUserResumes, getResume, deleteResume, downloadResumes, clearCollections } from '../services/api.js';

const hireMindLogo = '/hiremind-logo.png';

const Sidebar = ({ onNewChat, onChatSelect, chatSessions, onBulkUploadFiles }) => {
  const { theme, toggleTheme } = useTheme();
  const bulkUploadInputRef = useRef(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [resumes, setResumes] = useState([]);
  const [confirmDialog, setConfirmDialog] = useState(null);


  const handleBulkUploadClick = () => {
    bulkUploadInputRef.current.click();
  };

  const handleBulkFileChange = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploadLoading(true);
    setUploadStatus('Uploading and processing...');

    try {
      const data = await uploadResumes(files);
      if (data.message) {
        setUploadStatus(data.message);
        // Refresh list after successful upload
        fetchResumes();
      } else {
        setUploadStatus(data.error || 'Upload failed.');
      }
    } catch (error) {
      console.error('Bulk upload error:', error);
      setUploadStatus('Network error during upload.');
    } finally {
      setUploadLoading(false);
      e.target.value = ''; // Clear input
      setTimeout(() => setUploadStatus(''), 5000); // Clear status after 5 seconds
    }
  };

  const fetchResumes = async () => {
    try {
      const data = await getUserResumes();
      setResumes(data.resumes || []);
    } catch (err) {
      console.error('Failed to fetch resumes:', err);
      setResumes([]);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleDownload = async (fileName) => {
    try {
      const blob = await getResume(fileName);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const handlePreview = async (fileName) => {
    try {
      const blob = await getResume(fileName);
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      // Optionally revoke after some time
      setTimeout(() => window.URL.revokeObjectURL(url), 10000);
    } catch (err) {
      console.error('Preview failed:', err);
    }
  };

  const closeConfirmDialog = () => setConfirmDialog(null);

  const openConfirmDialog = (title, message, onConfirm) => {
    setConfirmDialog({ title, message, onConfirm });
  };

  const handleDelete = (fileName) => {
    openConfirmDialog(
      'Delete Resume',
      `Delete ${fileName}? This cannot be undone.`,
      async () => {
        try {
          await deleteResume(fileName);
          fetchResumes();
        } catch (err) {
          console.error('Delete failed:', err);
        }
      }
    );
  };

  const handleClearAll = () => {
    openConfirmDialog(
      'Clear All Data',
      'Clear ALL resumes and chat history? This cannot be undone.',
      async () => {
        try {
          await clearCollections();
          setUploadStatus('Collections cleared successfully!');
          fetchResumes();
          setTimeout(() => setUploadStatus(''), 5000);
        } catch (err) {
          console.error('Clear collections failed:', err);
          setUploadStatus('Failed to clear collections.');
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
    <div className="w-64 flex flex-col shadow-2xl z-10 p-5 bg-white/60 dark:bg-[#0A1118]/80 backdrop-blur-3xl text-slate-800 dark:text-slate-100 border-r border-slate-200/50 dark:border-white/5 transition-colors duration-300">

      {/* App Name/Header */}
      <div className="flex items-center justify-between p-3 mb-8 rounded-2xl text-xl font-bold transition-all duration-300 bg-white/50 dark:bg-black/40 shadow-[0_4px_20px_rgb(0,0,0,0.05)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.4)] border border-slate-200/50 dark:border-white/10">
        <div className="flex items-center gap-2">
          <img src={hireMindLogo} alt="HireMind Logo" className="w-8 h-8 object-contain drop-shadow-sm" />
          <span className="bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-300 text-transparent bg-clip-text">HireMind</span>
        </div>
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full transition-all duration-300 hover:bg-slate-200/50 dark:hover:bg-white/10 active:scale-95 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
          title="Toggle Theme"
        >
          {theme === 'dark' ? <FiMoon size={20} /> : <FiSun size={20} />}
        </button>
      </div>

      {/* Bulk Resume Upload */}
      {/* User Resumes List */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold mb-2">Your Resumes</h4>
        {resumes.length === 0 ? (
          <p className="text-xs text-slate-500">No resumes uploaded yet.</p>
        ) : (
          <ul className="space-y-2 max-h-48 overflow-auto">
            {resumes.map((r) => {
              const name = typeof r === 'string' ? r : (r.name || r.id || JSON.stringify(r));
              const key = (typeof r === 'object' && r.id) ? r.id : name;
              return (
                <li key={key} className="flex items-center justify-between gap-2">
                  <span className="text-sm truncate">{name}</span>
                  <div className="flex items-center gap-2 ml-2">
                    <button onClick={() => handlePreview(name)} title="Preview" className="text-slate-500 hover:text-slate-700">
                      <FiEye />
                    </button>
                    <button onClick={() => handleDownload(name)} title="Download" className="text-emerald-600 hover:text-emerald-800">
                      <FiDownload />
                    </button>
                    <button onClick={() => handleDelete(name)} title="Delete" className="text-red-500 hover:text-red-700">
                      <FiTrash2 />
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
      <div className="mt-auto pt-5 border-t border-slate-200/50 dark:border-white/10">
        <button
          onClick={handleBulkUploadClick}
          className="flex items-center justify-center gap-3 w-full px-4 py-3.5 rounded-2xl font-semibold shadow-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transform hover:-translate-y-0.5 active:scale-95 bg-gradient-to-br from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/20 hover:bg-emerald-500/20 dark:hover:bg-emerald-500/30"
          disabled={uploadLoading}
        >
          <FiUploadCloud size={20} /> {uploadLoading ? 'Uploading...' : 'Bulk Resume Upload'}
          <input
            type="file"
            multiple
            accept=".pdf,.doc,.docx"
            ref={bulkUploadInputRef}
            onChange={handleBulkFileChange}
            className="hidden"
          />
        </button>
        <button
          onClick={handleClearAll}
          className="flex items-center justify-center gap-3 w-full px-4 py-3.5 mt-3 rounded-2xl font-semibold shadow-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-red-500/50 transform hover:-translate-y-0.5 active:scale-95 bg-gradient-to-br from-red-500/10 to-red-600/10 dark:from-red-500/20 dark:to-red-600/20 text-red-700 dark:text-red-300 border border-red-500/20 hover:bg-red-500/20 dark:hover:bg-red-500/30"
        >
          <FiTrash size={20} /> Clear All
        </button>
        {uploadStatus && (
          <p className="text-center text-sm mt-3 font-medium text-emerald-600 dark:text-emerald-400">
            {uploadStatus}
          </p>
        )}
      </div>

      {confirmDialog && createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/55 backdrop-blur-sm px-4">
          <div className={`w-full max-w-md rounded-none border shadow-2xl p-6 ${theme === 'dark' ? 'bg-slate-950 border-slate-700 text-slate-100' : 'bg-white border-slate-300 text-slate-900'}`}>
            <h3 className="text-lg font-semibold">{confirmDialog.title}</h3>
            <p className={`mt-3 text-sm leading-6 ${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>
              {confirmDialog.message}
            </p>
            <div className="mt-6 flex items-center justify-end gap-3">
              <button
                onClick={closeConfirmDialog}
                className="px-4 py-2 rounded-none border border-slate-300 bg-transparent text-sm font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-200 dark:hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmAction}
                className="px-4 py-2 rounded-none border border-red-500 bg-red-600 text-sm font-medium text-white hover:bg-red-700"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default Sidebar;