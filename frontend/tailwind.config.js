/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bmir: {
          midnight: "#071426",
          navy: "#102A43",
          electric: "#2878FF",
          cyan: "#19C7D9",
          slate: "#334E68",
          lightBg: "#F5F7FB",
          darkBg: "#080F1C",
          surfaceDark: "#0D1829",
          cardDark: "#112038",
          borderDark: "#1E3352",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "sans-serif"],
        heading: ["var(--font-manrope)", "Manrope", "sans-serif"],
        display: ["var(--font-jakarta)", "Plus Jakarta Sans", "sans-serif"],
      },
    },
  },
  plugins: [],
};

