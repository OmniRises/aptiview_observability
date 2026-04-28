import { formatDateTime } from '../utils/formatters'

export function IncidentCard({ incident, services }) {
  const affected = services.filter((item) => item.status === 'outage').map((item) => item.name)

  if (!incident?.open_incident_id) {
    return (
      <section className="rounded-xl border border-[#2a4570] bg-[#0b2647] p-6 shadow-[0_10px_30px_rgba(2,18,36,0.45)]">
        <h2 className="text-lg font-semibold text-emerald-300">🟢 No ongoing incidents</h2>
      </section>
    )
  }

  return (
    <section className="rounded-xl border border-red-500/40 bg-red-500/10 p-6 shadow-[0_10px_30px_rgba(2,18,36,0.45)]">
      <h2 className="text-lg font-semibold text-red-100">🔴 Ongoing Incident</h2>
      <p className="mt-2 text-sm text-red-100">Start time: {formatDateTime(incident.open_since)}</p>
      <p className="mt-1 text-sm text-red-100">
        Affected services: {affected.length ? affected.join(', ') : 'Investigating'}
      </p>
      <p className="mt-1 text-sm text-red-100">Status summary: Active service outage detected</p>
    </section>
  )
}
