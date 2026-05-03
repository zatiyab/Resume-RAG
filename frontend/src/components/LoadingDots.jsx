// frontend/src/components/LoadingDots.jsx (updated)
import React from 'react';
import { useTheme } from '../contexts/ThemeContext.jsx';

const LoadingDots = () => {
  const { theme } = useTheme();
  const dotColorClass = theme === 'dark' ? 'bg-emerald-300' : 'bg-emerald-600';
  return (
    <div className="flex items-center gap-3">
      <span className={`text-xs font-medium tracking-wide ${theme === 'dark' ? 'text-hiremind-text-dark-secondary' : 'text-hiremind-text-light-secondary'}`}>
        Thinking
      </span>
      <div className="flex items-center gap-1.5">
        <span className={`w-2 h-2 rounded-full animate-bounce ${dotColorClass}`} style={{ animationDelay: '0s' }}></span>
        <span className={`w-2 h-2 rounded-full animate-bounce ${dotColorClass}`} style={{ animationDelay: '0.15s' }}></span>
        <span className={`w-2 h-2 rounded-full animate-bounce ${dotColorClass}`} style={{ animationDelay: '0.3s' }}></span>
      </div>
    </div>
  );
};

export default LoadingDots;