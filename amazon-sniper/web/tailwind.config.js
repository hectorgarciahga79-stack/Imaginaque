/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: { 950: "#07080a", 900: "#0c0e11", 850: "#111418", 800: "#161a1f", 700: "#20262d", 600: "#2c343d", 500: "#46515d", 400: "#6b7785", 300: "#98a3af", 200: "#c4ccd4", 100: "#e7ecf0" },
        lock: { DEFAULT: "#38f5a0", dim: "#1c7a52" },
        heat: { DEFAULT: "#ff4d5e", dim: "#7a2430" },
        warn: { DEFAULT: "#ffb547", dim: "#7a5620" },
        cyan: { DEFAULT: "#5cc8ff" },
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
      },
    },
  },
  plugins: [],
};
