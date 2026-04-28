function pointColor(status) {
  if (status === 'outage') return 'bg-red-400'
  if (status === 'degraded') return 'bg-amber-400'
  return 'bg-emerald-400'
}

export function UptimeStrip({ events }) {
  const recent = events
    .slice()
    .sort((a, b) => new Date(a.checked_at) - new Date(b.checked_at))
    .slice(-80)

  const operationalCount = recent.filter((item) => item.status === 'operational').length
  const uptime = recent.length ? ((operationalCount / recent.length) * 100).toFixed(2) : '0.00'

  return (
    <section className="rounded-xl border border-[#2a4570] bg-[#0b2647] p-5 shadow-[0_10px_30px_rgba(2,18,36,0.45)]">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold text-slate-100">Live Uptime</h2>
        <p className="text-sm text-slate-300">{uptime}% from recent checks</p>
      </div>
      <div className="flex flex-wrap gap-1">
        {recent.map((item, index) => (
          <span
            key={`${item.service}-${item.checked_at}-${index}`}
            className={`h-4 w-1.5 rounded-sm ${pointColor(item.status)}`}
            title={`${item.service}: ${item.status}`}
          />
        ))}
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-slate-300">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
          <span>Operational</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-amber-400" />
          <span>Degraded</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
          <span>Outage</span>
        </div>
      </div>
    </section>
  )
}
