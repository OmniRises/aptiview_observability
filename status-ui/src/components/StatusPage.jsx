import { useEffect, useMemo, useState } from 'react'

import logo from '../assets/aptiview-logo.png'
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
      <header className="group flex items-center justify-between border-b border-white/10 pb-5 mb-8 transition-all duration-500 hover:border-white/20">
        <div className="flex items-center gap-4">
          <div className="bg-white/95 p-2 rounded-xl shadow-2xl transition-all duration-500 group-hover:scale-110 group-hover:rotate-1">
            <img
              src={logo}
              alt="Aptiview Logo"
              className="h-8 w-auto"
              onError={(e) => e.target.style.display = 'none'}
            />
          </div>
          <div className="h-8 w-px bg-white/20 self-center" />
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-cyan-400 group-hover:text-cyan-300 transition-colors">Aptiview Status</p>
            <h1 className="text-2xl font-bold text-white tracking-tight group-hover:translate-x-1 transition-transform duration-500">Live platform health</h1>
          </div>
        </div>
        <div className="text-right hidden md:block">
          <p className="text-sm font-bold text-slate-400 group-hover:text-slate-200 transition-colors">Status and incident communication</p>
          <div className="mt-1.5 flex items-center justify-end gap-2">
            <div className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></span>
            </div>
            <span className="text-[11px] font-bold uppercase tracking-[0.2em] text-emerald-400">Live Monitoring</span>
          </div>
        </div>
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
