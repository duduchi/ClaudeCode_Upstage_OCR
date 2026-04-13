import { NavLink } from "react-router-dom";

const nav = [
  { to: "/",         label: "대시보드",    icon: "📊" },
  { to: "/upload",   label: "영수증 업로드", icon: "📤" },
  { to: "/receipts", label: "지출 내역",    icon: "🧾" },
  { to: "/stats",    label: "통계 분석",    icon: "📈" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 min-h-screen bg-white border-r border-slate-200 flex flex-col">
      {/* 로고 */}
      <div className="h-16 flex items-center px-6 border-b border-slate-200">
        <span className="text-indigo-600 font-bold text-lg">Receipt AI</span>
      </div>

      {/* 네비게이션 */}
      <nav className="flex-1 py-4 space-y-1 px-3">
        {nav.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              [
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-indigo-50 text-indigo-600"
                  : "text-slate-600 hover:bg-slate-100",
              ].join(" ")
            }
          >
            <span>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
