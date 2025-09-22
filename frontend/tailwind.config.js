/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0f172a",
          light: "#273c75"
        },
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
