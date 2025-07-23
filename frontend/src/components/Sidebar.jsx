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
    // Main Sidebar Container: Background, Text Color, Shadow
    <div className={`w-64 flex flex-col shadow-2xl z-10 p-4 
      ${theme === 'dark' 
        ? 'bg-hiremind-sidebar-dark text-hiremind-text-dark-primary shadow-hiremind-darkblue/50' 
        : 'bg-hiremind-sidebar-light text-hiremind-text-light-primary shadow-hiremind-darkblue/10'}`}>
      
      {/* App Name/Header */}
      <div className={`flex items-center justify-between p-3 mb-6 rounded-lg text-xl font-bold transition-all duration-300 
        ${theme === 'dark' 
          ? 'bg-hiremind-darkblue text-hiremind-beige shadow-lg' 
          : 'bg-hiremind-beige/50 text-hiremind-darkblue shadow-md'}`}>
        <div className="flex items-center gap-2"> {/* New div to hold logo and text */}
          <img src={hireMindLogo} alt="HireMind Logo" className="w-8 h-8 object-contain" /> {/* Logo added here */}
          HireMind
        </div>
        <button 
          onClick={toggleTheme} 
          className={`p-2 rounded-full transition-colors duration-300 
            ${theme === 'dark' 
              ? 'hover:bg-white/20 text-hiremind-text-dark-primary' 
              : 'hover:bg-black/10 text-hiremind-text-light-primary'}`}
          title="Toggle Theme"
        >
          {theme === 'dark' ? <FiMoon size={20} /> : <FiSun size={20} />}
        </button>
      </div>

      {/* New Chat Button */}
      <button 
        onClick={onNewChat}
        className="flex items-center justify-center gap-3 w-full px-4 py-3 mb-4 rounded-xl font-semibold shadow-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-hiremind-accent-blue focus:ring-opacity-50
          backdrop-blur-md 
          ${theme === 'dark' 
            ? 'bg-hiremind-accent-blue/40 text-black border border-hiremind-accent-blue/50 hover:bg-hiremind-accent-blue/60' 
            : 'bg-hiremind-accent-blue/20 text-hiremind-darkblue border border-hiremind-accent-blue/30 hover:bg-hiremind-accent-blue/40'}"
      >
        <FiPlus size={20} /> New Chat
      </button>

      {/* Chat History (Simplified for now) */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <h4 className={`text-sm mb-3 px-3 py-1 rounded-md 
          ${theme === 'dark' 
            ? 'text-hiremind-text-dark-secondary bg-white/5' 
            : 'text-hiremind-text-light-secondary bg-black/5'}`}>Chat History</h4>
        {chatSessions.length === 0 ? (
          <p className={`text-sm px-3 py-1 
            ${theme === 'dark' ? 'text-hiremind-text-dark-secondary' : 'text-hiremind-text-light-secondary'}`}>No recent chats.</p>
        ) : (
          chatSessions.map((session, index) => (
            <button
              key={index}
              onClick={() => onChatSelect(session.id)}
              className={`flex items-center gap-2 w-full px-3 py-2 text-left rounded-lg transition-colors duration-200 mb-2 backdrop-blur-sm 
                ${theme === 'dark' 
                  ? 'hover:bg-white/10 text-hiremind-text-dark-primary bg-white/5 border border-white/5' 
                  : 'hover:bg-black/10 text-hiremind-text-light-primary bg-black/5 border border-black/5'}`}
            >
              <FiMessageSquare size={16} /> {session.name}
            </button>
          ))
        )}
      </div>

      {/* Bulk Resume Upload */}
      <div className={`mt-auto pt-4 border-t 
        ${theme === 'dark' ? 'border-white/10' : 'border-black/10'}`}>
        <button
          onClick={handleBulkUploadClick}
          className="flex items-center justify-center gap-3 w-full px-4 py-3 rounded-xl font-semibold shadow-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-hiremind-accent-green focus:ring-opacity-50
            backdrop-blur-md 
            ${theme === 'dark' 
              ? 'bg-hiremind-accent-green/40 text-black border border-hiremind-accent-green/50 hover:bg-hiremind-accent-green/60' 
              : 'bg-hiremind-accent-green/20 text-hiremind-darkblue border border-hiremind-accent-green/30 hover:bg-hiremind-accent-green/40'}"
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
          <p className={`text-center text-sm mt-2 
            ${theme === 'dark' ? 'text-hiremind-text-dark-secondary' : 'text-hiremind-text-light-secondary'}`}>
            {uploadStatus}
          </p>
        )}
      </div>
    </div>
  );
};

export default Sidebar;