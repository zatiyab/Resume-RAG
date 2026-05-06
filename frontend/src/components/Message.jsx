// frontend/src/components/Message.jsx (updated)
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import LoadingDots from './LoadingDots.jsx';
import { useTheme } from '../contexts/ThemeContext.jsx';

const Message = ({ content, sender, time, isLoading = false, onDownload, hasDownloadButton = false, filesToDownload = [] }) => {
  const { theme } = useTheme();
  const isUser = sender === 'user';
  
  const bubbleClasses = isUser
    ? (theme === 'dark'
        ? 'bg-gradient-to-br from-emerald-600 to-teal-600 text-white'
        : 'bg-emerald-500/20 text-hiremind-text-light-primary')
    : (theme === 'dark'
        ? 'bg-slate-800/60 text-slate-100'
        : 'bg-hiremind-element-light text-hiremind-text-light-primary');

  const timeClasses = theme === 'dark' ? 'text-slate-400' : 'text-hiremind-text-light-secondary';
  const markdownTextClass = theme === 'dark' ? 'text-slate-100' : 'text-hiremind-text-light-primary';
  const markdownMutedClass = theme === 'dark' ? 'text-slate-300' : 'text-slate-700';
  const markdownBorderClass = theme === 'dark' ? 'border-white/15' : 'border-slate-300';
  const markdownCodeBgClass = theme === 'dark' ? 'bg-slate-900/80' : 'bg-slate-100';
  const markdownInlineCodeBgClass = theme === 'dark' ? 'bg-slate-700/70' : 'bg-slate-200';
  const markdownLinkClass = theme === 'dark' ? 'text-emerald-300 hover:text-emerald-200' : 'text-emerald-700 hover:text-emerald-800';
  const markdownBlockquoteClass = theme === 'dark' ? 'border-emerald-400/40 text-slate-300' : 'border-emerald-500/40 text-slate-700';

 return (
    <div className={`flex mb-5 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] md:max-w-[60%] px-3 py-4 md:px-4 md:py-7 rounded-lg shadow-lg backdrop-blur-sm transition-colors duration-200 
          ${theme === 'dark' ? 'border border-white/10' : 'border border-hiremind-element-light'}
          ${bubbleClasses}`}
      >
        {isLoading ? (
          <LoadingDots />
        ) : (
          <>
            <div className={`break-words leading-7 text-sm md:text-[0.95rem] ${markdownTextClass}`}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ children }) => <p className={`mb-3 last:mb-0 whitespace-pre-wrap ${markdownMutedClass}`}>{children}</p>,
                  ul: ({ children }) => <ul className="mb-3 ml-5 list-disc space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="mb-3 ml-5 list-decimal space-y-1">{children}</ol>,
                  li: ({ children }) => <li className={markdownMutedClass}>{children}</li>,
                  h1: ({ children }) => <h1 className="mb-3 text-lg font-bold">{children}</h1>,
                  h2: ({ children }) => <h2 className="mb-3 text-base font-bold">{children}</h2>,
                  h3: ({ children }) => <h3 className="mb-2 text-sm font-semibold">{children}</h3>,
                  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                  em: ({ children }) => <em className="italic">{children}</em>,
                  blockquote: ({ children }) => (
                    <blockquote className={`my-3 border-l-4 pl-3 italic ${markdownBlockquoteClass}`}>{children}</blockquote>
                  ),
                  hr: () => <hr className={`my-4 border ${markdownBorderClass}`} />,
                  a: ({ href, children }) => (
                    <a
                      href={href}
                      target="_blank"
                      rel="noreferrer"
                      className={`underline underline-offset-2 transition-colors ${markdownLinkClass}`}
                    >
                      {children}
                    </a>
                  ),
                  code: ({ inline, children }) =>
                    inline ? (
                      <code className={`rounded px-1 py-0.5 text-[0.85em] ${markdownInlineCodeBgClass}`}>{children}</code>
                    ) : (
                      <code className="text-[0.9em]">{children}</code>
                    ),
                  pre: ({ children }) => (
                    <pre className={`my-3 overflow-x-auto rounded-xl p-3 ${markdownCodeBgClass}`}>{children}</pre>
                  ),
                }}
              >
                {content || ''}
              </ReactMarkdown>
            </div>
            {hasDownloadButton && (
              <button
                onClick={() => onDownload(filesToDownload)}
                className={`mt-4 px-5 py-2.5 flex items-center gap-2 font-semibold text-sm rounded-xl transition-all duration-300 transform hover:-translate-y-0.5 active:scale-95 shadow-md
                  ${theme === 'dark' 
                    ? 'bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-emerald-900/40 hover:shadow-emerald-500/30' 
                    : 'bg-gradient-to-br from-emerald-400 to-teal-500 text-white shadow-emerald-200 hover:shadow-emerald-400/40'}`}
              >
                <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                <span className="truncate">Download Selected Resumes</span>
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