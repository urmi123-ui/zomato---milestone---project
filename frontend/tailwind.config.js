/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#fcf9f8",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f6f3f2",
        "surface-container": "#f0eded",
        "surface-container-high": "#eae7e7",
        "surface-container-highest": "#e5e2e1",
        "on-surface": "#1b1b1b",
        "on-surface-variant": "#5b403f",
        outline: "#8f6f6e",
        "outline-variant": "#e4bebc",
        primary: "#b7122a",
        "on-primary": "#ffffff",
        "primary-container": "#db313f",
        "secondary-container": "#feb700",
        "on-secondary-container": "#6b4b00",
        tertiary: "#0058bd",
        "tertiary-container": "#1470e8",
        "on-tertiary-container": "#fefcff",
        "tertiary-fixed": "#d8e2ff",
        "on-tertiary-fixed": "#001a41",
        "tertiary-fixed-dim": "#adc6ff",
        background: "#fcf9f8",
        "on-background": "#1b1b1b",
        error: "#ba1a1a",
        "error-container": "#ffdad6",
        "on-error-container": "#93000a",
      },
      spacing: {
        "margin-mobile": "16px",
        "margin-desktop": "48px",
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', "system-ui", "sans-serif"],
      },
      borderRadius: {
        card: "16px",
      },
      boxShadow: {
        card: "0 4px 20px rgba(0, 0, 0, 0.05)",
        "card-hover": "0 8px 24px rgba(0, 0, 0, 0.1)",
        featured: "0 8px 32px rgba(226, 55, 68, 0.15)",
        cta: "0 4px 14px rgba(226, 55, 68, 0.3)",
      },
    },
  },
  plugins: [],
};
