// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html', // For project-level templates and app templates
    './**/static/js/**/*.js',    // If you use Tailwind classes in JS
    // Add any other paths where you might use Tailwind classes
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  important: true, // Make all Tailwind utilities use !important
}