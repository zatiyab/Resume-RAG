// frontend/src/components/LoginForm.jsx (New File)
import React, { useState } from 'react';
import { FiMail, FiLock, FiEye, FiEyeOff } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';

const LoginForm = () => {
  const { theme } = useTheme();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Login Data:', formData);
    alert('Login button clicked! (No actual submission)'); // For now, just an alert
    // Here, you would typically send data to your backend for authentication
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
      >
        LOGIN
      </button>
    </form>
  );
};

export default LoginForm;