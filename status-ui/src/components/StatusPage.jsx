import { useEffect, useMemo, useState } from 'react'

import { ApiError, getHistory, getStatus } from '../api/statusApi'
import { deriveIncidentHistory } from '../utils/incidentUtils'
import { IncidentCard } from './IncidentCard'
import { IncidentHistory } from './IncidentHistory'
import { ServiceList } from './ServiceList'
import { StatusBanner } from './StatusBanner'
import { Timeline } from './Timeline'
import { UptimeStrip } from './UptimeStrip'

export function StatusPage() {
  const [statusData, setStatusData] = useState(null)
  const [historyData, setHistoryData] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [rateLimited, setRateLimited] = useState(false)
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null)

  useEffect(() => {
    let cancelled = false

    const loadStatus = async () => {
      try {
        const status = await getStatus()
        if (cancelled) return
        setStatusData(status)
        setLastUpdatedAt(new Date().toISOString())
        setHasError(false)
      } catch (error) {
        if (!cancelled) {
          if (error instanceof ApiError && error.status === 429) {
            setRateLimited(true)
            setHasError(false)
          } else {
            setHasError(true)
            setRateLimited(false)
          }
        }
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    loadStatus()
    const intervalId = setInterval(loadStatus, 30000)

    return () => {
      cancelled = true
      clearInterval(intervalId)
    }
  }, [])

  useEffect(() => {
    let cancelled = false

    const loadHistory = async () => {
      try {
        const history = await getHistory()
        if (cancelled) return
        setHistoryData(history.history || [])
      } catch (error) {
        if (!cancelled) setHistoryData([])
      }
    }

    loadHistory()

    return () => {
      cancelled = true
    }
  }, [])

  const incidents = useMemo(() => deriveIncidentHistory(historyData), [historyData])

  if (isLoading) {
    return <main className="mx-auto max-w-6xl p-6 text-slate-300">Loading status...</main>
  }

  if (rateLimited) {
    return (
      <main className="mx-auto max-w-6xl p-6 text-amber-200">
        Rate limit reached. Please wait a minute and refresh.
      </main>
    )
  }

  if (hasError || !statusData) {
    return <main className="mx-auto max-w-6xl p-6 text-red-300">Unable to load status</main>
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <header className="flex items-center justify-between border-b border-slate-700 pb-4">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-cyan-300">Aptiview Status</p>
          <h1 className="text-xl font-semibold text-slate-100">Live platform health</h1>
        </div>
        <p className="text-sm text-slate-300">Status and incident communication</p>
      </header>
      <StatusBanner overallStatus={statusData.overall_status} lastUpdatedAt={lastUpdatedAt} />
      <UptimeStrip events={historyData} />
      <section className="grid gap-6 lg:grid-cols-2">
        <ServiceList services={statusData.services || []} />
        <div className="space-y-6">
          <IncidentCard incident={statusData.incident} services={statusData.services || []} />
          <IncidentHistory incidents={incidents} />
        </div>
      </section>
      <Timeline events={historyData} />
    </main>
  )
}
