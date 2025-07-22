// frontend/tailwind.config.js (Colors Section CORRECTED)
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        hiremind: {
          // Core Palette
          'darkblue': '#1A2B3C',    // Deep Blue (Main dark background, text in light mode)
          'beige': '#F5F0E1',       // Creamy Beige (Main light background, text in dark mode)
          
          // Dark Mode Specific UI elements
          'bg-dark': '#12202E',     // Even darker background for main content area
          'sidebar-dark': '#0B151F',// Very dark for sidebar
          'element-dark': '#23384D',// Darker elements (cards, input fields)
          // --- YAHAN CORRECTION HAI ---
          'text-dark-primary': '#F5F0E1', // PRIMARY TEXT IN DARK MODE should be BEIGE
          'text-dark-secondary': '#B0AFAF',// SECONDARY TEXT IN DARK MODE should be LIGHT GREY
          // --- CORRECTION ENDS ---

          // Light Mode Specific UI elements
          'bg-light': '#FDFBF6',    // Very light background for main content area
          'sidebar-light': '#FFFFFF',// Pure white for sidebar
          'element-light': '#E9E5DE',// Lighter beige for elements
          'text-light-primary': '#1A2B3C', // PRIMARY TEXT IN LIGHT MODE should be DARKBLUE
          'text-light-secondary': '#5A6B7C',// SECONDARY TEXT IN LIGHT MODE should be DARKER GREY

          // Accents (for buttons, links, etc.)
          'accent-purple': '#8E6CEF', // Soft Purple
          'accent-green': '#4CAF50',  // Standard Green
          'accent-blue': '#3498DB',   // Standard Blue
        },
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        heading: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}