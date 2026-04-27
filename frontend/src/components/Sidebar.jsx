// frontend/src/components/Sidebar.jsx (UPDATED for MORE Professionalism and Colors)
import React, { useRef, useState } from 'react';
import { FiPlus, FiMessageSquare, FiUploadCloud, FiSun, FiMoon } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { uploadResumes } from '../services/api.js';

const hireMindLogo = '/hiremind-logo.png';

const Sidebar = ({ onNewChat, onChatSelect, chatSessions, onBulkUploadFiles }) => {
  const { theme, toggleTheme } = useTheme();
  const bulkUploadInputRef = useRef(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');


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
        {uploadStatus && (
          <p className="text-center text-sm mt-3 font-medium text-emerald-600 dark:text-emerald-400">
            {uploadStatus}
          </p>
        )}
      </div>
    </div>
  );
};

export default Sidebar;