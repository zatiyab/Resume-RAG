// frontend/src/components/Message.jsx (updated)
import React from 'react';
import LoadingDots from './LoadingDots.jsx';
import { useTheme } from '../contexts/ThemeContext.jsx';

const Message = ({ content, sender, time, isLoading = false, onDownload, hasDownloadButton = false, filesToDownload = [] }) => {
  const { theme } = useTheme();
  const isUser = sender === 'user';
  
  const bubbleClasses = isUser
  ? // User Bubble Styles
    `${theme === 'dark' 
        ? 'bg-hiremind-accent-purple text-hiremind-text-dark-primary' /* Solid accent for user in dark */ 
        : 'bg-hiremind-accent-purple/20 text-hiremind-text-light-primary'} /* Lighter accent for user in light */
    rounded-br-md`
  : // Bot Bubble Styles
    `${theme === 'dark' 
        ? 'bg-hiremind-element-dark text-hiremind-text-dark-primary' /* Dark element background for bot in dark */ 
        : 'bg-hiremind-element-light text-hiremind-text-light-primary'} /* Light element background for bot in light */
    rounded-bl-md`;  const timeClasses = theme === 'dark' ? 'text-hiremind-text-dark-secondary' : 'text-hiremind-text-light-secondary';

 return (
    <div className={`flex mb-5 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] md:max-w-[60%] px-3 py-4 md:px-4 md:py-7 rounded-2xl shadow-sm backdrop-blur-sm transition-colors duration-200 
          ${theme === 'dark' ? 'border border-hiremind-element-dark' : 'border border-hiremind-element-light'}
          ${bubbleClasses}`}
      >
        {isLoading ? (
          <LoadingDots />
        ) : (
          <>
            <div className="break-word" dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br/>') }} />
            {hasDownloadButton && (
              <button
                onClick={() => onDownload(filesToDownload)}
                className={`mt-4 px-5 py-2.5 flex items-center gap-2 font-semibold text-sm rounded-xl transition-all duration-300 transform hover:-translate-y-0.5 active:scale-95 shadow-md
                  ${theme === 'dark' 
                    ? 'bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-emerald-900/40 hover:shadow-emerald-500/30' 
                    : 'bg-gradient-to-br from-emerald-400 to-teal-500 text-white shadow-emerald-200 hover:shadow-emerald-400/40'}`}
              >
                <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                <span className="truncate">Download {filesToDownload.length} Selected Resumes</span>
              </button>
            )}
            <div className={`text-[0.7rem] mt-1 ${isUser ? 'text-right' : 'text-left'} ${timeClasses}`}>
              {time}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Message;