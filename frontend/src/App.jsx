// frontend/HireMind/src/App.js
import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { ThemeProvider} from './contexts/ThemeContext.jsx';
import HomePage from './pages/HomePage.jsx';
import DashboardAppUI from './pages/DashboardAppUI.jsx';
import AuthPage from './pages/AuthPage.jsx';


function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // State to track authentication
  const navigate = useNavigate(); // Initialize navigate outside of context consumer

  // Check auth status on initial load and whenever location changes (from react-router)
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
  }, []); // only run once on mount

  // Function to be called after successful login (from AuthPage)
  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    navigate('/chat'); // ensure single SPA navigation to dashboard after login
  };

  return (
    <ThemeProvider> {/* ThemeProvider wraps the entire app */}
      <Routes>
        {/* Home Page - Public Route */}
        <Route path="/" element={<HomePage />} />

        {/* Route for Authentication Page */}
        <Route path="/auth" element={<AuthPage onLoginSuccess={handleLoginSuccess} />} />

        {/* Protected Route for Dashboard */}
        <Route
          path="/chat"
          element={
            isAuthenticated === null ? (
              <div>Loading...</div>
            ) : isAuthenticated ? (
              <DashboardAppUI />
            ) : (
              <Navigate to="/auth" replace />
            )
          } // Redirect if not authenticated
        />

        {/* Fallback for unknown routes - redirects to home */}
        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </ThemeProvider>
  );
}

export default App;