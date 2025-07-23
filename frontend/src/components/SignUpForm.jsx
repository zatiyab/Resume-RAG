// frontend/src/components/SignUpForm.jsx (New File)
import React, { useState } from 'react';
import { FiUser, FiMail, FiLock, FiEye, FiEyeOff } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { signupUser } from '../services/api.js';


const SignUpForm = ({setIsSignUp}) => {
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
        print('Signup successful:', data)
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
  const inputClasses = `w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-hiremind-purple-accent transition-all duration-200 text-base border 
    ${theme === 'dark' 
      ? 'bg-hiremind-element-dark border-white/10 text-hiremind-text-dark-primary placeholder-hiremind-text-dark-secondary' 
      : 'bg-hiremind-input-bg-light border-hiremind-input-border-light text-hiremind-text-light-primary placeholder-hiremind-text-light-secondary'}`;

  const iconClasses = `text-hiremind-purple-accent text-lg ${theme === 'dark' ? 'opacity-80' : 'opacity-100'}`;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {formError && (
        <div className="text-red-500 font-bold text-sm text-center py-2 px-3 rounded-lg bg-red-500/20 border border-red-500/50 my-2">
          {formError}
        </div>
      )}
      {formSuccess && (
        <div className="text-green-500 font-bold text-sm text-center py-2 px-3 rounded-lg bg-green-500/20 border border-green-500/50 my-2">
          {formSuccess}
        </div>
      )}
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
          className={`pl-12 pr-16 ${inputClasses}`} // Increased right padding for injected icon
 
          required
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
 
          className="absolute right-4 top-1/2 -translate-y-1/2 text-hiremind-purple-accent text-lg opacity-80 hover:opacity-100 focus:outline-none z-10 
            px-2 py-1 rounded-full transition-colors 
            ${theme === 'dark' ? 'bg-hiremind-element-dark/80' : 'bg-hiremind-input-bg-light/80'}" // Added background and padding for button

        >
          {showPassword ? <FiEyeOff /> : <FiEye />}
        </button>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full py-3 rounded-xl font-semibold shadow-lg transition-all duration-300 
          bg-hiremind-purple-accent hover:bg-hiremind-purple-accent/90 text-black focus:outline-none focus:ring-2 focus:ring-hiremind-purple-accent focus:ring-opacity-80"
          disabled={isLoading} 
      >
        {isLoading ? 'Creating Account...' : 'CREATE ACCOUNT'} 
      </button>
    </form>
  );
};

export default SignUpForm;