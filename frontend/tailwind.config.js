/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
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
        app: {
          bg: 'rgb(var(--app-bg) / <alpha-value>)',
          surface: 'rgb(var(--app-surface) / <alpha-value>)',
          muted: 'rgb(var(--app-muted) / <alpha-value>)',
          border: 'rgb(var(--app-border) / <alpha-value>)',
          text: 'rgb(var(--app-text) / <alpha-value>)',
          'text-secondary': 'rgb(var(--app-text-secondary) / <alpha-value>)',
          'text-muted': 'rgb(var(--app-text-muted) / <alpha-value>)',
          overlay: 'rgb(var(--app-overlay) / <alpha-value>)',
          header: {
            bg: 'rgb(var(--app-header-bg) / <alpha-value>)',
            text: 'rgb(var(--app-header-text) / <alpha-value>)',
            border: 'rgb(var(--app-header-border) / <alpha-value>)',
          },
          control: {
            bg: 'rgb(var(--app-control-bg) / <alpha-value>)',
            border: 'rgb(var(--app-control-border) / <alpha-value>)',
            active: 'rgb(var(--app-control-active) / <alpha-value>)',
            inactive: 'rgb(var(--app-control-inactive) / <alpha-value>)',
          },
        },
      },
    },
  },
  plugins: [],
}
