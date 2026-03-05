/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      white: '#ffffff',
      black: '#000000',
      'dark-charcoal': '#1a1a2e',
      'darker-charcoal': '#0f0f1e',
      'electric-blue': '#00d4ff',
      'electric-blue-dark': '#0099cc',
      'warning-orange': '#ff6b35',
      'warning-orange-dark': '#cc5428',
      'cyber-gray': '#16213e',
      'cyber-gray-light': '#2a2a3e',
      'cyber-dark': '#0f0f1e',
      'cyber-card': '#1a1a2e',
      gray: {
        50: '#f9fafb',
        100: '#f3f4f6',
        200: '#e5e7eb',
        300: '#d1d5db',
        400: '#9ca3af',
        500: '#6b7280',
        600: '#4b5563',
        700: '#374151',
        800: '#1f2937',
        900: '#111827',
      },
      red: {
        300: '#fca5a5',
        400: '#f87171',
        500: '#ef4444',
        600: '#dc2626',
        700: '#b91c1c',
        900: '#7f1d1d',
      },
      orange: {
        300: '#fdba74',
        700: '#c2410c',
        900: '#7c2d12',
      },
      green: {
        300: '#86efac',
        400: '#4ade80',
        500: '#22c55e',
        700: '#15803d',
        900: '#14532d',
      },
      blue: {
        700: '#1d4ed8',
        900: '#1e3a8a',
      },
      yellow: {
        400: '#facc15',
        500: '#eab308',
      },
      purple: {
        300: '#d8b4fe',
        900: '#581c87',
      },
      cyan: {
        500: '#06b6d4',
      },
    },
    extend: {
      boxShadow: {
        'cyber-glow': '0 0 20px rgba(0, 212, 255, 0.3)',
        'cyber-glow-orange': '0 0 20px rgba(255, 107, 53, 0.3)',
        'cyber-intense': '0 0 30px rgba(0, 212, 255, 0.5)',
      },
      maxWidth: {
        '6xl': '72rem',
        '7xl': '80rem',
      },
    },
  },
  plugins: [],
}
