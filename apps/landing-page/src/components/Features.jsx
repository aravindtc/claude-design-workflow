const cards = [
  {
    title: 'AI Task Automation',
    description:
      'Let AI handle repetitive workflows. Create intelligent automations that learn from your patterns and execute tasks with precision.',
    gradient: 'from-accent-violet to-accent-blue',
  },
  {
    title: 'Smart Scheduling',
    description:
      'AI-powered calendar that optimizes your day. Never miss a deadline with predictive scheduling.',
    gradient: 'from-accent-blue to-accent-cyan',
  },
  {
    title: 'Real-time Analytics',
    description:
      "Live dashboards that surface actionable insights from your team's productivity data.",
    gradient: 'from-accent-cyan to-accent-green',
  },
  {
    title: 'Seamless Integrations',
    description:
      'Connect with 200+ tools your team already uses. Slack, GitHub, Notion, and more.',
    gradient: 'from-accent-pink to-accent-violet',
  },
  {
    title: 'Team Collaboration',
    description:
      'Shared workspaces with AI-assisted project tracking, comments, and progress reports.',
    gradient: 'from-accent-orange to-accent-red',
  },
]

function FeatureCard({ title, description, gradient }) {
  return (
    <div className="bg-glass-fill border border-glass-border rounded-4xl p-8 shadow-subtle flex flex-col gap-5">
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${gradient}`} />
      <h3 className="text-2xl font-semibold text-white tracking-tight">{title}</h3>
      <p className="text-base text-text-secondary leading-normal">{description}</p>
    </div>
  )
}

export default function Features() {
  return (
    <section className="flex flex-col items-center gap-12 w-full px-6 lg:px-16 py-20">
      {/* Section Header */}
      <div className="flex flex-col items-center gap-4 text-center">
        <span className="text-xs font-semibold text-accent-violet tracking-[0.04em]">
          FEATURES
        </span>
        <h2 className="text-3xl md:text-4xl lg:text-[48px] font-bold text-white tracking-h2 leading-tight">
          Everything you need to ship faster
        </h2>
        <p className="text-lg md:text-xl text-text-muted leading-relaxed">
          Powerful tools designed to help teams collaborate, automate, and deliver.
        </p>
      </div>

      {/* Bento Grid */}
      <div className="flex flex-col gap-6 w-full max-w-[1312px]">
        {/* Row 1 — two cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {cards.slice(0, 2).map((card) => (
            <div key={card.title} className="min-h-[340px]">
              <FeatureCard {...card} />
            </div>
          ))}
        </div>
        {/* Row 2 — three cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {cards.slice(2).map((card) => (
            <div key={card.title} className="min-h-[300px]">
              <FeatureCard {...card} />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
