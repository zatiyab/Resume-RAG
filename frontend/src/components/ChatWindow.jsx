// frontend/src/components/ChatWindow.jsx (updated)
import React, { useRef, useEffect } from 'react';
import Message from './Message.jsx'; // Make sure .jsx extension is here
import { useTheme } from '../contexts/ThemeContext.jsx';


const ChatWindow = ({ messages, onDownloadResumes }) => {
  const messagesEndRef = useRef(null);
  const { theme } = useTheme();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className={`flex-1 p-5 overflow-y-auto custom-scrollbar rounded-b-xl backdrop-blur-sm shadow-inner 
      ${theme === 'dark' 
        ? 'bg-hiremind-bg-dark/80 border border-hiremind-darkblue/80' /* Slightly transparent darkblue background */ 
        : 'bg-hiremind-bg-light/80 border border-hiremind-beige/80'}`}> {/* Slightly transparent beige background */}
      {messages.length === 0 ? (
        <div className={`text-center p-10 
          ${theme === 'dark' ? 'text-hiremind-text-dark-secondary' : 'text-hiremind-text-light-secondary'}`}>
          <div className="text-5xl mb-4">🤖</div>
          <p className="text-lg">Start by uploading resumes or typing a query!</p>
          <p className="text-sm mt-2 opacity-80">
            Try: "Find me a Senior Python Dev" or paste a Job Description.
          </p>
        </div>
      ) : (
        messages.map((msg, index) => (
          <Message
            key={index}
            content={msg.content}
            sender={msg.sender}
            time={msg.time}
            isLoading={msg.isLoading}
            hasDownloadButton={msg.hasDownloadButton}
            filesToDownload={msg.filesToDownload}
            onDownload={onDownloadResumes}
          />
        ))
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;