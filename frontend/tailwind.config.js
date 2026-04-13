/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "Noto Sans KR", "sans-serif"],
      },
      colors: {
        // 카테고리 배지 커스텀 색상 (PRD §8.2)
        category: {
          food:      "#6366F1",
          dining:    "#F59E0B",
          shopping:  "#EC4899",
          transport: "#14B8A6",
          medical:   "#22C55E",
          culture:   "#8B5CF6",
          education: "#F97316",
          etc:       "#94A3B8",
        },
      },
    },
  },
  plugins: [],
}

