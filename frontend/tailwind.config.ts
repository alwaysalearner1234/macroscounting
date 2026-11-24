import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        midnight: "#090c12",
        panel: "#111722",
        line: "#242d3b",
        cloud9: "#58b9e8",
      },
    },
  },
  plugins: [],
};

export default config;