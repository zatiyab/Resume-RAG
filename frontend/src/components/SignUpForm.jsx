// frontend/src/components/SignUpForm.jsx (New File)
import React, { useState } from 'react';
import { FiUser, FiMail, FiLock, FiEye, FiEyeOff } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';

const SignUpForm = () => {
  const { theme } = useTheme();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    // terms: false,
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Sign Up Data:', formData);
    alert('Sign Up button clicked! (No actual submission)'); // For now, just an alert
    // Here, you would typically send data to your backend
  };

  const inputClasses = `w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-hiremind-purple-accent transition-all duration-200 text-base border 
    ${theme === 'dark' 
      ? 'bg-hiremind-element-dark border-white/10 text-hiremind-text-dark-primary placeholder-hiremind-text-dark-secondary' 
      : 'bg-hiremind-input-bg-light border-hiremind-input-border-light text-hiremind-text-light-primary placeholder-hiremind-text-light-secondary'}`;

  const iconClasses = `text-hiremind-purple-accent text-lg ${theme === 'dark' ? 'opacity-80' : 'opacity-100'}`;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name Input */}
      <div className="relative">
        <FiUser className={`absolute left-4 top-1/2 -translate-y-1/2 ${iconClasses}`}/>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Name"
          className={`pl-12 ${inputClasses}`}
          required
        />
      </div>

      {/* Email Input */}
      <div className="relative">
        <FiMail className={`absolute left-4 top-1/2 -translate-y-1/2 ${iconClasses}`}/>
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
          // --- YAHAN CHANGE HAI (pr-12 to pr-16) ---
          className={`pl-12 pr-16 ${inputClasses}`} // Increased right padding for injected icon
          // --- END CHANGE ---
          required
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          // --- YAHAN CHANGE HAI (bg-transparent, added px-2 py-1, conditional bg) ---
          className="absolute right-4 top-1/2 -translate-y-1/2 text-hiremind-purple-accent text-lg opacity-80 hover:opacity-100 focus:outline-none z-10 
            px-2 py-1 rounded-full transition-colors 
            ${theme === 'dark' ? 'bg-hiremind-element-dark/80' : 'bg-hiremind-input-bg-light/80'}" // Added background and padding for button
          // --- END CHANGE ---
        >
          {showPassword ? <FiEyeOff /> : <FiEye />}
        </button>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full py-3 rounded-xl font-semibold shadow-lg transition-all duration-300 
          bg-hiremind-purple-accent hover:bg-hiremind-purple-accent/90 text-black focus:outline-none focus:ring-2 focus:ring-hiremind-purple-accent focus:ring-opacity-80"
      >
        CREATE ACCOUNT
      </button>
    </form>
  );
};

export default SignUpForm;