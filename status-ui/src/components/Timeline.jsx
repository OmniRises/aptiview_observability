import { useMemo } from 'react'

import { formatDateTime, formatServiceName, formatStatusLabel } from '../utils/formatters'

export function Timeline({ events }) {
  const transitionEvents = useMemo(() => {
    const sorted = events
      .slice()
      .sort((a, b) => new Date(a.checked_at) - new Date(b.checked_at))

    const lastStatusByService = new Map()
    const changes = []

    for (const event of sorted) {
      const previous = lastStatusByService.get(event.service)
      if (previous !== event.status) {
        changes.push(event)
        lastStatusByService.set(event.service, event.status)
      }
    }

    return changes.reverse().slice(0, 30)
  }, [events])

  return (
    <section className="rounded-xl border border-[#2a4570] bg-[#0b2647] p-6 shadow-[0_10px_30px_rgba(2,18,36,0.45)]">
      <h2 className="mb-4 text-lg font-semibold text-slate-100">Timeline</h2>
      {transitionEvents.length === 0 ? (
        <p className="text-sm text-slate-300">No status transitions yet.</p>
      ) : (
        <ul className="space-y-2">
          {transitionEvents.map((event, index) => (
            <li key={`${event.service}-${event.checked_at}-${index}`} className="text-sm text-slate-200">
              {formatDateTime(event.checked_at)} {formatServiceName(event.service)} changed to{' '}
              {formatStatusLabel(event.status)}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
