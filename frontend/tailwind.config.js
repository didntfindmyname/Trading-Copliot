/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172026",
        line: "#d8dee4",
        signal: "#0f766e",
        risk: "#b91c1c",
        steel: "#334155"
      }
    }
  },
  plugins: []
};

