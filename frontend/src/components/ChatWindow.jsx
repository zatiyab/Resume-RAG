// frontend/src/components/ChatWindow.jsx (updated with lazy loading)
import React, { useRef, useEffect, useState } from 'react';
import Message from './Message.jsx';
import { useTheme } from '../contexts/ThemeContext.jsx';

const ChatWindow = ({ messages, onDownloadResumes, onLoadMore, isLoadingMore = false, hasMore = false }) => {
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const { theme } = useTheme();
  const [scrolledFromBottom, setScrolledFromBottom] = useState(false);

  const scrollToBottom = () => {
    if (!scrolledFromBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrolledFromBottom]);

  // Handle scroll event for lazy loading
  const handleScroll = (e) => {
    const container = e.target;
    const isNearTop = container.scrollTop < 100;
    const isAtBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 50;

    setScrolledFromBottom(!isAtBottom);

    // Trigger load more when user scrolls near the top
    if (isNearTop && hasMore && !isLoadingMore && onLoadMore) {
      onLoadMore();
    }
  };

  return (
    <div 
      className={`flex-1 p-5 overflow-y-auto custom-scrollbar rounded-none backdrop-blur-sm shadow-inner 
        ${theme === 'dark' 
          ? 'bg-slate-900/20 border border-white/5' 
          : 'bg-hiremind-bg-light/80 border border-slate-300/80'}`}
      onScroll={handleScroll}
      ref={messagesContainerRef}
    >
      {/* Loading indicator when fetching more messages */}
      {isLoadingMore && (
        <div className={`text-center py-4 ${theme === 'dark' ? 'text-slate-400' : 'text-hiremind-text-light-secondary'}`}>
          <div className="text-sm">Loading earlier messages...</div>
        </div>
      )}

      {messages.length === 0 ? (
        <div className={`text-center p-10 
          ${theme === 'dark' ? 'text-slate-400' : 'text-hiremind-text-light-secondary'}`}>
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