// frontend/src/components/Sidebar.jsx (UPDATED for MORE Professionalism and Colors)
import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { FiPlus, FiSun, FiMoon, FiTrash2, FiLogOut } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { deleteChatGroup } from '../services/api.js';

const hireMindLogo = '/hiremind-logo.png';

const Sidebar = ({ onNewChat, onChatSelect, onDeleteChatGroup, chatSessions, currentChatGroupId, onLogout }) => {
  const { theme, toggleTheme } = useTheme();
  const [confirmDialog, setConfirmDialog] = useState(null);

  const closeConfirmDialog = () => setConfirmDialog(null);

  const openConfirmDialog = (title, message, onConfirm) => {
    setConfirmDialog({ title, message, onConfirm });
  };

  const handleDeleteChatGroup = async (session) => {
    if (!session?.id) return;

    openConfirmDialog(
      'Delete Chat Group',
      `Delete "${session.name || 'New Chat'}" and all of its messages? This cannot be undone.`,
      async () => {
        try {
          if (session.messageCount) {
            await deleteChatGroup(session.id);
          }
          if (onDeleteChatGroup) {
            onDeleteChatGroup(session.id);
          }
        } catch (err) {
          console.error('Delete chat group failed:', err);
        }
      }
    );
  };

  const handleConfirmAction = async () => {
    if (!confirmDialog?.onConfirm) return;
    const action = confirmDialog.onConfirm;
    closeConfirmDialog();
    await action();
  };

  const sidebarClassName = theme === 'dark'
    ? 'w-64 flex flex-col shadow-2xl z-10 p-5 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 backdrop-blur-md text-slate-300 border-r border-white/10 transition-colors duration-300'
    : 'w-64 flex flex-col shadow-2xl z-10 p-5 bg-gradient-to-b from-white via-slate-50 to-white backdrop-blur-md text-slate-800 border-r border-slate-200 transition-colors duration-300';

  const headerCardClassName = theme === 'dark'
    ? 'flex items-center justify-between p-3 mb-8 rounded-2xl text-xl font-bold transition-all duration-300 bg-slate-900/70 shadow-lg shadow-slate-950/50 border border-white/10'
    : 'flex items-center justify-between p-3 mb-8 rounded-2xl text-xl font-bold transition-all duration-300 bg-white/80 shadow-lg shadow-slate-200/60 border border-slate-200';

  const selectedSessionClassName = theme === 'dark'
    ? 'bg-emerald-500/10 border-emerald-400/30 text-emerald-200 shadow-[0_0_0_1px_rgba(16,185,129,0.08)]'
    : 'bg-emerald-50 border-emerald-500/30 text-emerald-800 shadow-[0_0_0_1px_rgba(16,185,129,0.06)]';

  const sessionClassName = theme === 'dark'
    ? 'bg-slate-900/60 border-white/10 text-slate-200 hover:bg-slate-800/80 hover:border-white/20'
    : 'bg-white/90 border-slate-200/80 text-slate-700 hover:bg-slate-50 hover:border-slate-300';

  return (
    <>
    <div className={sidebarClassName}>

      {/* App Name/Header */}
      <div className={headerCardClassName}>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <span className="text-white font-bold text-sm">HM</span>
          </div>
          <span className={`bg-gradient-to-r text-transparent bg-clip-text ${theme === 'dark' ? 'from-emerald-400 to-teal-300' : 'from-emerald-600 to-teal-500'}`}>HireMind</span>
        </div>
        <button
          onClick={toggleTheme}
          className={`p-2 rounded-full transition-all duration-300 active:scale-95 ${theme === 'dark' ? 'hover:bg-white/10 text-slate-400 hover:text-slate-200' : 'hover:bg-slate-100 text-slate-600 hover:text-slate-900'}`}
          title="Toggle Theme"
        >
          {theme === 'dark' ? <FiMoon size={20} /> : <FiSun size={20} />}
        </button>
      </div>

      <button
        onClick={onNewChat}
        className="flex items-center justify-center gap-3 w-full px-4 py-3.5 mb-4 rounded-lg font-semibold shadow-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transform hover:-translate-y-0.5 active:scale-95 bg-gradient-to-r from-emerald-500 to-teal-500 text-white hover:shadow-emerald-500/30"
      >
        <FiPlus size={20} /> New Chat Group
      </button>

      <div className="mb-4 flex-1 min-h-0 overflow-hidden flex flex-col">
        <h4 className={`text-sm font-semibold mb-2 uppercase tracking-[0.18em] ${theme === 'dark' ? 'text-slate-200' : 'text-slate-700'}`}>Chat Groups</h4>
        <div className="space-y-2 overflow-auto custom-scrollbar pr-1">
          {chatSessions.length === 0 ? (
            <p className={`text-xs ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>No chat groups yet.</p>
          ) : (
            chatSessions.map((session) => (
              <div
                key={session.id}
                className={`w-full text-left px-3 py-2 rounded-2xl border transition-all duration-200 ${currentChatGroupId === session.id ? selectedSessionClassName : sessionClassName}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <button
                    type="button"
                    onClick={() => onChatSelect(session.id)}
                    className="flex-1 min-w-0 text-left"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="truncate text-sm font-medium">{session.name}</span>
                    </div>
                    {session.lastMessage ? (
                      <p className={`mt-1 text-xs truncate ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>{session.lastMessage}</p>
                    ) : null}
                  </button>

                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteChatGroup(session);
                    }}
                    className={`mt-0.5 p-2 rounded-lg transition-all duration-200 ${theme === 'dark' ? 'hover:bg-red-500/10 text-slate-400 hover:text-red-300' : 'hover:bg-red-50 text-slate-500 hover:text-red-600'}`}
                    title="Delete chat group"
                  >
                    <FiTrash2 size={14} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className={`mt-auto pt-5 border-t ${theme === 'dark' ? 'border-white/10' : 'border-slate-200'}`} />

      <button
        onClick={onLogout}
        className={`flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-lg font-semibold transition-all duration-300 ${theme === 'dark' ? 'bg-red-600/10 hover:bg-red-600/20 text-red-400 hover:text-red-300 border border-red-600/30 hover:border-red-600/50' : 'bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-700 border border-red-200 hover:border-red-300'}`}
      >
        <FiLogOut size={18} />
        Logout
      </button>
    </div>
    {confirmDialog && createPortal(
      <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 px-4">
        <div className={`w-full max-w-md rounded-2xl border p-5 shadow-2xl ${theme === 'dark' ? 'bg-slate-950 border-white/10 text-slate-100' : 'bg-white border-slate-200 text-slate-900'}`}>
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-red-500/10 text-red-500">
              <FiTrash2 size={18} />
            </div>
            <div>
              <h3 className="text-lg font-semibold">{confirmDialog.title}</h3>
              <p className={`text-xs uppercase tracking-[0.22em] ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Permanent action</p>
            </div>
          </div>
          <p className={`mt-4 text-sm leading-6 ${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>{confirmDialog.message}</p>
          <div className="mt-6 flex justify-end gap-3">
            <button
              onClick={closeConfirmDialog}
              className={`px-4 py-2 rounded-xl text-sm font-medium border ${theme === 'dark' ? 'border-white/10 text-slate-200 hover:bg-white/10' : 'border-slate-200 text-slate-700 hover:bg-slate-50'}`}
            >
              Cancel
            </button>
            <button
              onClick={handleConfirmAction}
              className="px-4 py-2 rounded-xl text-sm font-medium bg-red-600 text-white hover:bg-red-700"
            >
              Delete group
            </button>
          </div>
        </div>
      </div>,
      document.body
    )}
    </>
  );
};

export default Sidebar;