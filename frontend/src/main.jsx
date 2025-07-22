// frontend/src/main.jsx (UPDATED)
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx'; // Ab App hi main component hai
import './index.css'; // Main CSS
import { ThemeProvider } from './contexts/ThemeContext.jsx'; // ThemeProvider ko yahan import karein

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider> {/* ThemeProvider App ko wrap kar raha hai */}
      <App />
    </ThemeProvider>
  </React.StrictMode>
);