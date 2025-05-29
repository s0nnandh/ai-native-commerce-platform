/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: "#4D7C0F", // Green for plant-powered theme
        secondary: "#78716C", // Earthy tone
        accent: "#059669", // Green accent for eco-friendly emphasis
        background: "#F8FAF5", // Soft natural background
        "text-primary": "#1F2937",
        "text-secondary": "#4B5563",
        "evergreen": "#166534", // Deep green for brand identity
        "sand": "#D6D3D1", // Light sand color for natural feel
        "leaf": "#84CC16", // Bright leaf green for highlights
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      keyframes: {
        shimmer: {
          '100%': { transform: 'translateX(100%)' }
        }
      },
    },
  },
  plugins: [],
}
