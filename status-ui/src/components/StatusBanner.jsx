import { formatDateTime, statusBadge } from '../utils/formatters'

export function StatusBanner({ overallStatus, lastUpdatedAt }) {
  const badge = statusBadge(overallStatus)

  return (
    <section className={`rounded-xl border p-6 shadow-[0_10px_30px_rgba(2,18,36,0.45)] ${badge.color}`}>
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          {badge.dot} {badge.label}
        </h1>
        <p className="text-sm font-medium text-slate-200">Last updated: {formatDateTime(lastUpdatedAt)}</p>
      </div>
    </section>
  )
}
