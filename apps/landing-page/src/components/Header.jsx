export default function Header() {
  return (
    <header className="flex items-center justify-between w-full h-20 px-8 lg:px-16">
      <span className="text-2xl font-semibold text-white tracking-tight">
        NeuralFlow
      </span>

      <nav className="hidden md:flex items-center gap-8 text-[15px] font-medium text-text-secondary">
        <a href="#" className="hover:text-white transition-colors">Products</a>
        <a href="#" className="hover:text-white transition-colors">Features</a>
        <a href="#" className="hover:text-white transition-colors">Pricing</a>
        <a href="#" className="hover:text-white transition-colors">About</a>
      </nav>

      <button className="bg-cta-primary rounded-full px-6 py-3 text-sm font-medium text-white transition-all hover:brightness-110">
        Get Started
      </button>
    </header>
  )
}
