/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme colors matching the existing design
        dark: {
          bg: '#1a1a2e',
          surface: '#16213e',
          border: 'rgba(255, 255, 255, 0.1)',
        },
        accent: {
          cyan: '#00d4ff',
          green: '#00ff88',
          warning: '#ffc107',
          error: '#ff5252',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
