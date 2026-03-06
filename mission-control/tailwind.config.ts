import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          base: "#0a0c10",
          surface: "#111318",
          card: "#161a22",
          hover: "#1c2030",
          border: "#232838",
        },
        agent: {
          active: "#22c55e",
          idle: "#f59e0b",
          offline: "#6b7280",
        },
        task: {
          backlog: "#6366f1",
          progress: "#3b82f6",
          review: "#f59e0b",
          qa: "#a855f7",
          done: "#22c55e",
        },
        brand: "#4f8ef7",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spin-slow": "spin 3s linear infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
