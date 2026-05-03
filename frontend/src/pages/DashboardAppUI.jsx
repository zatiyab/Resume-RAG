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

  const handleSendMessage = async (text, isJDSearch, kValue) => {
    const newMessage = {
      content: text,
      sender: 'user',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, newMessage]);
    setIsSending(true);

    // Add typing indicator
    const typingMessage = { content: '', sender: 'bot', time: '', isLoading: true };
    setMessages((prev) => [...prev, typingMessage]);

    try {
      const data = await searchResumes(text, kValue, isJDSearch);
      
      setMessages((prev) => {
        const updatedMessages = prev.filter(msg => !msg.isLoading); // Remove typing indicator
        const botResponse = {
          content: data.response || "I couldn't find a relevant answer.",
          sender: 'bot',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          hasDownloadButton: data.selected_files && data.selected_files.length > 0,
          filesToDownload: data.selected_files || [],
        };
        return [...updatedMessages, botResponse];
      });
    } catch (error) {
      console.error('Search error:', error);
      setMessages((prev) => {
        const updatedMessages = prev.filter(msg => !msg.isLoading); // Remove typing indicator
        const errorMessage = {
          content: "Sorry, I'm having trouble connecting to the backend. Please check if the server is running.",
          sender: 'bot',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        return [...updatedMessages, errorMessage];
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleDownloadResumes = async (files) => {
    try {
      const blob = await downloadResumes(files);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'selected_resumes.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setMessages((prev) => [...prev, {
        content: `Downloaded ${files.length} resume(s)!`,
        sender: 'bot',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch (error) {
      console.error('Download error:', error);
      setMessages((prev) => [...prev, {
        content: "Failed to download resumes. Please try again.",
        sender: 'bot',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentChatId(Math.random().toString(36).substring(7)); // Generate a new ID
    setChatSessions((prev) => [...prev, { id: currentChatId, name: `Chat ${prev.length + 1}` }]); // Add new session to history
  };

  const handleChatSelect = (chatId) => {
    // In a real app, you'd load messages for this chatId from backend
    setMessages([{ // Placeholder message for selected chat
      content: `Loaded chat: ${chatId}. (Feature under development)`,
      sender: 'bot',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }]);
    setCurrentChatId(chatId);
  };

  const handleBulkUploadFiles = async (files) => {
    setMessages((prev) => [...prev, {
      content: `Uploading ${files.length} resume(s) in bulk...`,
      sender: 'bot',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }]);
    try {
      const data = await apiUploadResumes(files);
      setMessages((prev) => [...prev, {
        content: data.message || data.error || 'Bulk upload complete.',
        sender: 'bot',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch (error) {
      console.error('Bulk upload error:', error);
      setMessages((prev) => [...prev, {
        content: "Failed to perform bulk upload. Network error or server issue.",
        sender: 'bot',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-transparent text-hiremind-text-light-primary dark:text-hiremind-text-dark-primary transition-colors duration-300">
      <Sidebar
        onNewChat={handleNewChat}
        onChatSelect={handleChatSelect}
        chatSessions={chatSessions}
        onBulkUploadFiles={handleBulkUploadFiles}
      />
      <div className="flex flex-col flex-1">
        <header className="p-5 text-center shadow-sm z-10 backdrop-blur-3xl bg-white/40 dark:bg-black/20 border-b border-black/5 dark:border-white/5 transition-colors duration-300">
          <h1 className="text-3xl font-extrabold tracking-tight font-heading bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-300 text-transparent bg-clip-text drop-shadow-sm">
            HireMind AI Assistant
          </h1>
        </header>
        <ChatWindow messages={messages} onDownloadResumes={handleDownloadResumes} />
        {/* Fixed Input Container placed in flow so content doesn't go behind it */}
        <div className="w-full px-0 md:px-0 z-20">
            <MessageInput onSendMessage={handleSendMessage} onUploadFiles={handleBulkUploadFiles} isSending={isSending} />
        </div>
      </div>
    </div>
  );
}

export default DashboardAppUI;
