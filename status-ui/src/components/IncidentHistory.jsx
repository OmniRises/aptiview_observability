import { formatDateTime, formatServiceName } from '../utils/formatters'

export function IncidentHistory({ incidents }) {
  return (
    <section className="rounded-xl border border-[#2a4570] bg-[#0b2647] p-6 shadow-[0_10px_30px_rgba(2,18,36,0.45)]">
      <h2 className="mb-4 text-lg font-semibold text-slate-100">Incident History</h2>
      {incidents.length === 0 ? (
        <p className="text-sm text-slate-300">No historical incidents found.</p>
      ) : (
        <ul className="space-y-3">
          {incidents.map((incident, index) => (
            <li key={`${incident.start_time}-${index}`} className="rounded-lg border border-[#2a4570] bg-[#0f3157] p-3">
              <p className="text-sm text-slate-200">Start: {formatDateTime(incident.start_time)}</p>
              <p className="text-sm text-slate-200">End: {formatDateTime(incident.end_time)}</p>
              <p className="text-sm text-slate-200">
                Affected: {(incident.affected_services || []).map(formatServiceName).join(', ') || 'Unknown'}
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
