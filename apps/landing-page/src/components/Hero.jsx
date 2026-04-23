import { ButtonPrimary, ButtonGhost } from './Button'

export default function Hero() {
  return (
    <section className="aurora-hero flex flex-col items-center justify-center gap-8 w-full min-h-[800px] px-6 lg:px-16 py-28">
      {/* Badge */}
      <div className="flex items-center gap-2 bg-glass-fill-strong border border-glass-border rounded-full px-4 py-2">
        <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
        <span className="text-xs font-semibold text-text-secondary tracking-[0.04em]">
          Now with GPT-5 Integration
        </span>
      </div>

      {/* Hero Content */}
      <div className="flex flex-col items-center gap-6 text-center">
        <h1 className="text-5xl md:text-6xl lg:text-[72px] font-bold text-white tracking-hero leading-[1.05]">
          Supercharge Your<br />Workflow with AI
        </h1>
        <p className="text-lg md:text-xl text-text-secondary leading-relaxed max-w-[602px]">
          The intelligent productivity platform that learns how you work,
          automates repetitive tasks, and helps your team ship 10x faster.
        </p>
      </div>

      {/* CTA Row */}
      <div className="flex flex-col sm:flex-row items-center gap-4">
        <ButtonPrimary>Get Started Free</ButtonPrimary>
        <ButtonGhost>Watch Demo</ButtonGhost>
      </div>
    </section>
  )
}
