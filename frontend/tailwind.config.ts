import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        graphite: "#17202a",
        panel: "#ffffff",
        line: "#d8e0e8",
        field: "#f5f7fa",
        teal: "#0f8b8d",
        cyan: "#00a3b5",
        amber: "#d97706",
        danger: "#dc2626",
      },
      boxShadow: {
        panel: "0 1px 2px rgba(15, 23, 42, 0.05)",
      },
    },
  },
  plugins: [],
};

export default config;
