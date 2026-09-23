/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        base: {
          950: "#070B14",
          900: "#0B1220",
          800: "#111A2E",
          700: "#182338",
          600: "#223049",
          500: "#334361",
        },
        ink: {
          100: "#E8ECF4",
          300: "#B7C1D6",
          500: "#8291AC",
        },
        brand: {
          400: "#5EEAD4",
          500: "#22D3EE",
          600: "#0EA5B7",
        },
        risk: {
          low: "#34D399",
          medium: "#FBBF24",
          high: "#FB7185",
          critical: "#EF4444",
        },
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
      },
    },
  },
  plugins: [],
};
