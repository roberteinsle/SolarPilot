/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'solar-yellow': '#FFD700',
        'battery-green': '#10B981',
        'grid-blue': '#3B82F6',
        'house-gray': '#6B7280',
      },
    },
  },
  plugins: [],
}
