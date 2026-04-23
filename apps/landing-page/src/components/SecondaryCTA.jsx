import { ButtonPrimary } from './Button'

export default function SecondaryCTA() {
  return (
    <section className="aurora-cta flex flex-col items-center justify-center gap-8 w-full px-6 lg:px-16 py-28">
      <div className="flex flex-col items-center gap-6 text-center">
        <h2 className="text-3xl md:text-4xl lg:text-[48px] font-bold text-white tracking-h2 leading-tight">
          Ready to transform<br />your productivity?
        </h2>
        <p className="text-lg md:text-xl text-text-secondary leading-relaxed">
          Join 10,000+ teams already using NeuralFlow to work smarter.
        </p>
      </div>

      <ButtonPrimary size="lg">Start Free Trial</ButtonPrimary>

      <span className="text-sm font-medium text-text-muted">
        No credit card required
      </span>
    </section>
  )
}
