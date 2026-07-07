/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        kinetix: {
          50: '#e8f4fd',
          100: '#d1e9fb',
          200: '#a3d3f7',
          300: '#6bb8f0',
          400: '#3a9ae8',
          500: '#2fc6f6',
          600: '#1a8cd8',
          700: '#1569a8',
          800: '#104d7a',
          900: '#0b3352',
        },
      },
    },
  },
  plugins: [],
}
