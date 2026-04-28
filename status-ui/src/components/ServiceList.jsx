import { ServiceRow } from './ServiceRow'

export function ServiceList({ services }) {
  return (
    <section className="rounded-xl border border-[#2a4570] bg-[#0b2647] p-6 shadow-[0_10px_30px_rgba(2,18,36,0.45)]">
      <h2 className="mb-4 text-lg font-semibold text-slate-100">System Status</h2>
      <ul className="space-y-3">
        {services.map((service) => (
          <ServiceRow key={service.name} service={service} />
        ))}
      </ul>
    </section>
  )
}
