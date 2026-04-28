function isProblemState(status) {
  return status === 'outage' || status === 'degraded'
}

export function deriveIncidentHistory(historyItems) {
  const grouped = new Map()

  historyItems
    .slice()
    .sort((a, b) => new Date(a.checked_at) - new Date(b.checked_at))
    .forEach((event) => {
      const key = event.service
      if (!grouped.has(key)) grouped.set(key, [])
      grouped.get(key).push(event)
    })

  const incidents = []

  grouped.forEach((events, serviceName) => {
    let openIncident = null
    for (const event of events) {
      if (isProblemState(event.status)) {
        if (!openIncident) {
          openIncident = {
            start_time: event.checked_at,
            end_time: null,
            affected_services: [serviceName],
          }
        }
      } else if (openIncident) {
        incidents.push({ ...openIncident, end_time: event.checked_at })
        openIncident = null
      }
    }
    if (openIncident) {
      incidents.push(openIncident)
    }
  })

  return incidents.sort((a, b) => new Date(b.start_time) - new Date(a.start_time))
}
