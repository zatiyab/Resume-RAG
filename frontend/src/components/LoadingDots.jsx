// frontend/src/components/LoadingDots.jsx (updated)
import React from 'react';
import { useTheme } from '../contexts/ThemeContext.jsx';

const LoadingDots = () => {
  const { theme } = useTheme();
  const dotColorClass = theme === 'dark' ? 'bg-hiremind-beige' : 'bg-hiremind-darkblue';
  return (
    <div className="flex space-x-1">
      <span className={`w-2 h-2 rounded-full animate-pulse ${dotColorClass}`} style={{ animationDelay: '0s' }}></span>
      <span className={`w-2 h-2 rounded-full animate-pulse ${dotColorClass}`} style={{ animationDelay: '0.2s' }}></span>
      <span className={`w-2 h-2 rounded-full animate-pulse ${dotColorClass}`} style={{ animationDelay: '0.4s' }}></span>
    </div>
  );
};

export default LoadingDots;