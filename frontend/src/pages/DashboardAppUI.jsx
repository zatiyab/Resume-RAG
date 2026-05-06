// frontend/src/pages/DashboardAppUI.jsx (NEW FILE)
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // <--- useNavigate ko yahan import kiya
import { FiFolder } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';
import Sidebar from '../components/Sidebar.jsx';
import ChatWindow from '../components/ChatWindow.jsx';
import MessageInput from '../components/MessageInput.jsx';
import ResumesDrawer from '../components/ResumesDrawer.jsx';
import { searchResumes, downloadResumes, fetchChatHistory, fetchChatGroups, logoutUser } from '../services/api.js';
import { getUserNameFromToken } from '../utils/helpers.js';

const createChatGroup = (name = 'New Chat') => ({
  id: window.crypto?.randomUUID ? window.crypto.randomUUID() : Math.random().toString(36).slice(2),
  name,
});

const createWelcomeMessage = (userName = null) => ({
  content: `Welcome${userName ? `, ${userName}` : ''} to HireMind! 👋 I'm your AI Recruitment Assistant. Upload resumes using the left sidebar, or paste a Job Description/ask a query in the input box below.`,
  sender: 'bot',
  time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
});

// Main App UI (your existing chat interface)
function DashboardAppUI() {
  const navigate = useNavigate(); 
  const { theme } = useTheme();
  const [userName] = useState(() => {
    const token = localStorage.getItem('access_token');
    return getUserNameFromToken(token);
  });
  
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/auth');
    }
  }, [navigate]);

  const handleLogout = async () => {
    try {
      await logoutUser();
      navigate('/auth');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const [messages, setMessages] = useState([createWelcomeMessage(userName)]);
  const [isSending, setIsSending] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isResumesDrawerOpen, setIsResumesDrawerOpen] = useState(false);
  const [currentChatGroupId, setCurrentChatGroupId] = useState(null);
  const [chatSessions, setChatSessions] = useState([]);

  // Pagination state for lazy loading
  const [paginationOffset, setPaginationOffset] = useState(0);
  const [hasMoreMessages, setHasMoreMessages] = useState(false);
  const [hasInitiallyLoaded, setHasInitiallyLoaded] = useState(false);

  // Fetch initial chat groups when component mounts
  useEffect(() => {
    const loadInitialState = async () => {
      const defaultGroup = createChatGroup();
      setCurrentChatGroupId(defaultGroup.id);
      setChatSessions([defaultGroup]);
      setMessages([createWelcomeMessage(userName)]);

      try {
        const data = await fetchChatGroups();
        if (data.groups && data.groups.length > 0) {
          const backendGroups = data.groups.map((group) => ({
            id: group.chat_group_id,
            name: group.title || 'New Chat',
            messageCount: group.message_count,
            lastMessage: group.last_message,
          }));

          setChatSessions([defaultGroup, ...backendGroups.filter((group) => group.id !== defaultGroup.id)]);
        }
        setHasInitiallyLoaded(true);
      } catch (error) {
        console.error('Error loading initial chat groups:', error);
        setHasInitiallyLoaded(true);
      }
    };

    loadInitialState();
  }, []);

  useEffect(() => {
    if (!currentChatGroupId || !hasInitiallyLoaded) {
      return;
    }

    const loadCurrentChatHistory = async () => {
      try {
        const data = await fetchChatHistory(currentChatGroupId, 5, 0);
        if (data.messages && data.messages.length > 0) {
          const transformedMessages = data.messages.map(msg => ({
            content: msg.content,
            sender: msg.role === 'user' ? 'user' : 'bot',
            time: new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          }));

          setMessages(transformedMessages);
          setPaginationOffset(5);
          setHasMoreMessages(data.hasMore);
        } else {
          setMessages([createWelcomeMessage(userName)]);
          setPaginationOffset(0);
          setHasMoreMessages(false);
        }
      } catch (error) {
        console.error('Error loading chat history:', error);
        setMessages([createWelcomeMessage(userName)]);
      }
    };

    loadCurrentChatHistory();
  }, [currentChatGroupId, hasInitiallyLoaded, userName]);

  // Load more messages when user scrolls to top
  const handleLoadMore = async () => {
    if (isLoadingMore || !hasMoreMessages) return;

    setIsLoadingMore(true);
    try {
      const data = await fetchChatHistory(currentChatGroupId, 5, paginationOffset);
      if (data.messages && data.messages.length > 0) {
        // Transform messages from API format to UI format
        const transformedMessages = data.messages.map(msg => ({
          content: msg.content,
          sender: msg.role === 'user' ? 'user' : 'bot',
          time: new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }));
        
        // Prepend new messages to the beginning (older messages)
        setMessages(prev => [...transformedMessages, ...prev]);
        setPaginationOffset(paginationOffset + 5);
        setHasMoreMessages(data.hasMore);
      }
    } catch (error) {
      console.error('Error loading more chat history:', error);
    } finally {
      setIsLoadingMore(false);
    }
  };

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
      const activeChatGroupId = currentChatGroupId || createChatGroup().id;
      const data = await searchResumes(text, kValue, isJDSearch, activeChatGroupId);

      if (!currentChatGroupId) {
        setCurrentChatGroupId(activeChatGroupId);
      }

      setChatSessions((prev) => prev.map((session) => {
        if (session.id !== activeChatGroupId) {
          return session;
        }

        return {
          ...session,
          name: session.name === 'New Chat' ? (text.trim().slice(0, 48) || 'New Chat') : session.name,
          lastMessage: text.trim(),
        };
      }));
      
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
    const nextGroup = createChatGroup();
    setCurrentChatGroupId(nextGroup.id);
    setMessages([createWelcomeMessage(userName)]);
    setPaginationOffset(0);
    setHasMoreMessages(false);
    setChatSessions((prev) => [
      nextGroup,
      ...prev.filter((session) => session.id !== nextGroup.id),
    ]);
  };

  const handleChatSelect = (chatGroupId) => {
    setCurrentChatGroupId(chatGroupId);
  };

  const handleDeleteChatGroup = (deletedChatGroupId) => {
    setChatSessions((prevSessions) => {
      const remainingSessions = prevSessions.filter((session) => session.id !== deletedChatGroupId);

      if (currentChatGroupId === deletedChatGroupId) {
        if (remainingSessions.length > 0) {
          const nextSession = remainingSessions[0];
          setCurrentChatGroupId(nextSession.id);
          setPaginationOffset(0);
          setHasMoreMessages(false);
          setMessages([createWelcomeMessage(userName)]);
        } else {
          const newGroup = createChatGroup();
          setCurrentChatGroupId(newGroup.id);
          setMessages([createWelcomeMessage(userName)]);
          setPaginationOffset(0);
          setHasMoreMessages(false);
          return [newGroup];
        }
      }

      return remainingSessions.length > 0 ? remainingSessions : [createChatGroup()];
    });
  };

  return (
    <div className={`flex h-screen overflow-hidden transition-colors duration-300 ${
      theme === 'dark'
        ? 'bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-300'
        : 'bg-gradient-to-br from-white via-slate-50 to-slate-100 text-slate-800'
    }`}>
      <Sidebar
        onNewChat={handleNewChat}
        onChatSelect={handleChatSelect}
        onDeleteChatGroup={handleDeleteChatGroup}
        chatSessions={chatSessions}
        currentChatGroupId={currentChatGroupId}
        onLogout={handleLogout}
      />
      <div className="flex flex-col flex-1">
        <header className={`p-5 shadow-lg z-10 backdrop-blur-md border-b transition-colors duration-300 ${
          theme === 'dark'
            ? 'bg-slate-900/50 border-white/10'
            : 'bg-white/70 border-slate-200/80'
        }`}>
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1 text-center">
              <h1 className={`text-3xl font-extrabold tracking-tight font-heading bg-gradient-to-r text-transparent bg-clip-text drop-shadow-sm ${
                theme === 'dark'
                  ? 'from-emerald-400 to-teal-300'
                  : 'from-emerald-600 to-teal-500'
              }`}>
                HireMind AI Assistant
              </h1>
            </div>
            <button
              onClick={() => setIsResumesDrawerOpen(true)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all duration-300 hover:-translate-y-0.5 active:scale-95 border ${theme === 'dark' ? 'bg-white/5 border-white/10 text-slate-200 hover:bg-white/10' : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'}`}
            >
              <FiFolder size={18} /> Resumes
            </button>
          </div>
        </header>
        <ChatWindow 
          messages={messages} 
          onDownloadResumes={handleDownloadResumes}
          isLoadingMore={isLoadingMore}
          hasMore={hasMoreMessages}
        />
        {/* Fixed Input Container placed in flow so content doesn't go behind it */}
        <div className="w-full px-0 md:px-0 z-20">
            <MessageInput onSendMessage={handleSendMessage} isSending={isSending} />
        </div>
      </div>
      <ResumesDrawer isOpen={isResumesDrawerOpen} onClose={() => setIsResumesDrawerOpen(false)} />
    </div>
  );
}

export default DashboardAppUI;
