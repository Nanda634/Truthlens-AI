/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: {
          950: '#05070a',
          900: '#0b0f14',
          800: '#111722',
          700: '#1a2233',
          600: '#28334a',
        },
        accent: {
          500: '#22d3ee',
          600: '#0ea5b7',
        },
      },
    },
  },
  plugins: [],
}
