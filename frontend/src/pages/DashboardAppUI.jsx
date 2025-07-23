// frontend/src/pages/DashboardAppUI.jsx (NEW FILE)
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // <--- useNavigate ko yahan import kiya
import Sidebar from '../components/Sidebar.jsx';
import ChatWindow from '../components/ChatWindow.jsx';
import MessageInput from '../components/MessageInput.jsx';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { searchResumes, downloadResumes, uploadResumes as apiUploadResumes } from '../services/api.js';

// Main App UI (your existing chat interface)
function DashboardAppUI() {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate(); // Ab yahan navigate defined hai
  
  // Basic authentication check within the UI component itself
  // If no token, redirect to login page
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/auth');
    }
  }, [navigate]);

  const [messages, setMessages] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const [currentChatId, setCurrentChatId] = useState('new');
  const [chatSessions, setChatSessions] = useState([{ id: 'new', name: 'New Chat' }]);

  useEffect(() => {
    if (messages.length === 0 && currentChatId === 'new') {
      const welcomeMessage = {
        content: "Welcome to HireMind! 👋 I'm your AI Recruitment Assistant. Upload resumes using the left sidebar, or paste a Job Description/ask a query in the input box below.",
        sender: 'bot',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages([welcomeMessage]);
    }
  }, [messages, currentChatId]);

  const handleSendMessage = async (text, isJDSearch, kValue) => { /* ... existing code ... */ };
  const handleDownloadResumes = async (files) => { /* ... existing code ... */ };
  const handleNewChat = () => { /* ... existing code ... */ };
  const handleChatSelect = (chatId) => { /* ... existing code ... */ };
  const handleBulkUploadFiles = async (files) => { /* ... existing code ... */ };

  return (
    <div className={`flex h-screen overflow-hidden 
      ${theme === 'dark' ? 'bg-hiremind-bg-dark text-hiremind-text-dark-primary' : 'bg-hiremind-bg-light text-hiremind-text-light-primary'}`}>
      <Sidebar
        onNewChat={handleNewChat}
        onChatSelect={handleChatSelect}
        chatSessions={chatSessions}
        onBulkUploadFiles={handleBulkUploadFiles}
      />
      <div className="flex flex-col flex-1">
        <header className={`p-4 text-center text-3xl font-extrabold tracking-wide shadow-xl border-b font-heading
          ${theme === 'dark' 
            ? 'bg-hiremind-element-dark text-hiremind-text-dark-primary border-white/10 shadow-hiremind-darkblue/40' 
            : 'bg-hiremind-element-light text-hiremind-text-light-primary border-black/10 shadow-hiremind-darkblue/10'}`}>
          HireMind: AI Resume Assistant
        </header>
        <ChatWindow messages={messages} onDownloadResumes={handleDownloadResumes} />
        <MessageInput onSendMessage={handleSendMessage} onUploadFiles={handleBulkUploadFiles} isSending={isSending} />
      </div>
    </div>
  );
}

export default DashboardAppUI;
