// frontend/src/components/LoginForm.jsx (New File)
import React, { useState } from 'react';
import { FiMail, FiLock, FiEye, FiEyeOff } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { loginUser } from '../services/api.js';

const LoginForm = ({ onLoginSuccess}) => {
  const { theme } = useTheme();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState(''); 
  const [isLoading, setIsLoading] = useState(false);

  const isDark = theme === 'dark';

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(''); // Clear previous errors
    setIsLoading(true); 

    try {
      const data = await loginUser(formData);
      if (data.detail) { // FastAPI error detail
        setFormError(data.detail);
      } else if (data.access_token) { 
        localStorage.setItem('access_token', data.access_token);
        // alert('Login successful! Redirecting...'); // For now, just an alert
        onLoginSuccess(); // Call callback to inform App which will handle navigation
      } else {
        setFormError('An unexpected error occurred during login.');
      }
    } catch (error) {
      console.error('Login API error:', error);
      setFormError('Network error or server unreachable. Please try again later.');
    } finally {
        setIsLoading(false); // <--- YAHAN CHANGE HAI: Loading always ends
    }

  };

  const inputClasses = `w-full px-4 py-3 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all duration-200 text-base border ${
    isDark
      ? 'bg-slate-900/80 border-white/10 text-slate-100 placeholder-slate-500'
      : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400'
  }`;

  const iconClasses = `text-emerald-500 text-lg ${isDark ? 'opacity-90' : 'opacity-100'}`;

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {formError && (
        <div className={`font-medium text-sm text-center py-3 px-4 rounded-2xl border ${isDark ? 'text-red-200 bg-red-500/10 border-red-500/20' : 'text-red-700 bg-red-50 border-red-200'}`}>
          {formError}
        </div>
      )}
      {/* Email Input */}
      <div className="relative">
        <FiMail className={`absolute left-4 top-1/2 -translate-y-1/2 ${iconClasses}`} />
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="E-mail"
          className={`pl-12 ${inputClasses}`}
          required
        />
      </div>

      {/* Password Input */}
      <div className="relative">
        <FiLock className={`absolute left-4 top-1/2 -translate-y-1/2 ${iconClasses}`} />
        <input
          type={showPassword ? 'text' : 'password'}
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Password"
          className={`pl-12 ${inputClasses}`}
          required
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
            className={`absolute right-4 top-1/2 -translate-y-1/2 text-emerald-500 text-lg hover:opacity-100 focus:outline-none ${isDark ? 'opacity-90' : 'opacity-80'}`}
        >
          {showPassword ? <FiEyeOff /> : <FiEye />}
        </button>
      </div>

      {/* Forgot Password (Optional)
      <div className="text-right text-sm">
        <a href="#" className="font-semibold text-hiremind-purple-accent hover:underline focus:outline-none">
          Forgot password?
        </a>
      </div> */}

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full py-3.5 rounded-2xl font-semibold shadow-lg transition-all duration-300 bg-gradient-to-r from-emerald-500 to-teal-500 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 hover:shadow-emerald-500/30 hover:-translate-y-0.5 active:scale-95"
          disabled={isLoading}
      >
        {isLoading ? 'Signing In...' : 'LOGIN'}
      </button>
    </form>
  );
};

export default LoginForm;