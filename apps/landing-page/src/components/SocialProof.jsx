const stats = [
  { value: '10,000+', label: 'Teams worldwide' },
  { value: '50M+', label: 'Tasks automated' },
  { value: '99.9%', label: 'Uptime SLA' },
  { value: '4.9/5', label: 'Customer rating' },
]

const logos = ['Acme Corp', 'Globex', 'Initech', 'Umbrella', 'Stark Industries']

export default function SocialProof() {
  return (
    <section className="bg-base-surface flex flex-col items-center gap-12 w-full px-6 lg:px-16 py-20">
      {/* Stats */}
      <div className="flex flex-wrap justify-between items-center w-full gap-8">
        {stats.map((stat) => (
          <div key={stat.label} className="flex flex-col items-center gap-2">
            <span className="text-3xl md:text-[32px] font-semibold text-white tracking-tight">
              {stat.value}
            </span>
            <span className="text-sm font-medium text-text-muted leading-normal">
              {stat.label}
            </span>
          </div>
        ))}
      </div>

      {/* Divider */}
      <div className="w-full h-px bg-base-border" />

      {/* Trusted By */}
      <div className="flex flex-col items-center gap-8 w-full">
        <span className="text-sm font-medium text-text-muted">
          Trusted by teams at
        </span>
        <div className="flex flex-wrap justify-center items-center gap-10 md:gap-16 w-full text-lg font-semibold text-text-muted">
          {logos.map((logo) => (
            <span key={logo} className="opacity-60">
              {logo}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
