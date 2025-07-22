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

  const inputBgColor = theme === 'dark' ? 'bg-hiremind-element-dark' : 'bg-hiremind-element-light';
  const inputTextColor = theme === 'dark' ? 'text-hiremind-text-dark-primary' : 'text-hiremind-text-light-primary';
  const inputBorderColor = theme === 'dark' ? 'border-white/10' : 'border-black/10';
  const placeholderColor = theme === 'dark' ? 'placeholder-hiremind-text-dark-secondary' : 'placeholder-hiremind-text-light-secondary';
  
  return (
    <div className={`p-4 border-t shadow-lg backdrop-blur-md 
      ${theme === 'dark' 
        ? 'bg-hiremind-element-dark/50 border-white/10 shadow-hiremind-darkblue/30' 
        : 'bg-hiremind-element-light/50 border-black/10 shadow-hiremind-darkblue/10'}`}>
      <div className="relative flex items-end gap-3 max-w-3xl mx-auto">
        {/* Attachment button */}
        <button
          onClick={handleFileUploadClick}
          className={`p-3 rounded-full shadow-md transition-colors 
            backdrop-blur-sm border 
            ${theme === 'dark' 
              ? 'bg-hiremind-darkblue/60 text-hiremind-text-dark-primary hover:bg-hiremind-darkblue/80 border-hiremind-darkblue/70' 
              : 'bg-hiremind-beige/60 text-hiremind-darkblue hover:bg-hiremind-beige/80 border-hiremind-beige/70'}`}
          disabled={isSending}
          title="Upload JD or Resumes"
        >
          <FiPlus size={20} />
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
          className={`flex-1 p-3 pl-5 rounded-3xl resize-none outline-none focus:ring-2 focus:ring-hiremind-accent-purple/50 transition-colors custom-scrollbar
            backdrop-blur-sm border border max-h-24 overflow-y-auto
            ${inputBgColor} ${inputTextColor} ${inputBorderColor} ${placeholderColor}`}
          disabled={isSending}
        />
        
        {/* K-value slider and display */}
        <div className={`flex items-center rounded-xl p-2 px-3 text-sm flex-shrink-0 w-24 sm:w-32 md:w-40 
          backdrop-blur-sm border 
          ${theme === 'dark' 
            ? 'bg-hiremind-element-dark/60 text-hiremind-text-dark-secondary border-white/10' 
            : 'bg-hiremind-element-light/60 text-hiremind-text-light-secondary border-black/10'}`}>
            <FaSlidersH className="mr-2 flex-shrink-0" />
            <span className="flex-shrink-0">K: {kValue}</span>
            <input
                type="range"
                min="1"
                max="100"
                value={kValue}
                onChange={(e) => setKValue(parseInt(e.target.value))}
                className="ml-2 w-full h-1 rounded-lg cursor-pointer accent-hiremind-accent-purple flex-grow"
                disabled={isSending}
            />
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          className="p-3 rounded-full shadow-md hover:bg-hiremind-accent-purple/80 transition-colors
            backdrop-blur-sm border 
            ${theme === 'dark' 
              ? 'bg-hiremind-accent-purple/60 text-black border-hiremind-accent-purple/70' 
              : 'bg-hiremind-accent-purple/30 text-hiremind-darkblue border-hiremind-accent-purple/40'}"
          disabled={isSending || (!query.trim() && !jdText.trim())}
        >
          <FiSend size={20} />
        </button>
      </div>
       <div className={`text-center text-sm mt-2 
        ${theme === 'dark' ? 'text-hiremind-text-dark-secondary' : 'text-hiremind-text-light-secondary'}`}>
            Tip: For JD search, paste the JD. For general queries, type directly. Use the K-slider for number of results.
        </div>
    </div>
  );
}

export default MessageInput;