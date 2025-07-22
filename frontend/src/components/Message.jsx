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
                className="mt-3 px-3 py-1 bg-hiremind-accent-green text-white font-medium rounded-lg text-sm shadow-md hover:bg-hiremind-accent-green/80 transition"
              >
                📥 Download Selected Resumes ({filesToDownload.length})
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