/**
 * 로딩 스피너 공통 컴포넌트.
 * @param {string} size - "sm" | "md" | "lg" (기본값 "md")
 * @param {string} className - 추가 Tailwind 클래스
 */
export default function LoadingSpinner({ size = "md", className = "" }) {
  const sizeClass = {
    sm: "h-4 w-4 border-2",
    md: "h-8 w-8 border-2",
    lg: "h-12 w-12 border-4",
  }[size];

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div
        className={`${sizeClass} animate-spin rounded-full border-slate-200 border-t-blue-600`}
      />
    </div>
  );
}
