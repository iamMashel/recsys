import type { Config } from "tailwindcss"

export default {
  content: [
    "./components/**/*.{vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.ts",
    "./app.vue",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#fdf2ff",
          500: "#a855f7",
          600: "#9333ea",
          700: "#7e22ce",
          900: "#581c87",
        },
      },
    },
  },
} satisfies Config
