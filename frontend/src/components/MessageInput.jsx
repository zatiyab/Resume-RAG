// frontend/src/components/MessageInput.jsx (updated)
import React, { useState, useRef, useEffect } from 'react';
import { FiPlus, FiSend } from 'react-icons/fi';
import { IoDocumentTextOutline, IoSearchOutline } from 'react-icons/io5'; // Not used in this component, but if needed elsewhere
import { FaSlidersH } from 'react-icons/fa';
import { useTheme } from '../contexts/ThemeContext.jsx'; // Make sure .jsx extension is here

const MessageInput = ({ onSendMessage, onUploadFiles, isSending }) => {
  const { theme } = useTheme(); // Get current theme
  const [query, setQuery] = useState('');
  const [jdText, setJdText] = useState('');
  const [kValue, setKValue] = useState(5);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [query, jdText]);

  const handleSend = () => {
    if (query.trim()) {
      onSendMessage(query.trim(), false, kValue); // isJDSearch = false
      setQuery('');
    } else if (jdText.trim()) {
      onSendMessage(jdText.trim(), true, kValue); // isJDSearch = true
      setJdText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      onUploadFiles(files);
      e.target.value = ''; // Clear input
    }
  };

  return (
    <div className="p-3 md:p-4 rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.4)] backdrop-blur-2xl bg-white/70 dark:bg-slate-900/70 border border-slate-200/50 dark:border-slate-700/50 transition-all duration-300">
      <div className="relative flex items-end gap-3 max-w-4xl mx-auto">
        {/* Attachment button */}
        <button
          onClick={handleFileUploadClick}
          className="p-3 rounded-full flex-shrink-0 transition-all duration-300 bg-slate-100 hover:bg-slate-200 text-slate-600 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-300 border border-transparent dark:border-white/5 active:scale-95"
          disabled={isSending}
          title="Upload JD or Resumes"
        >
          <FiPlus size={22} />
          <input
            type="file"
            multiple
            accept=".pdf,.doc,.docx"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
          />
        </button>

        {/* Textarea for General Query / JD */}
        <textarea
          ref={textareaRef}
          value={query || jdText}
          onChange={(e) => {
            if (e.target.value.includes("Job Description") || e.target.value.length > 100) {
              setJdText(e.target.value);
              setQuery('');
            } else {
              setQuery(e.target.value);
              setJdText('');
            }
          }}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question or paste Job Description..."
          rows="1"
          className="flex-1 p-3.5 px-5 rounded-3xl resize-none outline-none transition-all duration-300 custom-scrollbar max-h-32 overflow-y-auto bg-white/50 focus:bg-white dark:bg-slate-950/50 dark:focus:bg-slate-900 focus:ring-2 focus:ring-emerald-500/50 text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 border border-slate-200/50 dark:border-white/5 shadow-inner"
          disabled={isSending}
        />
        
        {/* K-value slider and display */}
        <div className="flex items-center rounded-2xl p-2 px-4 flex-shrink-0 w-28 sm:w-36 md:w-44 transition-colors duration-300 bg-slate-100/50 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 border border-slate-200/50 dark:border-white/5">
            <FaSlidersH className="mr-2 flex-shrink-0 opacity-70" />
            <span className="flex-shrink-0 text-sm font-medium">K: {kValue}</span>
            <input
                type="range"
                min="1"
                max="100"
                value={kValue}
                onChange={(e) => setKValue(parseInt(e.target.value))}
                className="ml-2 w-full h-1.5 rounded-lg cursor-pointer accent-emerald-500 bg-slate-200 dark:bg-slate-700"
                disabled={isSending}
            />
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          className={`p-3.5 rounded-full shadow-lg transition-all duration-300 flex-shrink-0 border 
            ${(query.trim() || jdText.trim()) && !isSending 
              ? 'bg-gradient-to-br from-emerald-500 to-teal-500 text-white border-transparent hover:shadow-emerald-500/30 hover:-translate-y-0.5 active:scale-95 cursor-pointer' 
              : 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 border-transparent cursor-not-allowed'}`}
          disabled={isSending || (!query.trim() && !jdText.trim())}
        >
          <FiSend size={20} className={(query.trim() || jdText.trim()) && !isSending ? 'drop-shadow-sm' : ''} />
        </button>
      </div>
       <div className="text-center text-xs mt-3 font-medium text-slate-400 dark:text-slate-500 tracking-wide">
            Tip: For JD search, simply paste the JD. Use the K-slider to control the number of matching resumes retrieved.
        </div>
    </div>
  );
}

export default MessageInput;