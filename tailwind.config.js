/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      white: '#ffffff',
      black: '#000000',

      /* ── Core surfaces ─────────────────────────────────── */
      'void':       '#06060e',
      'surface-0':  '#0a0a16',
      'surface-1':  '#0f0f1e',
      'surface-2':  '#161628',
      'surface-3':  '#1e1e38',

      /* ── Accent ────────────────────────────────────────── */
      'accent':     '#00d4ff',
      'accent-dim': '#0099cc',
      'accent-muted':'rgba(0,212,255,0.15)',

      /* ── Signal colors ─────────────────────────────────── */
      'danger':     '#ff4d6a',
      'danger-dim': '#cc3d55',
      'warn':       '#ff8c42',
      'warn-dim':   '#cc7035',
      'success':    '#22c55e',
      'success-dim':'#1a9e4b',
      'purple':     '#a855f7',
      'purple-dim': '#7e3fba',

      /* ── Neutrals ──────────────────────────────────────── */
      gray: {
        50:  '#f9fafb',
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

      /* ── Legacy aliases (so old classnames still work) ── */
      'dark-charcoal':      '#0f0f1e',
      'darker-charcoal':    '#06060e',
      'electric-blue':      '#00d4ff',
      'electric-blue-dark': '#0099cc',
      'warning-orange':     '#ff8c42',
      'warning-orange-dark':'#cc7035',
      'cyber-gray':         '#161628',
      'cyber-gray-light':   '#1e1e38',
      'cyber-dark':         '#06060e',
      'cyber-card':         '#0f0f1e',

      /* ── Extended palette for Tailwind classes ─────────── */
      red:    { 300:'#fca5a5', 400:'#f87171', 500:'#ef4444', 600:'#dc2626', 700:'#b91c1c', 900:'#7f1d1d' },
      orange: { 300:'#fdba74', 700:'#c2410c', 900:'#7c2d12' },
      green:  { 300:'#86efac', 400:'#4ade80', 500:'#22c55e', 700:'#15803d', 900:'#14532d' },
      blue:   { 400:'#60a5fa', 700:'#1d4ed8', 900:'#1e3a8a' },
      yellow: { 400:'#facc15', 500:'#eab308' },
      cyan:   { 400:'#22d3ee', 500:'#06b6d4' },
    },
    extend: {
      boxShadow: {
        'glow-sm':  '0 0 15px rgba(0,212,255,0.12)',
        'glow':     '0 0 30px rgba(0,212,255,0.18)',
        'glow-lg':  '0 0 60px rgba(0,212,255,0.22)',
        'glow-danger': '0 0 30px rgba(255,77,106,0.2)',
      },
      borderRadius: {
        '2xl': '16px',
        '3xl': '20px',
        '4xl': '24px',
      },
      maxWidth: {
        '6xl': '72rem',
        '7xl': '80rem',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
};
