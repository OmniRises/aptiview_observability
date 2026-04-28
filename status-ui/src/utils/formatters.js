export function formatDateTime(value) {
  if (!value) return 'N/A'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'N/A'
  return date.toLocaleString()
}

export function formatStatusLabel(status) {
  if (!status) return 'Unknown'
  return status.charAt(0).toUpperCase() + status.slice(1)
}

export function statusBadge(status) {
  if (status === 'outage') {
    return {
      dot: '🔴',
      label: 'Major Outage',
      color: 'border-red-400/50 bg-red-500/10 text-red-100',
    }
  }
  if (status === 'degraded') {
    return {
      dot: '🟡',
      label: 'Degraded Performance',
      color: 'border-amber-400/50 bg-amber-500/10 text-amber-100',
    }
  }
  return {
    dot: '🟢',
    label: 'All Systems Operational',
    color: 'border-emerald-400/50 bg-emerald-500/10 text-emerald-100',
  }
}
