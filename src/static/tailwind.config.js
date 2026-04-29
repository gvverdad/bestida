/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../templates/frontend/**/*.html",
            "../static/js/components/**/*.js",
            "../static/scripts/**/*.js",
            "../static/icons/*.js",
            "../static/icons/*.svg"],
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("daisyui")
  ],
  daisyui: {
    themes: ["corporate", "dark"],
  },
}
