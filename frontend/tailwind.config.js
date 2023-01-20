/** @type {import('tailwindcss').Config} */
const percentageWidth = require('tailwindcss-percentage-width');
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/typography"),
    percentageWidth,
  ],
}
