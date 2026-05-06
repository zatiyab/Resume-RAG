import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { FiMenu, FiX, FiMoon, FiSun, FiArrowRight, FiUploadCloud, FiFilter, FiZap } from 'react-icons/fi';
import { useState } from 'react';

const HomePage = () => {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLoginClick = () => {
    navigate('/auth');
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      theme === 'dark' ? 'bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950' : 'bg-gradient-to-b from-white via-slate-50 to-white'
    }`}>
      {/* Navigation Bar */}
      <nav className={`sticky top-0 z-50 backdrop-blur-md transition-colors duration-300 ${
        theme === 'dark' 
          ? 'bg-slate-950/80 border-b border-white/5' 
          : 'bg-white/80 border-b border-slate-200'
      }`}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">HM</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-300 text-transparent bg-clip-text">
              HireMind
            </span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <button 
              onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}
              className={`text-sm font-medium hover:text-emerald-600 transition-colors ${
                theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
              }`}
            >
              Features
            </button>
            <button 
              onClick={toggleTheme}
              className={`p-2 rounded-full transition-colors ${
                theme === 'dark' 
                  ? 'bg-white/10 hover:bg-white/20 text-slate-300' 
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
              }`}
            >
              {theme === 'dark' ? <FiSun size={20} /> : <FiMoon size={20} />}
            </button>
            <button
              onClick={handleLoginClick}
              className="px-6 py-2 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold hover:shadow-lg hover:shadow-emerald-500/50 transition-all hover:-translate-y-0.5 active:scale-95"
            >
              Login / Sign Up
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-4">
            <button 
              onClick={toggleTheme}
              className={`p-2 rounded-full transition-colors ${
                theme === 'dark' 
                  ? 'bg-white/10 hover:bg-white/20 text-slate-300' 
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
              }`}
            >
              {theme === 'dark' ? <FiSun size={20} /> : <FiMoon size={20} />}
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className={`p-2 rounded-lg transition-colors ${
                theme === 'dark' 
                  ? 'bg-white/10 hover:bg-white/20 text-slate-300' 
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
              }`}
            >
              {mobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className={`md:hidden border-t ${
            theme === 'dark' ? 'border-white/5 bg-slate-900/50' : 'border-slate-200 bg-slate-50/50'
          } backdrop-blur-sm`}>
            <div className="px-4 py-4 space-y-3">
              <button 
                onClick={() => {
                  document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
                  setMobileMenuOpen(false);
                }}
                className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                  theme === 'dark' 
                    ? 'text-slate-300 hover:bg-white/10' 
                    : 'text-slate-700 hover:bg-slate-200'
                }`}
              >
                Features
              </button>
              <button
                onClick={() => {
                  handleLoginClick();
                  setMobileMenuOpen(false);
                }}
                className="w-full px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold"
              >
                Login / Sign Up
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h1 className={`text-5xl sm:text-6xl font-bold leading-tight ${
                theme === 'dark' 
                  ? 'text-white' 
                  : 'text-slate-900'
              }`}>
                AI-Powered <span className="bg-gradient-to-r from-emerald-500 to-teal-400 text-transparent bg-clip-text">Recruitment</span> Assistant
              </h1>
              <p className={`text-xl ${
                theme === 'dark' 
                  ? 'text-slate-400' 
                  : 'text-slate-600'
              }`}>
                HireMind helps you find the perfect candidates instantly. Upload resumes, ask questions, and let AI match them to your job requirements.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={handleLoginClick}
                className="px-8 py-3 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-emerald-500/50 transition-all hover:-translate-y-1 active:scale-95"
              >
                Get Started <FiArrowRight size={20} />
              </button>
              <button
                onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}
                className={`px-8 py-3 rounded-lg font-semibold border-2 transition-all hover:-translate-y-1 active:scale-95 ${
                  theme === 'dark' 
                    ? 'border-emerald-500/50 text-emerald-400 hover:border-emerald-500 hover:bg-emerald-500/10' 
                    : 'border-emerald-500 text-emerald-600 hover:bg-emerald-50'
                }`}
              >
                Learn More
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 pt-8 border-t border-white/10">
              <div>
                <p className="text-3xl font-bold bg-gradient-to-r from-emerald-500 to-teal-400 text-transparent bg-clip-text">99%</p>
                <p className={`text-sm ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>Accuracy</p>
              </div>
              <div>
                <p className="text-3xl font-bold bg-gradient-to-r from-emerald-500 to-teal-400 text-transparent bg-clip-text">&lt;5s</p>
                <p className={`text-sm ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>Response Time</p>
              </div>
              <div>
                <p className="text-3xl font-bold bg-gradient-to-r from-emerald-500 to-teal-400 text-transparent bg-clip-text">24/7</p>
                <p className={`text-sm ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>Availability</p>
              </div>
            </div>
          </div>

          {/* Right Visual */}
          <div className="relative hidden md:block">
            <div className="relative w-full h-96 rounded-2xl overflow-hidden backdrop-blur-sm border border-white/10">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/20 to-teal-500/20"></div>
              <div className="absolute top-10 left-10 right-10 space-y-4">
                <div className="flex gap-2 p-3 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm">
                  <FiUploadCloud className="text-emerald-400 flex-shrink-0 mt-1" size={20} />
                  <div>
                    <p className={`text-sm font-semibold ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>Upload Resumes</p>
                    <p className={`text-xs ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>Drag & drop or browse</p>
                  </div>
                </div>
                <div className="flex gap-2 p-3 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm">
                  <FiFilter className="text-teal-400 flex-shrink-0 mt-1" size={20} />
                  <div>
                    <p className={`text-sm font-semibold ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>Smart Matching</p>
                    <p className={`text-xs ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>AI-powered analysis</p>
                  </div>
                </div>
                <div className="flex gap-2 p-3 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm">
                  <FiZap className="text-yellow-400 flex-shrink-0 mt-1" size={20} />
                  <div>
                    <p className={`text-sm font-semibold ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>Instant Results</p>
                    <p className={`text-xs ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>Get answers in seconds</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className={`py-20 transition-colors duration-300 ${
        theme === 'dark' 
          ? 'bg-slate-900/50' 
          : 'bg-slate-100/50'
      }`}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 space-y-4">
            <h2 className={`text-4xl sm:text-5xl font-bold ${
              theme === 'dark' ? 'text-white' : 'text-slate-900'
            }`}>
              Why Choose <span className="bg-gradient-to-r from-emerald-500 to-teal-400 text-transparent bg-clip-text">HireMind</span>?
            </h2>
            <p className={`text-xl ${
              theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
            }`}>
              Everything you need to revolutionize your hiring process
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: FiUploadCloud,
                title: 'Resume Management',
                description: 'Easily upload and organize resumes. Support for PDF, DOC, and DOCX formats.'
              },
              {
                icon: FiFilter,
                title: 'Smart Filtering',
                description: 'Ask questions about candidates and get AI-powered answers in seconds.'
              },
              {
                icon: FiZap,
                title: 'Instant Matching',
                description: 'Match job descriptions with candidates automatically using advanced AI.'
              },
              {
                icon: FiZap,
                title: '24/7 Availability',
                description: 'Access your recruitment assistant anytime, anywhere, from any device.'
              },
              {
                icon: FiFilter,
                title: 'Secure Storage',
                description: 'Your data is encrypted and stored securely on enterprise-grade servers.'
              },
              {
                icon: FiUploadCloud,
                title: 'Export & Download',
                description: 'Download candidate information and matched results in bulk.'
              }
            ].map((feature, idx) => (
              <div
                key={idx}
                className={`p-6 rounded-xl border transition-all hover:-translate-y-2 hover:shadow-lg ${
                  theme === 'dark'
                    ? 'bg-slate-800/50 border-white/10 hover:border-emerald-500/50 hover:shadow-emerald-500/20'
                    : 'bg-white border-slate-200 hover:border-emerald-500 hover:shadow-emerald-500/20'
                }`}
              >
                <feature.icon className="text-emerald-500 mb-4" size={28} />
                <h3 className={`text-lg font-semibold mb-2 ${
                  theme === 'dark' ? 'text-white' : 'text-slate-900'
                }`}>
                  {feature.title}
                </h3>
                <p className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className={`rounded-2xl p-12 text-center border ${
          theme === 'dark'
            ? 'bg-gradient-to-r from-emerald-950/50 to-teal-950/50 border-emerald-500/20'
            : 'bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200'
        }`}>
          <h2 className={`text-4xl font-bold mb-4 ${
            theme === 'dark' ? 'text-white' : 'text-slate-900'
          }`}>
            Ready to Transform Your Hiring?
          </h2>
          <p className={`text-xl mb-8 ${
            theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
          }`}>
            Join hundreds of companies using HireMind to find their perfect candidates
          </p>
          <button
            onClick={handleLoginClick}
            className="px-8 py-3 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold hover:shadow-lg hover:shadow-emerald-500/50 transition-all hover:-translate-y-1 active:scale-95"
          >
            Get Started Now <FiArrowRight className="inline ml-2" size={20} />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className={`border-t transition-colors duration-300 ${
        theme === 'dark' 
          ? 'bg-slate-950 border-white/5' 
          : 'bg-slate-50 border-slate-200'
      }`}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
          <p className={`mb-4 font-semibold bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-300 text-transparent bg-clip-text`}>
            HireMind AI
          </p>
          <p className={`text-sm ${
            theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
          }`}>
            © 2026 HireMind. All rights reserved. Revolutionizing recruitment with AI.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
