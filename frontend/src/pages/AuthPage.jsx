// frontend/src/pages/AuthPage.jsx (New File)
import React, { useState } from 'react';
import { useTheme } from '../contexts/ThemeContext.jsx'; // Import useTheme

// Import form components (will create later)
import SignUpForm from '../components/SignUpForm.jsx'; // Assuming forms are in components
import LoginForm from '../components/LoginForm.jsx';

const AuthPage = ({ onLoginSuccess }) => {
  const { theme } = useTheme(); // Get theme for background colors
  const [isSignUp, setIsSignUp] = useState(true); // State to switch between Sign Up and Login

  const cardBgClass = theme === 'dark' ? 'bg-hiremind-element-dark/80' : 'bg-hiremind-light-bg-card';
  const textColorClass = theme === 'dark' ? 'text-hiremind-text-dark-primary' : 'text-hiremind-text-light-primary';
  const cardBorderClass = theme === 'dark' ? 'border-white/10' : 'border-input-border-light';
  const cardShadowClass = theme === 'dark' ? 'shadow-hiremind-darkblue/50' : 'shadow-hiremind-darkblue/10';

  return (
    <div className={`flex items-center justify-center min-h-screen p-4 
      ${theme === 'dark' ? 'bg-hiremind-purple-primary' : 'bg-hiremind-beige'}`}>
      
      {/* Auth Card */}
      <div className={`w-full max-w-md p-8 rounded-2xl backdrop-blur-md shadow-xl border 
        ${cardBgClass} ${textColorClass} ${cardBorderClass} ${cardShadowClass}`}>
        
        <h2 className="text-3xl font-bold text-center mb-6 font-heading">
          {isSignUp ? 'Sign Up' : 'Login'}
        </h2>

        {isSignUp ? 
            <SignUpForm setIsSignUp={setIsSignUp} /> : // Pass setIsSignUp to SignUpForm
            <LoginForm onLoginSuccess={onLoginSuccess} />}
        <div className="text-center mt-6">
          <p className="text-sm">
            {isSignUp ? 'Already have an account?' : 'Don\'t have an account?'}{' '}
            <button
              onClick={() => setIsSignUp(!isSignUp)}
              className="font-semibold text-hiremind-purple-accent hover:underline focus:outline-none"
            >
              {isSignUp ? 'Sign in' : 'Sign up'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;