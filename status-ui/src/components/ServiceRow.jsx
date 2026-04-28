import { formatStatusLabel } from '../utils/formatters'

function statusPill(status) {
  if (status === 'outage') return 'bg-red-500/20 text-red-100 border border-red-400/40'
  if (status === 'degraded') return 'bg-amber-500/20 text-amber-100 border border-amber-400/40'
  return 'bg-emerald-500/20 text-emerald-100 border border-emerald-400/40'
}

function statusIcon(status) {
  if (status === 'outage') return '🔴'
  if (status === 'degraded') return '🟡'
  return '🟢'
}

export function ServiceRow({ service }) {
  return (
    <li className="rounded-lg border border-[#2a4570] bg-[#0f3157] p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-base font-semibold text-slate-100">{service.name}</p>
          <p className="mt-1 text-sm text-slate-300">
            {service.latency != null ? `latency: ${service.latency}ms` : 'latency: N/A'}
          </p>
          <p className="mt-1 text-sm text-slate-300">{service.message || 'No message'}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-medium ${statusPill(service.status)}`}>
          {statusIcon(service.status)} {formatStatusLabel(service.status)}
        </span>
      </div>
    </li>
  )
}
