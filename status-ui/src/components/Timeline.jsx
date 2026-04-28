import { formatDateTime, formatStatusLabel } from '../utils/formatters'

export function Timeline({ events }) {
  return (
    <section className="rounded-xl border border-[#2a4570] bg-[#0b2647] p-6 shadow-[0_10px_30px_rgba(2,18,36,0.45)]">
      <h2 className="mb-4 text-lg font-semibold text-slate-100">Timeline</h2>
      {events.length === 0 ? (
        <p className="text-sm text-slate-300">No timeline events yet.</p>
      ) : (
        <ul className="space-y-2">
          {events.map((event, index) => (
            <li key={`${event.service}-${event.checked_at}-${index}`} className="text-sm text-slate-200">
              {formatDateTime(event.checked_at)} {event.service} -&gt; {formatStatusLabel(event.status)}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
