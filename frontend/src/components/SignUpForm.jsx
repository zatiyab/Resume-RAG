// frontend/src/components/SignUpForm.jsx (New File)
import React, { useState } from 'react';
import { FiUser, FiMail, FiLock, FiEye, FiEyeOff } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { signupUser } from '../services/api.js';


const SignUpForm = ({ setIsSignUp }) => {
  const { theme } = useTheme();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    // terms: false,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState(''); // For displaying form errors
  const [formSuccess, setFormSuccess] = useState(''); // For displaying success messages
  const isDark = theme === 'dark';


  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('handleSublmit called');
    setFormError(''); // Clear previous errors
    setFormSuccess(''); // Clear previous success
    setIsLoading(true);
    if (formData.password.length < 8) {
      setFormError('Password must be at least 8 characters long.');
      console.log("password too short:", formData.password.length);
      setIsLoading(false);
      return;
    }
    console.log('Attempting signup for:', formData.email);

    try {
      const data = await signupUser(formData);
      console.log('API response data:', data);
      if (data.detail) { // FastAPI error detail
        setFormError(data.detail);
      } else if (data.email) { // Successful signup returns user data
        console.log('Signup successful:', data);
        setFormSuccess('Account created successfully! You can now log in.');
        console.log('Signup successful, response:', data);
        setFormData({ name: '', email: '', password: '' }); // Clear form
        // Redirect to Sign In page
        setIsSignUp(false);
        console.log('Redirecting to Sign In page.'); // Debugging
      } else {
        setFormError('An unexpected error occurred during signup.');
        console.log('Unexpected API response:', data);
      }
    } catch (error) {
      console.error('Signup API error:', error);
      setFormError('Network error or server unreachable. Please try again later.');
    } finally {
      setIsLoading(false);
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
      {formSuccess && (
        <div className={`font-medium text-sm text-center py-3 px-4 rounded-2xl border ${isDark ? 'text-emerald-200 bg-emerald-500/10 border-emerald-500/20' : 'text-emerald-700 bg-emerald-50 border-emerald-200'}`}>
          {formSuccess}
        </div>
      )}
      {/* Name Input */}
      <div className="relative">
        <FiUser className={`absolute left-4 top-1/2 -translate-y-1/2 ${iconClasses}`} />
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
          className={`pl-12 pr-16 ${inputClasses}`}

          required
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className={`absolute right-4 top-1/2 -translate-y-1/2 text-emerald-500 text-lg hover:opacity-100 focus:outline-none z-10 px-2 py-1 rounded-full transition-colors ${isDark ? 'bg-slate-900/80 opacity-90' : 'bg-white/80 opacity-80'}`}

        >
          {showPassword ? <FiEyeOff /> : <FiEye />}
        </button>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full py-3.5 rounded-2xl font-semibold shadow-lg transition-all duration-300 bg-gradient-to-r from-emerald-500 to-teal-500 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 hover:shadow-emerald-500/30 hover:-translate-y-0.5 active:scale-95"
        disabled={isLoading}
      >
        {isLoading ? 'Creating Account...' : 'CREATE ACCOUNT'}
      </button>
    </form>
  );
};

export default SignUpForm;