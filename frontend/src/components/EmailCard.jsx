import { PRIORITY_STYLES, CATEGORY_STYLES } from "../utils/ui/mini-styles";

export default function EmailCard({ email, isNew }) {
  return (
    <div
      className={`
        relative rounded-2xl border bg-white/3 backdrop-blur-xl p-4
        hover:bg-white/3 hover:-translate-y-0.5
        transition-all duration-300 animate-fadeIn
        ${isNew ? "border-indigo-500/40 shadow-[0_0_20px_rgba(99,102,241,0.15)]" : "border-white/[0.07]"}
      `}
    >
      {/* top row */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-slate-200 leading-snug truncate">
            {email.subject}
          </p>
          <p className="text-xs text-slate-500 mt-0.5 truncate">
            {email.sender}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          <span
            className={`text-[10px] font-semibold px-2.5 py-1 rounded-full ${PRIORITY_STYLES[email.priority]}`}
          >
            {email.priority}
          </span>
          {isNew && (
            <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 animate-pulse">
              NEW
            </span>
          )}
        </div>
      </div>

      {/* category */}
      <span
        className={`inline-block text-[10px] font-medium px-2 py-0.5 rounded-md mb-2.5 ${CATEGORY_STYLES[email.category] || CATEGORY_STYLES.OTHER}`}
      >
        {email.category?.replace(/_/g, " ")}
      </span>

      {/* reason */}
      <p className="text-xs text-slate-400 leading-relaxed mb-3">
        {email.reason}
      </p>

      {/* time */}
      <p className="text-[11px] text-slate-600">
        {new Date(email.received_at).toLocaleString()}
      </p>
    </div>
  );
}
