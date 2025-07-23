// frontend/src/main.jsx (UPDATED for React Router)
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx'; // App will now contain routing logic
import './index.css';
import { BrowserRouter } from 'react-router-dom'; // Import BrowserRouter

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter> {/* App is wrapped by BrowserRouter */}
      <App />
    </BrowserRouter>
  </React.StrictMode>
);