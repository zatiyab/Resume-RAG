// frontend/HireMind/src/App.js
import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { ThemeProvider} from './contexts/ThemeContext.jsx';
import DashboardAppUI from './pages/DashboardAppUI.jsx';
import AuthPage from './pages/AuthPage.jsx';





function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false); // State to track authentication
  const navigate = useNavigate(); // Initialize navigate outside of context consumer

  // Check auth status on initial load and whenever location changes (from react-router)
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token); // Convert token presence to boolean
  }, [navigate]); // Depend on navigate to re-check when URL changes (e.g. from /auth to /)

  // Function to be called after successful login (from AuthPage)
  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    // navigate('/'); // AuthPage's LoginForm already handles this redirection
  };

  return (
    <ThemeProvider> {/* ThemeProvider wraps the entire app */}
      <Routes>
        {/* Route for Authentication Page */}
        <Route path="/auth" element={<AuthPage onLoginSuccess={handleLoginSuccess} />} />

        {/* Protected Route for Dashboard */}
        <Route
          path="/"
          element={isAuthenticated ? <DashboardAppUI /> : <Navigate to="/auth" replace />} // Redirect if not authenticated
        />

        {/* Fallback for unknown routes - redirects to dashboard if authenticated, else to auth */}
        <Route
          path="*"
          element={isAuthenticated ? <Navigate to="/" replace /> : <Navigate to="/auth" replace />}
        />
      </Routes>
    </ThemeProvider>
  );
}

export default App;