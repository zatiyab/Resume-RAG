// frontend/src/components/MessageInput.jsx (updated)
import React, { useState } from 'react';
import { FiSend } from 'react-icons/fi';
import { FaSlidersH } from 'react-icons/fa';
import { useTheme } from '../contexts/ThemeContext.jsx'; // Make sure .jsx extension is here

const MessageInput = ({ onSendMessage, isSending }) => {
  const { theme } = useTheme(); // Get current theme
  const [query, setQuery] = useState('');
  const [jdText, setJdText] = useState('');
  const [kValue, setKValue] = useState(5);

  const composerClassName = theme === 'dark'
    ? 'p-3 md:p-4 rounded-none shadow-[0_8px_30px_rgb(0,0,0,0.6)] backdrop-blur-md bg-slate-950/90 border border-white/10 transition-all duration-300'
    : 'p-3 md:p-4 rounded-none shadow-[0_8px_30px_rgb(0,0,0,0.12)] backdrop-blur-md bg-white/70 border border-slate-200/50 transition-all duration-300';

  const textareaClassName = theme === 'dark'
    ? 'flex-1 p-3.5 pl-3 pr-6 rounded-lg resize-none outline-none transition-all duration-300 custom-scrollbar h-12 bg-slate-900/90 focus:bg-slate-900 focus:ring-2 focus:ring-emerald-500/50 text-slate-100 placeholder-slate-500 border border-white/10'
    : 'flex-1 p-3.5 pl-3 pr-6 rounded-lg resize-none outline-none transition-all duration-300 custom-scrollbar h-12 bg-white/50 focus:bg-white focus:ring-2 focus:ring-emerald-500/50 text-slate-800 placeholder-slate-400 border border-slate-200/50';

  const sliderClassName = theme === 'dark'
    ? 'flex items-center rounded-lg p-2 px-4 flex-shrink-0 w-28 sm:w-36 md:w-44 transition-colors duration-300 bg-slate-900/90 text-slate-300 border border-white/10'
    : 'flex items-center rounded-lg p-2 px-4 flex-shrink-0 w-28 sm:w-36 md:w-44 transition-colors duration-300 bg-slate-100/50 text-slate-600 border border-slate-200/50';

  const sendButtonClassName = (query.trim() || jdText.trim()) && !isSending
    ? 'bg-gradient-to-br from-emerald-500 to-teal-500 text-white border-transparent hover:shadow-emerald-500/30 hover:-translate-y-0.5 active:scale-95 cursor-pointer'
    : theme === 'dark'
      ? 'bg-slate-800 text-slate-500 border-transparent cursor-not-allowed'
      : 'bg-slate-100 text-slate-400 border-transparent cursor-not-allowed';

  const tipClassName = theme === 'dark'
    ? 'text-center text-xs mt-3 font-medium text-slate-400 tracking-wide'
    : 'text-center text-xs mt-3 font-medium text-slate-500 tracking-wide';

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

  return (
    <div className={composerClassName}>
      <div className="relative flex items-end gap-3 w-full">
        {/* Textarea for General Query / JD */}
        <textarea
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
          rows="2"
          className={textareaClassName}
          disabled={isSending}
        />
        
        {/* K-value slider and display */}
        <div className={sliderClassName}>
            <FaSlidersH className="mr-2 flex-shrink-0 opacity-70" />
            <span className="flex-shrink-0 text-sm font-medium">K: {kValue}</span>
            <input
                type="range"
                min="1"
                max="10"
                value={kValue}
                onChange={(e) => setKValue(parseInt(e.target.value))}
                className="ml-2 w-full h-1.5 rounded-lg cursor-pointer accent-emerald-500 bg-slate-200 dark:bg-slate-700"
                disabled={isSending}
            />
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          className={`p-3.5 rounded-full shadow-lg transition-all duration-300 flex-shrink-0 border ${sendButtonClassName}`}
          disabled={isSending || (!query.trim() && !jdText.trim())}
        >
          <FiSend size={20} className={(query.trim() || jdText.trim()) && !isSending ? 'drop-shadow-sm' : ''} />
        </button>
      </div>
         <div className={tipClassName}>
            Tip: For JD search, simply paste the JD. Use the K-slider to control the number of matching resumes retrieved.
        </div>
    </div>
  );
}

export default MessageInput;