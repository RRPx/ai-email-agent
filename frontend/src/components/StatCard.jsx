export default function StatCard({ label, value, color }) {
  return (
    <div className="rounded-xl border border-white/6 bg-white/3 backdrop-blur-xl p-4 text-center hover:-translate-y-0.5 transition-transform">
      <p className={`text-3xl font-semibold ${color}`}>{value}</p>
      <p className="text-xs text-slate-500 uppercase tracking-wider mt-1">
        {label}
      </p>
    </div>
  );
}
