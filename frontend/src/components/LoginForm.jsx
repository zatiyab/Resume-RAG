// frontend/src/components/LoginForm.jsx (New File)
import React, { useState } from 'react';
import { FiMail, FiLock, FiEye, FiEyeOff } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { loginUser } from '../services/api.js'; // Import loginUser API
import { useNavigate } from 'react-router-dom';

const LoginForm = ({ onLoginSuccess}) => {
  const { theme } = useTheme();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState(''); 
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

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
        if (data.user_id) {
            localStorage.setItem('user_id', data.user_id);
        }
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

  const inputClasses = `w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-hiremind-purple-accent transition-all duration-200 text-base border 
    ${theme === 'dark' 
      ? 'bg-hiremind-element-dark border-white/10 text-hiremind-text-dark-primary placeholder-hiremind-text-dark-secondary' 
      : 'bg-hiremind-input-bg-light border-hiremind-input-border-light text-hiremind-text-light-primary placeholder-hiremind-text-light-secondary'}`;

  const iconClasses = `text-hiremind-purple-accent text-lg ${theme === 'dark' ? 'opacity-80' : 'opacity-100'}`;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
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
          className="absolute right-4 top-1/2 -translate-y-1/2 text-hiremind-purple-accent text-lg opacity-80 hover:opacity-100 focus:outline-none"
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
        className="w-full py-3 rounded-xl font-semibold shadow-lg transition-all duration-300 
          bg-hiremind-purple-accent hover:bg-hiremind-purple-accent/90 text-black focus:outline-none focus:ring-2 focus:ring-hiremind-purple-accent focus:ring-opacity-50"
          disabled={isLoading}
      >
        {isLoading ? 'Signing In...' : 'LOGIN'}
      </button>
    </form>
  );
};

export default LoginForm;