// frontend/tailwind.config.js (Colors Section CORRECTED)
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        hiremind: {
          // Core Palette
          'darkblue': '#0A1118',    // Deep Blue-Black for dark backgrounds
          'emerald-primary': '#10B981', // Solid Emerald
          'teal-primary': '#14B8A6',    // Solid Teal
          
          // Dark Mode Specific UI elements
          'bg-dark': '#060B11',     // Ultra deep background
          'sidebar-dark': '#0A1118',// Clean dark sidebar
          'element-dark': '#111827',// Dark elements (cards, input fields)
          'text-dark-primary': '#F8FAFC', // White-ish text
          'text-dark-secondary': '#94A3B8', // Grey-ish text

          // Light Mode Specific UI elements
          'bg-light': '#F8FAFC',    // Cool, ultra-light slate
          'sidebar-light': '#FFFFFF',// Pure white 
          'element-light': '#F1F5F9',// Clean slate for light elements
          'text-light-primary': '#0F172A', // Very dark slate for primary text
          'text-light-secondary': '#64748B',// Soft text

          // Accents 
          'accent-teal': '#14B8A6',
          'accent-emerald': '#10B981',
          
          // Legacy Auth mapping to prevent breaks temporarily
          'purple-primary': '#060B11', 
          'purple-accent': '#10B981', 
          'light-bg-card': '#FFFFFF',
          'input-bg-light': '#F8FAFC', 
          'input-border-light': '#E2E8F0', 
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