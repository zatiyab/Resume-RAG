// frontend/vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react'; // React projects ke liye yeh plugin chahiye
import tailwindcss from '@tailwindcss/vite'; // Tailwind CSS Vite plugin

export default defineConfig({
  plugins: [
    react(), // React support ke liye
    tailwindcss(), // Tailwind CSS plugin integrate kiya
  ],
});