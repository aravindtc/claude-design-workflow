/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: {
          bg: '#0a0b14',
          surface: '#12131e',
          border: 'rgba(255,255,255,0.08)',
        },
        glass: {
          fill: 'rgba(255,255,255,0.05)',
          'fill-strong': 'rgba(255,255,255,0.08)',
          border: 'rgba(255,255,255,0.1)',
        },
        cta: {
          primary: '#7c3aed',
        },
        accent: {
          violet: '#8b5cf6',
          blue: '#3b82f6',
          cyan: '#06b6d4',
          green: '#4cde7e',
          pink: '#f65c8b',
          orange: '#f6ae3b',
          red: '#f65c5c',
        },
        text: {
          primary: '#ffffff',
          secondary: 'rgba(255,255,255,0.7)',
          muted: 'rgba(255,255,255,0.5)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        18: '4.5rem',
        120: '30rem',
      },
      borderRadius: {
        '4xl': '1.5rem',
      },
      boxShadow: {
        'cta-glow': '0 4px 32px rgba(124,58,237,0.5)',
        subtle: '0 4px 16px rgba(0,0,0,0.3)',
      },
      letterSpacing: {
        hero: '-0.02em',
        h2: '-0.015em',
        h3: '-0.01em',
      },
    },
  },
  plugins: [],
}
