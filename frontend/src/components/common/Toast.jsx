import { useEffect, useState } from "react";

const ICONS = {
  success: "✓",
  error: "✕",
  info: "ℹ",
};

const COLORS = {
  success: "bg-green-50 border-green-400 text-green-800",
  error: "bg-red-50 border-red-400 text-red-800",
  info: "bg-blue-50 border-blue-400 text-blue-800",
};

/**
 * Toast 알림 컴포넌트.
 * @param {string}  message  - 표시할 메시지
 * @param {"success"|"error"|"info"} type - 알림 유형
 * @param {number}  duration - 자동 닫힘 시간(ms), 기본 3000
 * @param {Function} onClose - 닫힐 때 콜백
 */
export default function Toast({ message, type = "info", duration = 3000, onClose }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onClose?.();
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  if (!visible) return null;

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-lg border px-4 py-3 shadow-md transition-opacity ${COLORS[type]}`}
    >
      <span className="font-bold">{ICONS[type]}</span>
      <p className="text-sm font-medium">{message}</p>
      <button
        onClick={() => { setVisible(false); onClose?.(); }}
        className="ml-2 text-current opacity-60 hover:opacity-100"
      >
        ✕
      </button>
    </div>
  );
}
