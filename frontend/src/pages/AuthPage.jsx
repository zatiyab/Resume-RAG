import React, { useState } from 'react';
import { useTheme } from '../contexts/ThemeContext.jsx';
import { FiSun, FiMoon, FiShield, FiZap, FiUsers, FiArrowRight } from 'react-icons/fi';
import SignUpForm from '../components/SignUpForm.jsx';
import LoginForm from '../components/LoginForm.jsx';

const AuthPage = ({ onLoginSuccess }) => {
  const { theme, toggleTheme } = useTheme();
  const [isSignUp, setIsSignUp] = useState(true);

  const isDark = theme === 'dark';

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950' : 'bg-gradient-to-b from-white via-slate-50 to-white'}`}>
      <div className={`sticky top-0 z-30 backdrop-blur-md border-b transition-colors duration-300 ${isDark ? 'bg-slate-950/80 border-white/5' : 'bg-white/80 border-slate-200'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <button
            onClick={() => window.history.back()}
            className={`text-sm font-medium transition-colors ${isDark ? 'text-slate-300 hover:text-white' : 'text-slate-700 hover:text-slate-900'}`}
          >
            Back
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <span className="text-white font-bold text-sm">HM</span>
            </div>
            <span className={`text-xl font-bold bg-gradient-to-r text-transparent bg-clip-text ${isDark ? 'from-emerald-400 to-teal-300' : 'from-emerald-600 to-teal-500'}`}>
              HireMind
            </span>
          </div>
          <button
            onClick={toggleTheme}
            className={`p-2 rounded-full transition-colors ${isDark ? 'bg-white/10 hover:bg-white/20 text-slate-300' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'}`}
          >
            {isDark ? <FiSun size={18} /> : <FiMoon size={18} />}
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
        <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-8 items-stretch">
          <section className="hidden lg:flex flex-col justify-between rounded-3xl border p-8 xl:p-10 shadow-2xl shadow-black/10 overflow-hidden relative ${isDark ? 'border-white/10 bg-slate-950/70' : 'border-slate-200 bg-white'}">
            <div className={`absolute inset-0 ${isDark ? 'bg-[radial-gradient(circle_at_20%_20%,rgba(16,185,129,0.16),transparent_32%),radial-gradient(circle_at_80%_0%,rgba(20,184,166,0.15),transparent_28%)]' : 'bg-[radial-gradient(circle_at_20%_20%,rgba(16,185,129,0.12),transparent_32%),radial-gradient(circle_at_80%_0%,rgba(20,184,166,0.10),transparent_28%)]'}`} />
            <div className="relative z-10 space-y-8">
              <div className="space-y-4 max-w-xl">
                <p className={`text-xs uppercase tracking-[0.28em] ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Welcome to HireMind</p>
                <h1 className={`text-5xl font-bold leading-tight ${isDark ? 'text-white' : 'text-slate-900'}`}>
                  AI recruitment that feels fast, focused, and polished.
                </h1>
                <p className={`text-lg leading-8 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                  Sign in to continue matching resumes, managing chat groups, and reviewing candidate insight in one clean workspace.
                </p>
              </div>

              <div className="grid sm:grid-cols-3 gap-4">
                {[
                  { icon: FiShield, title: 'Secure', text: 'Protected login and encrypted access.' },
                  { icon: FiUsers, title: 'Organized', text: 'Keep every search in its own chat group.' },
                  { icon: FiZap, title: 'Fast', text: 'Get resume matches in seconds.' },
                ].map((item) => (
                  <div key={item.title} className={`rounded-2xl p-4 border backdrop-blur-sm ${isDark ? 'bg-white/5 border-white/10' : 'bg-slate-50 border-slate-200'}`}>
                    <item.icon className="text-emerald-500 mb-3" size={22} />
                    <p className={`font-semibold mb-1 ${isDark ? 'text-white' : 'text-slate-900'}`}>{item.title}</p>
                    <p className={`text-sm leading-6 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{item.text}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative z-10 mt-10 flex items-center gap-3">
              <button
                onClick={() => setIsSignUp(false)}
                className="px-5 py-3 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold flex items-center gap-2 hover:shadow-lg hover:shadow-emerald-500/30 transition-all hover:-translate-y-0.5 active:scale-95"
              >
                Login <FiArrowRight />
              </button>
              <button
                onClick={() => setIsSignUp(true)}
                className={`px-5 py-3 rounded-lg border font-semibold transition-colors ${isDark ? 'border-white/10 text-slate-200 hover:bg-white/10' : 'border-slate-200 text-slate-700 hover:bg-slate-50'}`}
              >
                Create account
              </button>
            </div>
          </section>

          <section className="flex items-center justify-center">
            <div className={`w-full max-w-xl rounded-3xl border shadow-2xl backdrop-blur-md p-6 sm:p-8 ${isDark ? 'bg-slate-950/85 border-white/10' : 'bg-white/90 border-slate-200'}`}>
              <div className="mb-6 space-y-3">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className={`text-xs uppercase tracking-[0.24em] ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Account access</p>
                    <h2 className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      {isSignUp ? 'Create your account' : 'Welcome back'}
                    </h2>
                  </div>
                  <div className={`inline-flex rounded-full p-1 border ${isDark ? 'border-white/10 bg-white/5' : 'border-slate-200 bg-slate-50'}`}>
                    <button
                      onClick={() => setIsSignUp(false)}
                      className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${!isSignUp ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white' : isDark ? 'text-slate-300 hover:text-white' : 'text-slate-600 hover:text-slate-900'}`}
                    >
                      Login
                    </button>
                    <button
                      onClick={() => setIsSignUp(true)}
                      className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${isSignUp ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white' : isDark ? 'text-slate-300 hover:text-white' : 'text-slate-600 hover:text-slate-900'}`}
                    >
                      Sign up
                    </button>
                  </div>
                </div>
                <p className={`${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                  {isSignUp ? 'Start a fresh workspace for candidate search and resume matching.' : 'Pick up where you left off and return to your chat groups.'}
                </p>
              </div>

              {isSignUp ? (
                <SignUpForm setIsSignUp={setIsSignUp} />
              ) : (
                <LoginForm onLoginSuccess={onLoginSuccess} />
              )}

              <div className="mt-6 text-center">
                <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                  {isSignUp ? 'Already have an account?' : "Don\'t have an account?"}{' '}
                  <button
                    onClick={() => setIsSignUp(!isSignUp)}
                    className="font-semibold text-emerald-500 hover:text-teal-500 transition-colors"
                  >
                    {isSignUp ? 'Sign in' : 'Sign up'}
                  </button>
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;